# 快速开始（Windows 10 / 11）

推荐从「只读自检 → CA 查询 → Routine 审计」入手。这三项不需要任何钱包、不需要关联币安账户。

## 1. 安装 Python

从 [Python 官方网站](https://www.python.org/downloads/windows/) 安装 **Python 3.10+**，安装时勾选 **Add python.exe to PATH**。本项目核心代码仅使用 Python 标准库，不需要 `pip install`。

## 2. 下载仓库

在 GitHub 项目页点击 `Code → Download ZIP`，解压到例如 `D:\GrokBotKit`。**不要**把下载的 `.zip` 本身当作可运行文件。

## 3. 双击 `启动工具.bat`

菜单可选：
- `1` 环境自检（本地，不联网）
- `2` 计算示例 Routine 执行次数（本地，不联网）
- `3` 粘贴 BSC 合约地址，查询行情与公开安全审计
- `4` 检查所填 RPC 是否接受 `eth_getLogs`
- `5` 扫描一次新区块，新安装时仅建立游标
- `6` 持续扫描，只写本地记录（**不发给 Grok Bot**）
- `7` 发送一次真实 Webhook 测试（**会消耗用量**）

没有安装 Python 或没有加入 PATH 时，请先处理环境问题。

## 4. 配置 BSC 监控（可选）

复制 `config.example.json`，重命名为 `config.local.json`。填入支持 `eth_getLogs` 的 HTTPS BSC RPC URL。建议从服务商获取专属节点，**不要把这个文件传到 GitHub**。

```json
{
  "bsc_rpc_url": "https://YOUR-LOGS-ENABLED-RPC",
  "data_dir": "data",
  "monitor": {"confirmations": 3, "batch_blocks": 50, "poll_seconds": 15, "max_webhooks_per_cycle": 1},
  "webhook": {"url": "", "key": ""}
}
```

先运行菜单 `4`；即使返回日志数为0，也不能证明节点没有阉割 `eth_getLogs`。你需要向 RPC 服务商确认支持此方法，并用可信的历史 PairCreated 事件对照。

首次运行 `5` 只建立游标；过一段时间，再选 `5` 查看新增事件。扫描结果写到 `data/events.jsonl`。重复启动默认从已保存的区块继续，不会从创世块重扫。

**覆盖范围：仅 PancakeSwap V2 的 WBNB 新交易池。不是 Agent ID专属监控、NFT Mint探测或全BSC市场雷达。** 需要更广覆盖时应新增明确的数据源和测试。

## 5. 启用 Grok Bot Webhook（可选）

参见 [Webhook 图文步骤文字版](grok-webhook.md)。粘贴你自己的 Bot Routine `POST to` 和 `key` 到本地文件，菜单 `7` 发一次测试。要在命令行发送实盘监控事件，明确运行：

```bash
python -m grok_kit watch --send-webhook
```

双击菜单 `6` 刻意**不**发 Webhook，以防不了解耗额的用户误触发。

## 6. 怎样让 Grok Bot 使用这套 Skill？

把仓库的 `SKILL.md` 提供给具备相应文件与运行能力的 AI，或在支持 GitHub / Agent Skills 安装流程的环境中安装。可以尝试社区通行的命令：

```bash
npx skills add 0xMulight/grok-bot-efficiency-kit
```

这只负责把 Skill 说明提供给兼容环境。**它不会自动在 Grok Bot 的云端安装 Python，也不会自动替你运行本地脚本、连接桌面、开通Webhook或授权第三方应用。** Grok Bot 侧可能需要按照 Connect apps / Private skills 的实际可用界面单独配置。

## 常见问题

**Q：看到 `RPC eth_getLogs failed`？** BNB Chain 多数公共节点不开放日志接口，改用明确支持日志查询的供应商。

**Q：看到监控正常但一直0事件？** 不一定真没新池；可能节点返回假空数组。必须做已知事件的历史交叉验证。

**Q：CA检查返回 `UNKNOWN`？** 第三方审核接口缺数据、故障或者不支持该币，不能按安全处理。

**Q：不想使用命令行？** 使用 `启动工具.bat`。第一次配置仍要编辑本地JSON文件。

**Q：没有任何 AI 订阅，也能用吗？** CA查询/次数审计/只读扫描可以单独用；Webhook连接才需要Grok Bot Routine。
