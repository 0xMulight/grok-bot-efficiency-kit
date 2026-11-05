"""Shared small, read-only helpers. Python 3.10+ standard library only."""
from __future__ import annotations
import json
import os
import pathlib
import ipaddress
import socket
import urllib.parse
import urllib.request
import urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent

class KitError(Exception):
    """Safe user-facing error."""


def load_config(path: str | None = None) -> dict:
    p = pathlib.Path(path) if path else (ROOT / 'config.local.json' if (ROOT / 'config.local.json').exists() else ROOT / 'config.example.json')
    try:
        obj = json.loads(p.read_text(encoding='utf-8'))
    except (ValueError, OSError) as e:
        raise KitError(f'Cannot load config {p}: {e}') from e
    if not isinstance(obj, dict):
        raise KitError('Config must be a JSON object')
    return obj


def data_dir(config: dict) -> pathlib.Path:
    raw = config.get('data_dir', 'data')
    p = pathlib.Path(raw)
    p = p if p.is_absolute() else ROOT / p
    p.mkdir(parents=True, exist_ok=True)
    return p


def read_json(path: pathlib.Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def atomic_write_json(path: pathlib.Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)


def append_jsonl(path: pathlib.Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n')


def assert_address(address: str) -> str:
    if not isinstance(address, str) or len(address) != 42 or not address.startswith('0x'):
        raise KitError('CA/address must be 0x followed by 40 hexadecimal digits')
    try:
        int(address[2:], 16)
    except ValueError as e:
        raise KitError('Invalid hexadecimal address') from e
    return address.lower()


def validate_rpc_url(url: str) -> str:
    p = urllib.parse.urlsplit(url)
    if p.scheme != 'https' or not p.hostname or p.username or p.password:
        raise KitError('RPC URL must be HTTPS without embedded credentials')
    return url


def validate_webhook_url(url: str) -> str:
    p = urllib.parse.urlsplit(url)
    if p.scheme != 'https' or not p.hostname or p.username or p.password or p.fragment:
        raise KitError('Webhook must use an HTTPS URL without embedded credentials or a fragment')
    host = p.hostname.lower().rstrip('.')
    if host in {'localhost', 'localhost.localdomain'} or host.endswith(('.local', '.internal')):
        raise KitError('Local/internal webhook host refused')
    try:
        ip = ipaddress.ip_address(host)
        if not ip.is_global:
            raise KitError('Private, reserved or loopback webhook IP refused')
    except ValueError:
        pass
    return url


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise KitError('HTTP redirect refused (protects webhook bearer key)')


def post_json(url: str, payload: dict, headers: dict | None = None, timeout: int = 15, no_redirect: bool = False) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    hdr = {'Content-Type': 'application/json', 'Accept': 'application/json', 'User-Agent': 'Mulight-Grok-Efficiency-Kit/1.0'}
    hdr.update(headers or {})
    request = urllib.request.Request(url, data=data, headers=hdr, method='POST')
    handler = urllib.request.build_opener(_NoRedirect) if no_redirect else urllib.request.build_opener()
    try:
        with handler.open(request, timeout=timeout) as response:
            body = response.read(2_000_000)
            return {'http_status': response.status, 'body': body.decode('utf-8', errors='replace')}
    except urllib.error.HTTPError as e:
        raise KitError(f'HTTP {e.code} from remote service') from e
    except urllib.error.URLError as e:
        raise KitError('Remote connection failed; check network, URL, RPC provider or key') from e


def get_json(url: str, timeout: int = 15) -> dict:
    req = urllib.request.Request(url, headers={'Accept': 'application/json', 'User-Agent': 'Mulight-Grok-Efficiency-Kit/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read(2_000_000).decode('utf-8'))
    except (OSError, ValueError) as e:
        raise KitError(f'HTTP GET failed or invalid JSON: {type(e).__name__}') from e


class Rpc:
    def __init__(self, url: str):
        self.url = validate_rpc_url(url)

    def call(self, method: str, params: list | None = None):
        answer = post_json(self.url, {'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params or []})
        try:
            j = json.loads(answer['body'])
        except ValueError as e:
            raise KitError('RPC returned invalid JSON') from e
        if 'error' in j:
            err = j['error']
            raise KitError(f'RPC {method} failed: {err.get("code", "?")} {str(err.get("message", ""))[:180]}')
        if 'result' not in j:
            raise KitError(f'RPC {method} returned no result')
        return j['result']


def configured_rpc(config: dict) -> Rpc:
    url = os.getenv('BSC_RPC_URL') or config.get('bsc_rpc_url', '')
    if not url or 'YOUR_' in url or 'example' in url.lower():
        raise KitError('Set BSC_RPC_URL or bsc_rpc_url in config.local.json (eth_getLogs-enabled provider)')
    return Rpc(url)


def assert_bsc(rpc: Rpc) -> None:
    chain = int(rpc.call('eth_chainId'), 16)
    if chain != 56:
        raise KitError(f'Expected BSC chainId 56; RPC returned {chain}')
