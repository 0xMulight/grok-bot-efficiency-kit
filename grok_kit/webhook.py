"""Grok Bot Routine bearer webhook; not Grok automations HMAC webhooks."""
import os
from .core import KitError, post_json, validate_webhook_url


def send_bot_webhook(config: dict, event: dict) -> dict:
    wcfg = config.get('webhook', {})
    url = os.getenv('GROK_BOT_WEBHOOK_URL') or wcfg.get('url', '')
    key = os.getenv('GROK_BOT_WEBHOOK_KEY') or wcfg.get('key', '')
    if not url or not key or 'REPLACE_ME' in key or 'example' in url:
        raise KitError('Set GROK_BOT_WEBHOOK_URL and GROK_BOT_WEBHOOK_KEY (from Bot Routine > Webhook)')
    validate_webhook_url(url)
    # Deliberately keep the data small; no arbitrary contract metadata or web links.
    if not isinstance(event, dict) or event.get('event_type') not in {'bsc_new_wbnb_pair','bsc_wallet_balance_change','test'}:
        raise KitError('Unrecognized webhook event type')
    payload = {'source': 'grok-bot-efficiency-kit', 'schema_version': 1, 'event': event}
    result = post_json(url, payload, headers={'Authorization': f'Bearer {key}'}, no_redirect=True)
    if result['http_status'] != 200:
        raise KitError(f'Grok Bot webhook did not accept event (HTTP {result["http_status"]})')
    return {'accepted': True, 'http_status': result['http_status'], 'note': 'Accepted is not completed; inspect Bot chat for result'}
