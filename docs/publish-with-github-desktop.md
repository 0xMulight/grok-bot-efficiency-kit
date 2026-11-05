# 不用命令行，把这套完整工具发布成新的GitHub仓库

你在Windows 10上操作即可。下面说明的目标是一个 **新的独立仓库**，不要往已有 `agent-id-hunter` 仓库里复制。

## 选择GitHub Desktop

1. 安装或打开 [GitHub Desktop](https://desktop.github.com/)，登录自己的 `0xMulight` GitHub账号。
2. 下载并解压 `grok-bot-efficiency-kit.zip`，得到同名文件夹，里面应当直接看到 `README.md`、`SKILL.md`、`grok_kit`、`docs`、`启动工具.bat`，不要多包一层空目录。
3. 在GitHub Desktop选择 `File → Add Local Repository...`，指向解压后的文件夹。
4. 如果提示 **This directory does not appear to be a Git repository**，点 **Create a repository here**，选择名称 `grok-bot-efficiency-kit`，描述见下文。
5. 完成后点击 **Publish repository**。确认Owner是 `0xMulight`、仓库名正确；希望公开分享就取消 `Keep this code private`。点击Publish后等待确认。
6. 在浏览器打开你的新仓库首页，确认README已显示、`docs/index.html`存在、Actions测试运行。

**推荐仓库信息**

- Repository name: `grok-bot-efficiency-kit`
- Description: `One Skill, three tools: read-only BSC events, CA checks, and Grok Bot Routine usage audit. By @0xMulight.`
- Topics: `grok-bot`, `bsc`, `ai-agent`, `web3`, `skill`, `webhook`, `python`, `routine`
- License: MIT（文件已包含）
- Default branch: `main`

## 打开独立官网主页

GitHub仓库的 `README.md` 就是仓库主页；仓库里还提供了一个静态Landing Page，文件为 `docs/index.html`。

要让它成为可访问的网页，可在仓库 **Settings → Pages → Build and deployment** 里选 **Deploy from a branch**，Branch选 `main`，folder选 `/docs`，保存。部署成功后，Pages会提供页面地址。

如果找不到 `/docs` 或 Pages不可用，先确认仓库已经发布到GitHub、main分支已存在，并检查账号Pages权限。无需为静态主页配置任何API密钥。

## 发布后至少检查三件事

- 仓库 `README.md` 主页显示正确，链接能打开；无历史旧仓库引用。
- GitHub Actions的Python离线测试通过；代码不会自启动或者连接钱包。
- `config.local.json`、`.env`、`data/` 未提交到GitHub。

## 注意

*上传公开文件≠连接Grok Bot。* 真实BSC监控仍要自己配置一个支持`eth_getLogs`的RPC，Webhook还需要在你的Grok Bot Routine中创建，并只在明确同意耗额时启用。
