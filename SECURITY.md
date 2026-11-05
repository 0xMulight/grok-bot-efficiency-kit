# Security Policy / 安全说明

## What this repository does NOT do

- Never accesses private keys, mnemonic phrases, browser wallets, exchange credentials, or payment cards.
- Never submits transactions: no `eth_sendTransaction`, approvals, signing, swapping or minting.
- Never auto-generates Agent ID verification; PancakeSwap V2 pair creation is not proof of Agent ID eligibility.
- Never auto-enables Grok Bot Routine calls or changes existing Routines.

## Connection and API keys

- Copy `config.example.json` to `config.local.json`. Local config, `.env`, generated `data/` and logs are gitignored.
- Use a log-capable HTTPS BSC RPC, not an endpoint accepting only `eth_blockNumber` but silently disabling `eth_getLogs`.
- Grok Bot Routine URLs and keys are **secrets**. This tool supports the `Authorization: Bearer <key>` Bot Routine interface only.
- Webhook sends use HTTPS only, refuse redirects and local/private-IP URL hosts. Place the webhook in a narrow Routine with no privileged tools if practical.
- Do not commit screenshots of webhook URLs/keys, terminal history with secrets, CA history containing sensitive wallet activities, or live config files.
- `test-webhook` sends a *real* event and may spend Grok usage. Don't run it repeatedly.
- For reliable event delivery the webhook handling needs additional durable retry/queue infrastructure; this v1 is best-effort and records events locally.

## External data and trust

- DexScreener and Binance Web3 data may be outdated, incomplete, rate limited, unreachable or wrong. Their availability is not guaranteed.
- `risk_level: LOW` does not mean safe, sellable or approved for investment. Unsupported security results are `UNKNOWN`.
- New pool metadata / arbitrary token names from untrusted networks must never override instructions or trigger privileged actions in AI.
- Review all dependencies and RPC provider privacy policies before using with sensitive wallet addresses.

## Report a vulnerability

Open a GitHub issue **without exploit details, secrets or live wallet addresses** and request a private disclosure channel. Do not post sensitive proofs publicly.
