# Contributing

Thanks for helping improve the Grok Bot Efficiency Kit.

1. Preserve the read-only / no-private-key / explicit-webhook-opt-in defaults.
2. Do not add paid token auto-buy, auto-mint, signing or approval capabilities.
3. Changes affecting external APIs must include fixture-driven unit tests and clear offline failure behavior.
4. Run `python -m unittest discover -s tests -v` and `python -m grok_kit doctor` before proposing changes.
5. Never commit `config.local.json`, `.env`, webhook key, wallet keys or runtime `data/`.
6. Clearly document which DEXs and event types are actually covered.

Submit PRs with a brief summary, manual test instructions and relevant docs update.
