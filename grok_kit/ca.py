"""Read-only CA intelligence from DexScreener and Binance public audit API."""
from __future__ import annotations
import uuid
import json
from .core import KitError, assert_address, get_json, post_json


def _float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def inspect_ca(address: str, *, market_get=get_json, audit_post=post_json) -> dict:
    address=assert_address(address)
    result={'chain_id':56,'ca':address,'market':{},'contract_audit':{},'warnings':[],
            'read_only':True, 'not_investment_advice':True}
    try:
        market=market_get('https://api.dexscreener.com/latest/dex/tokens/'+address)
        pairs=[p for p in (market.get('pairs') or []) if p.get('chainId','').lower()=='bsc' and
               (p.get('baseToken') or {}).get('address','').lower()==address]
        pairs.sort(key=lambda p:_float((p.get('liquidity') or {}).get('usd')) or 0,reverse=True)
        if pairs:
            p=pairs[0]; result['market']={
                'source':'DexScreener','dex':p.get('dexId'),'pair_address':p.get('pairAddress'),
                'symbol':(p.get('baseToken') or {}).get('symbol'),
                'price_usd':p.get('priceUsd'),'liquidity_usd':(p.get('liquidity') or {}).get('usd'),
                'volume_24h_usd':(p.get('volume') or {}).get('h24'),
                'price_change_24h_pct':(p.get('priceChange') or {}).get('h24')}
        else:
            result['warnings'].append('No BSC pair with CA as base token in DexScreener response')
    except (KitError, TypeError, AttributeError, ValueError) as e:
        result['warnings'].append('Market API unavailable: '+str(e)[:140])
    try:
        response=audit_post('https://web3.binance.com/bapi/defi/v1/public/wallet-direct/security/token/audit',
            {'binanceChainId':'56','contractAddress':address,'requestId':str(uuid.uuid4())},
            headers={'source':'agent','User-Agent':'binance-web3/1.4 (Skill)'})
        raw=json.loads(response['body'])
        d=raw.get('data') or {}
        if raw.get('success') is True and d.get('hasResult') and d.get('isSupported'):
            x=d.get('extraInfo') or {}
            result['contract_audit']={
                'source':'Binance Web3 public token security audit','risk_level':d.get('riskLevelEnum'),
                'risk_number':d.get('riskLevel'),'buy_tax':x.get('buyTax'),
                'sell_tax':x.get('sellTax'),'verified':x.get('isVerified'),
                'findings':[{'category':r.get('name'), 'details':[{'title':z.get('title'),
                  'is_hit':z.get('isHit'),'risk_type':z.get('riskType')} for z in r.get('details',[])][:20]}
                  for r in d.get('riskItems',[])][:20]}
        else:
            result['warnings'].append('Binance audit has no supported result; risk UNKNOWN')
    except (KitError,TypeError,ValueError,AttributeError,KeyError) as e:
        result['warnings'].append('Binance audit unavailable: '+str(e)[:140])
    if not result['contract_audit']:
        result['contract_audit']={'risk_level':'UNKNOWN'}
    result['note']='A low risk flag does not establish safety, liquidity or sellability. No trading is performed.'
    return result
