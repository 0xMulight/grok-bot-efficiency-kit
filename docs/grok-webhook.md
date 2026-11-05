# Grok Bot Webhook 设置和安全说明

> 适用对象：**Grok Bot Routine**。不要和另一套 `docs.x.ai/grok/automations/webhooks` 的 HMAC-SHA256 签名Webhook混淆。

## 1. 在Bot里创建Routine

在你的Grok Bot聊天中提出：

> 请帮我建立一条Webhook触发的只读Routine。收到 `bsc_new_wbnb_pair` 事件时，仅检查提供的BSC合约和交易池，按合约地址、流动性、可交易性、公开来源与风险提醒输出短报告。不能保证Agent ID资格，不能签名、交易、授权、Mint。收到`test`时只回复测试成功。未经确认不要发起任何外部操作。

创建后，在电脑端打开 Bot 名称 → Details → Routines，打开对应Routine，在Webhook区找到：

- `POST to`：目标HTTPS地址（保密）
- `key`：Bearer密钥（保密）
- `header`：完整Authorization字段（复制时核对）

来源：[Grok Bot 官方Routines文档](https://docs.x.ai/grok-bot/skills-routines-and-automations)。

## 2. 复制并本地保存

将 `config.example.json` 复制为 `config.local.json`，填入：

```json
"webhook": {
  "url": "https://YOUR-GROK-BOT-ROUTINE-WEBHOOK-URL",
  "key": "YOUR_PRIVATE_BEARER_KEY"
}
```

请勿在X、GitHub、聊天截图、日志里曝光这两个值。也可用本地环境变量 `GROK_BOT_WEBHOOK_URL` / `GROK_BOT_WEBHOOK_KEY`，它们优先于配置文件。

## 3. 测试单次Webhook

```bash
python -m grok_kit test-webhook
```

它会发送**真实请求并消耗一次Bot执行额度**。返回200只代表接收，不代表任务完成；到Bot对话中查看最终输出。

## 4. 显式启用监控联动

```bash
python -m grok_kit watch --send-webhook
```

没有 `--send-webhook` 的监控只落地到本地。每轮最多发1条，默认每小时最多12条、间隔至少300秒，但如果每15秒都有事件，仍可能累计大量调用。应按自身预算降低额度、缩小监控范围，必要时暂停。

## 5. 失败处理

- `HTTP 401`：密钥错、已轮换或过期。
- `HTTP 404`：Routine被删、URL不正确。
- `HTTP 429`：达到速率或用量限制。
- `HTTP 200`：已接收，不保证完成。
- 其他错误：先查看Routine是否Paused、密钥是否对应当前Webhook。

v1 若Webhook失败，会在输出中提示，事件仍保存在本地 `data/events.jsonl`；**不会自动重复重放**，避免意外扣费。生产环境应增加可靠队列、去重、可人工审核的重发机制。
