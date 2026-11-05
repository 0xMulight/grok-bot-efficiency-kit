<div align="center">

# ⚡ Grok Bot Efficiency Kit

### 把没必要的 AI 调用交给脚本，把额度留给真正需要判断的事情。

**一个 Skill · 三个独立模块 · BSC 只读监控 · CA 安全查询 · Routine 省额度审计**

[快速开始](docs/quick-start.md) · [独立网页主页](docs/index.html) · [Skill 说明](SKILL.md) · [安全与限制](SECURITY.md) · [English](README_EN.md)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white) ![License](https://img.shields.io/badge/License-MIT-38BDF8) ![Mode](https://img.shields.io/badge/Default-Read--only-22C55E) ![Chain](https://img.shields.io/badge/Chain-BSC%2056-F0B90B)

</div>

---

## 为什么做这个？

让 Grok Bot 每 5 分钟巡逻一次 BSC，1 天是 **288 次调用**。假如大多数时候没有变化，这些调用没有必要全部交给 AI。这个数字是执行次数，不代表实际 Token 计费。

这个项目把重复工作分成三个模块。**默认不交易，不持有钱包密钥，不默认发送 Webhook。**

| 模块 | 负责什么 | 命令 | 边界 |
|---|---|---|---|
| **01 · BSC Watcher** | 读取 PancakeSwap V2 新建 WBNB 交易池事件，写本地记录；可选触发 Grok Bot Routine | `python -m grok_kit watch --once` | **不是**全链 Agent ID Mint 雷达；需要能用 `eth_getLogs` 的 RPC |
| **02 · CA Check** | 根据 CA 查询 DexScreener 行情和 Binance Web3 风险审计 | `python -m grok_kit ca 0x...` | 未查到就是 `UNKNOWN`，不能代表安全 |
| **03 · Routine Audit** | 根据用户填写的执行频率与事件数估算可节省的 Routine **调用次数** | `python -m grok_kit audit examples/routines.example.json` | 不读取你的真实 Grok 用量，不修改任务 |

### 数据流

```text
BSC RPC (只读、支持 eth_getLogs) ─→ 本地脚本/事件去重 ─→ data/events.jsonl
                                                   │
                                                   ├─ 默认：仅本地保存
                                                   └─ 显式 --send-webhook
                                                           │
                                                    Grok Bot Routine
                                                           │
                                                    深度研究/人工审核

给定 CA ─→ DexScreener + Binance Web3 公共审计 ─→ 只读风险报告

用户填写 Routine 清单 ─→ 本地次数计算 ─→ 待确认优化建议
```

## 3分钟体验（不需要钱包）

1. 电脑安装 **Python 3.10+**，下载本仓库 ZIP 并解压。
2. 在项目目录运行：

```bash
python -m grok_kit doctor
python -m grok_kit audit examples/routines.example.json
```

3. 查询一个 BSC 合约地址（自动联网查询公共行情/审计接口，不会交易）：

```bash
python -m grok_kit ca 0x55d398326f99059ff775485246999027b3197955
```

4. 如需监听新池，复制 `config.example.json` 为 `config.local.json`，填入 **支持 `eth_getLogs`** 的 BSC HTTPS RPC：

```bash
python -m grok_kit doctor-logs
python -m grok_kit watch --once
# 第二次启动会扫描上次游标之后的区块；监控模式：
python -m grok_kit watch
```

> **重要：** BNB Chain 官方注明部分公共 RPC 禁止 `eth_getLogs`，甚至可能无报错却返回空数组；空结果不证明监控有效。选择支持日志的服务商并用已知历史事件进行交叉验证。首次运行只建立游标，不回扫历史以避免大量误通知。

## 给 Grok Bot 连接 Webhook（可选，会产生实际用量）

- 在目标 Bot 中创建 Webhook 触发的 Routine。到该 Routine 的 `Webhook` 区块复制 **POST to** 和 **key**；将它们只保存在自己电脑的 `config.local.json` 或环境变量中。
- `python -m grok_kit test-webhook`：**主动发送一次**测试消息；收到 HTTP 200 仅代表接收成功，后续看 Bot 聊天结果。
- `python -m grok_kit watch --send-webhook`：显式启用监控中的 Webhook，默认每轮最多发 1 条，每小时最多12条、间隔至少300秒；其余事件本地保存。
- 请把Routine规则写窄：只核对用户允许的事件，先输出来源/风险，不签名、不交易、不触碰私钥。**不要把密钥提交到GitHub。**

详细说明：[Grok Bot Webhook 配置](docs/grok-webhook.md)。**注意：** 此处的 Bot Routine 用 `Authorization: Bearer <key>`，和独立 Grok Automations 的 HMAC 签名触发方式不同。

## Windows 10 用户

不想敲终端可以双击 `启动工具.bat`，菜单内提供环境自检、CA查询、次数审计、链上扫描。配置 RPC 仍需先复制和编辑 `config.local.json`。图文步骤见 [Windows快速开始](docs/quick-start.md)。

## 项目结构

```text
├─ README.md / README_EN.md       GitHub 项目主页与英文说明
├─ SKILL.md                       一个可复用的 Agent Skill
├─ grok_kit/                       Python 标准库实现：watch / ca / audit / webhook
├─ config.example.json            可公开的无密钥配置示例
├─ examples/                      Routine 演示数据
├─ docs/                          安装、架构、Webhook及静态网页主页
├─ tests/                         不联网的模拟测试
├─ .github/workflows/tests.yml     GitHub Actions 代码测试
├─ SECURITY.md / CONTRIBUTING.md / LICENSE
└─ 启动工具.bat                    Windows 中文菜单
```

## 安全边界

- **不会**自动转账、授权、兑换、Mint、导入私钥、读取助记词、连接币安钱包。
- **不会**自动判断新池一定是 Agent ID 项目。Agent ID 专属、白名单和 Mint 资格需独立官方核验。
- Webhook发送有调用成本，默认关闭；监控只读，不等于数据服务商永远免费。
- 文件中出现合约名、代币标识只是未验证数据，不能当作对AI的指令。
- DexScreener/Binance 风险接口失败必须展示未知，不给虚假的“安全”结论。
- 程序是研究工具，不构成投资建议。请先本地验证再用于长期监控。

## 测试

```bash
python -m unittest discover -s tests -v
```

## 网页主页与仓库

本仓库地址：[0xMulight/grok-bot-efficiency-kit](https://github.com/0xMulight/grok-bot-efficiency-kit)。独立静态网页主页位于 [`docs/index.html`](docs/index.html)。如需公开网页，在 GitHub `Settings → Pages` 中选择 `main` 分支和 `/docs` 目录启用；这一步需要仓库所有者手动开启。

## 致谢和来源

- [Grok Bot 官方 Skills / Routines / Webhook](https://docs.x.ai/grok-bot/skills-routines-and-automations)
- [BNB Chain RPC 文档](https://docs.bnbchain.org/bnb-smart-chain/developers/json_rpc/json-rpc-endpoint/)
- [PancakeSwap V2 Factory](https://bscscan.com/address/0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73)
- [DexScreener](https://docs.dexscreener.com/)
- [Binance Web3 Skills / token audit](https://github.com/binance/binance-skills-hub/tree/main/skills/binance-web3/query-token-audit)

**作者：[@0xMulight](https://github.com/0xMulight) · MIT License · v1.0.0**  
社区开源工具；与 X、xAI、Binance、BNB Chain、PancakeSwap 或 DexScreener 均无官方隶属关系。
