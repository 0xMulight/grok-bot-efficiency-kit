"""BSC PancakeSwap V2 PairCreated event polling; read-only by default.

This is not an Agent ID detector and does not cover all DEXs.
Requires an RPC provider with eth_getLogs enabled.
"""
from __future__ import annotations
import time
import datetime as dt
from .core import KitError, atomic_write_json, append_jsonl, assert_bsc, configured_rpc, data_dir, read_json
from .webhook import send_bot_webhook

FACTORY='0xca143ce32fe78f1f7019d7d551a6402fc5350c73'
WBNB='0xbb4cdb9cb d36b01bd1cbaebf2de08d9173bc095c'.replace(' ','')
PAIR_CREATED_TOPIC='0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9'


def parse_pair_log(record: dict) -> dict:
    topics = record.get('topics') or []
    if len(topics) < 3 or topics[0].lower()!=PAIR_CREATED_TOPIC:
        raise KitError('Not a PairCreated log')
    token0='0x'+topics[1][-40:].lower()
    token1='0x'+topics[2][-40:].lower()
    data=record.get('data', '0x')
    if len(data)<66:
        raise KitError('PairCreated log missing pair address')
    pair='0x'+data[2:66][-40:].lower()
    return {'event_type':'bsc_new_wbnb_pair', 'chain_id':56,'token0':token0,'token1':token1, 'pair':pair,
            'candidate_token': token1 if token0==WBNB else token0,
            'block_number':int(record['blockNumber'],16),
            'transaction_hash':record['transactionHash'].lower(),
            'log_index':int(record['logIndex'],16),
            'classification':'NEW_PANCAKESWAP_V2_WBNB_PAIR_NOT_AGENT_ID_VERIFIED'}


def _config_settings(config: dict) -> tuple[int,int,int,int]:
    m=config.get('monitor', {})
    confirmation=int(m.get('confirmations', 3)); batch=int(m.get('batch_blocks', 50))
    delay=int(m.get('poll_seconds', 15)); limit=int(m.get('max_webhooks_per_cycle', 2))
    if confirmation<1 or not (1<=batch<=500) or not (3<=delay<=3600) or not (0<=limit<=20):
        raise KitError('Invalid monitor configuration; see README')
    return confirmation,batch,delay,limit


def scan_once(config: dict, *, send: bool=False, rpc=None) -> dict:
    confirmation,batch,_,limit=_config_settings(config)
    rpc=rpc or configured_rpc(config)
    assert_bsc(rpc)
    data=data_dir(config)
    state_path=data / 'monitor-state.json'
    state=read_json(state_path, default=None)
    head=int(rpc.call('eth_blockNumber'),16)
    safe_head=head-confirmation
    if safe_head<0:
        raise KitError('No confirmed blocks available')
    if state is None:
        # First run establishes a live baseline. Never trigger historical events by surprise.
        atomic_write_json(state_path, {'last_complete_block':safe_head})
        return {'status':'initialized','last_complete_block':safe_head, 'events':0,'note':'First run establishes baseline only'}
    prev=state['last_complete_block']
    if safe_head<=prev:
        return {'status':'up_to_date','last_complete_block':prev,'events':0}
    start=prev+1
    end=min(safe_head, start+batch-1)
    logs=rpc.call('eth_getLogs',[{'address':FACTORY,'fromBlock':hex(start),'toBlock':hex(end),'topics':[PAIR_CREATED_TOPIC]}])
    if not isinstance(logs,list):
        raise KitError('eth_getLogs returned non-list data')
    # Public BSC endpoints can silently return empty logs; provider capability is required.
    # No way to prove completeness without a known positive historical test; see doctor-logs.
    # Persist outbound webhook budget independently from on-chain cursor.
    # A noisy chain should not consume a user's entire weekly Bot allowance.
    wb_path=data / 'webhook-budget.json'
    wb=read_json(wb_path, default={'hour_started':time.time(),'sent_this_hour':0,'last_sent_at':0})
    now=time.time()
    if now-float(wb.get('hour_started',0)) >= 3600:
        wb={'hour_started':now,'sent_this_hour':0,'last_sent_at':0}
    hourly_limit=int(config.get('webhook',{}).get('max_per_hour',12))
    min_gap=int(config.get('webhook',{}).get('min_gap_seconds',300))
    if not (0<=hourly_limit<=60 and 0<=min_gap<=3600):
        raise KitError('Webhook budget must have max_per_hour 0..60 and min_gap_seconds 0..3600')
    events=[]; accepted=0; failures=[]; capped=0
    for raw in sorted(logs,key=lambda r:(int(r['blockNumber'],16),int(r['logIndex'],16))):
        try:
            event=parse_pair_log(raw)
            if WBNB not in {event['token0'],event['token1']}:
                continue
            append_jsonl(data/'events.jsonl',event)
            events.append(event)
            if send:
                now=time.time()
                may_send=(accepted < limit and int(wb.get('sent_this_hour',0)) < hourly_limit
                          and now-float(wb.get('last_sent_at',0))>=min_gap)
                if may_send:
                    try:
                        send_bot_webhook(config,event)
                        accepted+=1
                        wb['sent_this_hour']=int(wb.get('sent_this_hour',0))+1
                        wb['last_sent_at']=now
                        atomic_write_json(wb_path,wb)
                    except KitError as e:
                        failures.append(str(e))
                else:
                    capped+=1
        except (ValueError,KeyError,IndexError,KitError) as e:
            failures.append('Bad event ignored: '+str(e)[:150])
    atomic_write_json(state_path, {'last_complete_block':end})
    result={'status':'scanned','range':[start,end],'events':len(events),'webhooks_accepted':accepted,
            'webhooks_skipped':capped if send else 0}
    if failures:
        result['warnings']=failures[:5]
    if send and capped:
        result['note']='Webhook per-cycle/cooldown/hourly budget applied; all events saved locally; surplus not delivered'
    return result


def continuous(config:dict, *,send:bool=False):
    _,_,delay,_=_config_settings(config)
    while True:
        try:
            result=scan_once(config,send=send)
            print(result,flush=True)
        except (KitError, OSError, ValueError) as e:
            print('Monitor error: '+str(e),flush=True)
        time.sleep(delay)


def doctor_logs(config:dict, rpc=None) -> dict:
    """Verify RPC supports eth_getLogs call; an empty result is *inconclusive*."""
    rpc=rpc or configured_rpc(config)
    assert_bsc(rpc)
    head=int(rpc.call('eth_blockNumber'),16)
    result=rpc.call('eth_getLogs',[{'address':FACTORY, 'topics':[PAIR_CREATED_TOPIC],
                                    'fromBlock':hex(max(0,head-100)), 'toBlock':hex(max(0,head-1))}])
    if not isinstance(result,list):
        raise KitError('eth_getLogs unsupported or malformed response')
    return {'rpc_call_succeeded':True,'logs_found':len(result),
            'warning':'Empty response does NOT prove eth_getLogs works; some public nodes silently return []' if not result else None}
