# 架构、覆盖范围与非目标

## 一个Skill，三个独立模块

| 模块 | 入口 | 输入 | 输出 | 依赖 |
|---|---|---|---|---|
| Watcher | `python -m grok_kit watch` | HTTPS BSC RPC (支持`eth_getLogs`) | `data/events.jsonl`、游标；明确允许后可发Bot Webhook | BSC JSON-RPC |
| CA | `python -m grok_kit ca 0x...` | 链56的合约地址 | JSON价格、流动性、审计结果/UNKNOWN | DexScreener与Binance Web3公共API |
| Audit | `python -m grok_kit audit examples/routines.example.json` | 你提供的Routine假设 | 模拟每周触发次数、潜在减少次数 | 无需联网 |

## BSC Watcher

- 主网：chainId 56。开始扫描前调用 `eth_chainId` 校验网络。
- 事件源：PancakeSwap V2 Factory `0xca143ce32fe78f1f7019d7d551a6402fC5350c73` 的 `PairCreated`。
- 过滤条件：配对的一个Token为WBNB (`0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c`)。
- `confirmations` 默认3，`batch_blocks` 默认50；本地游标在成功处理完一块区间后保存。
- 初次启动只写入当前安全块，不补扫旧历史（避免一装就刷屏）。
- 每次有效事件写 `data/events.jsonl`。无法读取事件时会报错，不声称获取了全链信息。
- 可选 `--send-webhook`：向单个Grok Bot Routine发送经过格式化的结构化事件，每轮最多1条，默认每小时最多12条、间隔至少300秒。没有开启就不发。

**这不是：** Agent ID Mint雷达、提前发现所有新项目、对钱包授权/交易风险的全面分析、自动买卖系统。新池可能是普通代币或恶意合约。若希望监控 Agent ID，必须另外接入可验证的 Agent ID 合约标识、平台官方事件、资格/成本来源及安全审计，再另行测试。

### BNB Chain RPC Caveat

BNB Chain 官方声明部分公共RPC禁止 `eth_getLogs`，且社区有无报错返回空数组的报告。可靠扫描需可读日志的服务商，或专门的链上索引服务。此仓库使用轮询，**不是秒级 WebSocket 扫块**。`doctor-logs` 仅证明调用没直接报错；无事件不代表服务正常。

## CA Check

选择 DexScreener BSC 中与CA匹配的基础币交易池，并按流动性选最大池作为展示数据。再尝试调用 Binance Web3公开安全审核接口。行情与审核都可能失败，分别记录警告。不会因某个来源超时就给出“安全”结论。

## Routine Audit

输入 `{name, enabled, interval_minutes, active_hours_per_day, estimated_events_per_day}`。本地按该频率估算每周计划运行次数，并与给定的“每天预期有效事件”对照。不会访问GroK账户、读取真实Token余额、删除Routine或修改计划任务。请将结果视为模型设想，不是账单。

## 不提供的能力

- 真实节约 token 数、货币数、GPU计费。
- Bot后台自动读取所有Routine的运行历史。
- 无配置从公网自动识别所有CA诈骗。
- Auto Mint、Sniper、钱包托管、批量账户。
- 可靠的任务队列、数据库、重试投递保证；如需生产级稳定性应接入独立队列和监控。
