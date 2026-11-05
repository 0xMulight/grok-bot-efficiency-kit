"""Run with python -m grok_kit <command>."""
from __future__ import annotations
import argparse
import json
import sys
import datetime as dt
from .core import KitError, load_config, configured_rpc, assert_bsc, assert_address
from .monitor import scan_once, continuous, doctor_logs
from .ca import inspect_ca
from .audit import audit_file
from .webhook import send_bot_webhook


def main(argv=None)->int:
    parser=argparse.ArgumentParser(prog='python -m grok_kit',description='Mulight Grok Bot Efficiency Kit — three independent read-only tools')
    parser.add_argument('--config', help='Local config JSON (default: config.local.json or example)')
    sub=parser.add_subparsers(dest='cmd',required=True)
    sub.add_parser('doctor',help='Check Python and config, no network or wallet')
    sub.add_parser('doctor-logs',help='Test BSC RPC eth_getLogs provider (network)')
    mon=sub.add_parser('watch',help='Read-only PancakeSwap V2 WBNB pair scanner')
    mon.add_argument('--once',action='store_true',help='One cycle, instead of continuous')
    mon.add_argument('--send-webhook',action='store_true',help='Explicit opt-in to send capped webhook notifications')
    ca=sub.add_parser('ca',help='Public CA market and security check')
    ca.add_argument('contract',help='BSC contract address')
    a=sub.add_parser('audit',help='Calculate estimated Routine call reductions offline')
    a.add_argument('file',help='JSON routines input')
    sub.add_parser('test-webhook',help='Sends ONE test event; may consume one Grok run')
    p=parser.parse_args(argv)
    try:
        config=load_config(p.config)
        if p.cmd=='doctor':
            result={'config':'ok','python':sys.version.split()[0], 'read_only_default':True,
                    'rpc_configured':bool(__import__('os').getenv('BSC_RPC_URL') or config.get('bsc_rpc_url')),
                    'webhook_configured':bool(__import__('os').getenv('GROK_BOT_WEBHOOK_KEY') or config.get('webhook',{}).get('key')),
                    'status':'Ready for offline audit. For BSC logs use an eth_getLogs-enabled paid/private RPC.'}
        elif p.cmd=='doctor-logs':
            result=doctor_logs(config)
        elif p.cmd=='watch':
            if p.once:result=scan_once(config,send=p.send_webhook)
            else:
                continuous(config,send=p.send_webhook)
                return 0
        elif p.cmd=='ca':
            result=inspect_ca(assert_address(p.contract))
        elif p.cmd=='audit':
            result=audit_file(p.file)
        elif p.cmd=='test-webhook':
            result=send_bot_webhook(config,{'event_type':'test', 'message':'Read-only integration test',
                        'time_utc':dt.datetime.now(dt.timezone.utc).isoformat()})
        else:raise KitError('Unsupported command')
        print(json.dumps(result,indent=2,ensure_ascii=False))
        return 0
    except (KitError,KeyboardInterrupt) as e:
        print(f'ERROR: {e}',file=sys.stderr)
        return 1

if __name__=='__main__':
    raise SystemExit(main())
