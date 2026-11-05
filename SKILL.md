---
name: grok-bot-efficiency-kit
description: BSC new WBNB pair monitoring, read-only token CA inspection, and Grok Bot Routine call audit with opt-in Bearer webhooks. No wallet, no trades.
license: MIT
metadata:
  author: 0xMulight
  version: "1.0.0"
---

# Grok Bot Efficiency Kit / Grok Bot 省额度工具包

Use this skill when the user wants to reduce repetitive Grok Bot Routine calls, analyze BSC CA, set up read-only BSC new-pair monitoring, or convert repetitive scheduled checks into narrowly filtered event-triggered Routines.

## First read

- This repository contains **one skill with three independent modules**; use only the requested module.
- Never assume GitHub code can be installed inside Grok Bot's sandbox or can run on a remote computer. These scripts execute in a trusted environment with Python 3.10+, such as the user's own PC. If that environment is unavailable, provide commands and ask the user to run them locally.
- BSC watcher detects **PancakeSwap V2 WBNB new pairs only**. It does not automatically identify Agent ID projects, monitor all DEXs, or execute Mint/transactions. Agent ID verification needs an additional authoritative source and review.
- BNB Chain public dataseed RPC may disable or silently empty `eth_getLogs`; require a provider explicitly enabling logs. Verify reliability before deployment.
- **Always read-only by default.** Never request wallet seed, private key, exchange password, API secret, or browser cookies. Never sign, mint, swap, grant approval or modify a live Routine without explicit informed confirmation.
- **Webhook sending is opt-in** and a request can spend Grok Bot usage. The user owns their webhook URL/key; never include them in output, repo, screenshots, logs, or chats.
- **Bot webhook vs Grok automations**: this skill implements the Bot Routine `Authorization: Bearer <key>` interface from the official Grok Bot documentation. It does NOT implement Grok automations' HMAC signature trigger.

## Module 1: BSC event watcher / Webhook

1. Ask whether the user has an HTTPS BSC RPC provider that supports `eth_getLogs`. Use `config.local.json` or `BSC_RPC_URL` only, never commit credentials.
2. Run `python -m grok_kit doctor` and `python -m grok_kit doctor-logs`. Note: an empty log check is inconclusive.
3. Run `python -m grok_kit watch --once` to initialize the current safe-block cursor. Run a second time after new blocks to observe events; `data/events.jsonl` stores events locally.
4. Only after user explicitly connects an individual Grok Bot Routine webhook using its URL and Bearer key, test via `python -m grok_kit test-webhook`, warn this creates a real run.
5. Run `python -m grok_kit watch --send-webhook` for continuous monitoring with the configured alert cap; without `--send-webhook`, only local logging is performed.
6. Check the Bot chat. HTTP 200 means the event was accepted, not that the Bot finished the work.

## Module 2: CA read-only risk inspection

Use `python -m grok_kit ca 0xCONTRACT`. This calls DexScreener for market data and Binance Web3's public token audit endpoint. Report market liquidity/price/volume with source, detected risks, and missing/unsupported results as `UNKNOWN`. This never certifies token safety. No transaction.

## Module 3: Routine usage audit

Use `python -m grok_kit audit examples/routines.example.json`. User must input each Routine name, enabled state, interval, active hours/day, and estimated meaningful events/day. Output estimates **number of calls**, not tokens or money saved. Never claim this tool can inspect Grok account billing, connected app permissions or routines automatically. Do not edit any Routine automatically.

## Suggested Bot prompt

> 请检查我提供的Routine清单，找出频繁轮询但很少产生有效事件的任务。计算原来的每周触发次数，再根据我给出的有效事件次数估算改成Webhook后可能减少多少次调用。需要读取链上数据时先调用本地只读脚本；发现新币仅生成待核对报告，绝不自动交易。未经我确认不要暂停、创建、编辑或删除Routine，不要把Webhook密钥输出到聊天中。报告中列出假设、数据来源、修改方案、风险和人工确认点。

## Relevant documentation

- [README](README.md)
- [Windows/installation](docs/quick-start.md)
- [Webhook security and setup](docs/grok-webhook.md)
- [Architecture and boundaries](docs/architecture.md)
- [Security policy](SECURITY.md)
- Official Grok Bot routines: https://docs.x.ai/grok-bot/skills-routines-and-automations
- BNB Chain RPC: https://docs.bnbchain.org/bnb-smart-chain/developers/json_rpc/json-rpc-endpoint/
