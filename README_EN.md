# Grok Bot Efficiency Kit

**One reusable skill, three independent Python 3.10+ standard-library tools.** Build BSC read-only event notifications, inspect CA market/security data, and estimate Grok Bot Routine call reductions.

> Community project by 0xMulight. Not affiliated with X, xAI, Binance, PancakeSwap or BNB Chain. Not investment advice. No wallet, transactions or automated trading.

## Usage

```bash
python -m grok_kit doctor
python -m grok_kit audit examples/routines.example.json
python -m grok_kit ca 0x55d398326f99059ff775485246999027b3197955
```

For on-chain monitoring copy `config.example.json` to `config.local.json`, configure an HTTPS BSC RPC supporting `eth_getLogs`, then run:

```bash
python -m grok_kit doctor-logs
python -m grok_kit watch --once
python -m grok_kit watch
```

**Public BSC dataseed RPC endpoints frequently block `eth_getLogs` and may silently return empty arrays.** A paid/private log-capable provider is typically needed. The watcher tracks **PancakeSwap V2 new WBNB pairs**, not Agent ID Mint or every BSC pair.

To use a Grok Bot webhook, create a Bot Routine webhook and keep the POST URL and Bearer key in your **uncommitted** local config. `python -m grok_kit test-webhook` sends one event and consumes a Bot run. `python -m grok_kit watch --send-webhook` explicitly enables capped notifications. This is not the separate Grok Automations HMAC webhook type.

Read [Chinese README](README.md), [Skill](SKILL.md), [Windows installation](docs/quick-start.md), [Security](SECURITY.md), [Architecture](docs/architecture.md).

License: MIT · Author: 0xMulight · Version 1.0.0
