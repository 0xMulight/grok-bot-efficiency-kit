import unittest
from grok_kit.core import assert_address, validate_webhook_url, KitError
from grok_kit.monitor import parse_pair_log, scan_once, FACTORY, WBNB, PAIR_CREATED_TOPIC
from grok_kit.audit import audit_routines
from grok_kit.ca import inspect_ca
from grok_kit.webhook import send_bot_webhook
from unittest.mock import patch
import tempfile, pathlib, json

CA='0x'+'a'*40

def mklog(block='0x7',idx='0x0'):
    tok='0x'+'a'*40
    return {'topics':[PAIR_CREATED_TOPIC,'0x'+'0'*24+WBNB[2:],'0x'+'0'*24+tok[2:]],
            'data':'0x'+'0'*24+'b'*40+'0'*64,'blockNumber':block,
            'transactionHash':'0x'+'c'*64,'logIndex':idx}

class DummyRPC:
    def __init__(self,head=11,logs=None):
        self.head=head;self.logs=logs or [];self.calls=[]
    def call(self,method,params=None):
        self.calls.append(method)
        if method=='eth_chainId':return '0x38'
        if method=='eth_blockNumber':return hex(self.head)
        if method=='eth_getLogs':return self.logs
        raise AssertionError(method)

class CoreTests(unittest.TestCase):
    def test_ca_address_validation(self):
        self.assertEqual(assert_address(CA),CA)
        for address in ['0x0','abc','0x'+'z'*40]:
            with self.assertRaises(KitError):assert_address(address)

    def test_webhook_url_validation(self):
        for url in ['http://example.com','https://localhost/x','https://127.0.0.1/x','https://10.0.0.1/x','https://u:p@example.com/x']:
            with self.assertRaises(KitError):validate_webhook_url(url)
        self.assertEqual(validate_webhook_url('https://hooks.example.com/a'),'https://hooks.example.com/a')

    def test_parse_pair(self):
        p=parse_pair_log(mklog())
        self.assertEqual(p['candidate_token'],CA)
        self.assertEqual(p['pair'],'0x'+'b'*40)
        self.assertEqual(p['block_number'],7)

    def test_monitor_baseline_and_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            config={'data_dir':tmp,'monitor':{'confirmations':3,'batch_blocks':50,'poll_seconds':15}}
            rpc=DummyRPC(head=11)
            result=scan_once(config,rpc=rpc)
            self.assertEqual(result['status'],'initialized')
            self.assertFalse((pathlib.Path(tmp)/'events.jsonl').exists())
            rpc.head=14;rpc.logs=[mklog('0xa')]
            result=scan_once(config,rpc=rpc)
            self.assertEqual(result['events'],1)
            self.assertEqual(result['webhooks_accepted'],0)
            lines=(pathlib.Path(tmp)/'events.jsonl').read_text().strip().splitlines()
            self.assertEqual(len(lines),1)
            self.assertEqual(json.loads(lines[0])['candidate_token'],CA)
            self.assertEqual(json.loads((pathlib.Path(tmp)/'monitor-state.json').read_text())['last_complete_block'],11)

    def test_audit_math(self):
        a=audit_routines({'routines':[{'name':'test','interval_minutes':5,'active_hours_per_day':24,'estimated_events_per_day':6}]})
        self.assertEqual(a['weekly_scheduled_calls'],2016)
        self.assertEqual(a['weekly_estimated_triggered_calls_for_modeled_items'],42)
        self.assertEqual(a['routines'][0]['estimated_calls_avoided_per_week'],1974)

    def test_ca_fallback_and_data(self):
        def market(url):
            return {'pairs':[{'chainId':'bsc','baseToken':{'address':CA,'symbol':'T'},'liquidity':{'usd':2000},'volume':{'h24':30},'priceUsd':'0.1','dexId':'pancakeswap','pairAddress':'0xPAIR'}]}
        def audit(url,payload,headers):
            return {'body':json.dumps({'success':True,'data':{'hasResult':True,'isSupported':True,'riskLevelEnum':'MEDIUM','riskItems':[]}})}
        r=inspect_ca(CA,market_get=market,audit_post=audit)
        self.assertEqual(r['market']['symbol'],'T')
        self.assertEqual(r['contract_audit']['risk_level'],'MEDIUM')
        r=inspect_ca(CA,market_get=lambda x: (_ for _ in ()).throw(KitError('offline')),
                     audit_post=lambda *a,**k:(_ for _ in ()).throw(KitError('offline')))
        self.assertEqual(r['contract_audit']['risk_level'],'UNKNOWN')
        self.assertTrue(r['warnings'])

    @patch('grok_kit.webhook.post_json')
    def test_webhook_bearer_and_test(self,mock_post):
        mock_post.return_value={'http_status':200,'body':'ok'}
        cfg={'webhook':{'url':'https://hooks.grokbot.test/abc','key':'secret'}}
        result=send_bot_webhook(cfg,{'event_type':'test'})
        self.assertTrue(result['accepted'])
        self.assertEqual(mock_post.call_args.kwargs['headers']['Authorization'],'Bearer secret')
        self.assertTrue(mock_post.call_args.kwargs['no_redirect'])

if __name__=='__main__': unittest.main()
