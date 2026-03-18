# cpa-codex-auth-sweep

[English](#english) | [中文](#中文)

---

## English

A high-performance, fully async (asyncio + aiohttp) credential scanner for local [Codex](https://openai.com/index/codex/) authentication files. It probes each credential against the live API with 200+ concurrent coroutines, classifies results, and optionally purges dead tokens in one shot. Packaged as a plug-and-play **AI Agent Skill**.

### ✨ Features

- **Fully Async & High Concurrency** — Built on `asyncio` + `aiohttp`, default 200+ coroutines, scans thousands of files in seconds
- **Smart Detection** — Auto-identifies Codex auth files and sends real API probe requests
- **Precise Classification** — Distinguishes 401 (expired), quota-exceeded, unlimited, and healthy credentials
- **One-Click Cleanup** — `--delete-401` to batch-remove expired credentials
- **AI Agent Skill** — Install as a Skill, your AI assistant auto-recognizes intents like "sweep accounts" or "clean dead tokens" and executes
- **MCP Compatible** — Also ships with an MCP (Model Context Protocol) wrapper for standalone server use

### 🚀 Install

**Easiest — just tell your AI:**

> Install this skill for me: https://github.com/paradoxie/cpa-codex-auth-sweep

**Or one-liner script:**

```bash
curl -fsSL https://raw.githubusercontent.com/paradoxie/cpa-codex-auth-sweep/main/install.sh | bash
```

<details>
<summary><b>Manual install (click to expand)</b></summary>

```bash
# Step 1: Clone into your agent's skill directory
git clone https://github.com/paradoxie/cpa-codex-auth-sweep.git \
  ~/.gemini/antigravity/skills/cpa-codex-auth-sweep

# Step 2: Install Python dependency
pip install aiohttp
```

</details>

Done! ✅ Now tell your AI "sweep accounts" or "clean dead tokens" and it just works.

> **Tip:** Also includes `cpa-codex-auth-sweep-skill.py` for standalone skill server use (`pip install mcp && python3 cpa-codex-auth-sweep-skill.py`).

### CLI Usage

You can also use it directly from the command line:

```bash
# Scan only (read-only, no side effects)
python3 scanner.py --no-quarantine

# Scan + delete all 401 expired credentials
python3 scanner.py --no-quarantine --delete-401 --yes

# Output as JSON (for programmatic use)
python3 scanner.py --output-json --no-quarantine
```

### 🖥️ Server Deployment

If you have [CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI) deployed on a remote server (e.g. Ubuntu VPS), you can use this tool directly on the server to scan and clean credentials:

```bash
# 1. Clone the repo on your server
ssh your-server
cd ~
git clone https://github.com/paradoxie/cpa-codex-auth-sweep.git

# 2. Install dependency
pip3 install aiohttp

# 3. Run the scanner
cd ~/cpa-codex-auth-sweep
python3 scanner.py --no-quarantine
```

The scanner automatically reads credentials from `~/.cli-proxy-api` — the default `auth-dir` used by CLIProxyAPI.

> **Note:** If CLIProxyAPI runs under a non-root user (e.g. `ubuntu`), you must specify the full path: `--auth-dir /home/ubuntu/.cli-proxy-api`

### ⏰ Automated Scheduled Scanning (Cron)

Set up a cron job to automatically scan and purge expired credentials on a regular schedule.

**Step 1: Open the crontab editor**

```bash
crontab -e
# First time? Select 1 (nano) as the editor
```

**Step 2: Add one of the following lines at the end of the file**

```bash
# Every 12 hours (recommended — balanced between freshness and safety)
0 */12 * * * cd ~/cpa-codex-auth-sweep && python3 scanner.py --no-quarantine --delete-401 --yes --auth-dir /home/ubuntu/.cli-proxy-api >> /tmp/codex-sweep.log 2>&1

# Every 6 hours (more aggressive)
0 */6 * * * cd ~/cpa-codex-auth-sweep && python3 scanner.py --no-quarantine --delete-401 --yes --auth-dir /home/ubuntu/.cli-proxy-api >> /tmp/codex-sweep.log 2>&1

# Once daily at 3:00 AM (most conservative)
0 3 * * * cd ~/cpa-codex-auth-sweep && python3 scanner.py --no-quarantine --delete-401 --yes --auth-dir /home/ubuntu/.cli-proxy-api >> /tmp/codex-sweep.log 2>&1
```

> ⚠️ **Important:** Adjust `--auth-dir` to match your actual CLIProxyAPI auth directory path.

**Step 3: Save and exit** (nano: `Ctrl+X` → `Y` → `Enter`)

**Step 4: Verify the cron job**

```bash
crontab -l
```

**Checking logs:**

```bash
# View the latest scan log
cat /tmp/codex-sweep.log

# Or follow the log in real-time
tail -f /tmp/codex-sweep.log
```

#### Frequency Recommendations

| Frequency | Cron Expression | Best For |
|-----------|----------------|----------|
| Every 12 hours | `0 */12 * * *` | ✅ Recommended — good balance |
| Every 6 hours | `0 */6 * * *` | High-volume credential environments |
| Once daily | `0 3 * * *` | Conservative / few credentials |

> **Note:** After the first cleanup, scan volume drops significantly — only surviving credentials are probed. For example, 72 credentials → 67 deleted 401s → only 5 probed per scan.

### 🔧 Troubleshooting

<details>
<summary><b>1. <code>pip3: command not found</code></b></summary>

On Ubuntu 20.04 and some minimal server images, `pip3` is not pre-installed.

```bash
sudo apt update && sudo apt install python3-pip -y
pip3 install aiohttp
```

</details>

<details>
<summary><b>2. <code>Error: auth directory not found: /root/.cli-proxy-api</code></b></summary>

The scanner defaults to `~/.cli-proxy-api`. If CLIProxyAPI runs under a different user (e.g. `ubuntu`), `~` expands to that user's home, not `/root/`.

**Solution:** Specify the correct path with `--auth-dir`:

```bash
# Check your CLIProxyAPI config to find the actual auth-dir
cat /home/ubuntu/cliproxyapi/config.yaml | grep auth-dir

# Then specify the full path
python3 scanner.py --no-quarantine --auth-dir /home/ubuntu/.cli-proxy-api
```

**How to find it if you forgot:**

```bash
# Find the running CLIProxyAPI process
ps aux | grep cli-proxy

# Find config files
find / -name "config.yaml" -path "*cli*" 2>/dev/null
```

</details>

<details>
<summary><b>3. <code>module 'asyncio' has no attribute 'to_thread'</code></b></summary>

`asyncio.to_thread()` requires **Python 3.9+**. Ubuntu 20.04 ships with Python 3.8.

This has been fixed in the latest version — the code now uses `loop.run_in_executor()` which is compatible with Python 3.8+.

```bash
# Update to the latest version
cd ~/cpa-codex-auth-sweep
git pull origin main
```

If you are stuck on an older version, you can also manually replace line 545 in `scanner.py`:

```diff
- payload = await asyncio.to_thread(_load_json, path)
+ loop = asyncio.get_event_loop()
+ payload = await loop.run_in_executor(None, _load_json, path)
```

</details>

### Cleanup Rules

Only credentials with **definitive failure** will be cleaned. Transient errors are always preserved.

| Action | Conditions |
|--------|-----------|
| **Keep** (transient) | `network error`, `timeout`, `parse error` |
| **Delete** (confirmed dead) | HTTP 401 Unauthorized, `invalid auth`, `revoked` |

### Environment Variables

| Variable | Description | Default |
|----------|------------|---------|
| `CODEX_CLIENT_ID` | Override the OAuth Client ID | `app_EMoamEEZ73f0CkXaXp7hrann` |

---

## 中文

一款高性能全异步（asyncio + aiohttp）本地 [Codex](https://openai.com/index/codex/) 认证文件探活扫描器。以 200+ 协程并发向真实 API 发起探测，精确分类凭证状态，支持一键批量清理死号。封装为即插即用的 **AI Agent Skill（智能体技能）**。

### ✨ 特性

- **全异步高并发** — 基于 `asyncio` + `aiohttp`，默认 200+ 协程并发，几千个文件几十秒扫完
- **智能探测** — 自动识别 Codex 认证文件，发起真实 API 探活请求
- **精确分类** — 区分 401（失效）、配额超限、无限额、正常存活等状态
- **一键清理** — 支持 `--delete-401` 批量删除失效凭证
- **AI Agent Skill** — 安装为技能后，AI 自动识别「扫号」「清死号」等意图并执行
- **MCP 兼容** — 同时附带 MCP（Model Context Protocol）封装，支持独立服务器模式

### 🚀 安装

**最简单 —— 直接跟你的 AI 说：**

> 帮我安装这个 skill：https://github.com/paradoxie/cpa-codex-auth-sweep

**或者一行脚本搞定：**

```bash
curl -fsSL https://raw.githubusercontent.com/paradoxie/cpa-codex-auth-sweep/main/install.sh | bash
```

<details>
<summary><b>手动安装（点击展开）</b></summary>

```bash
# 第一步：克隆到技能目录
git clone https://github.com/paradoxie/cpa-codex-auth-sweep.git \
  ~/.gemini/antigravity/skills/cpa-codex-auth-sweep

# 第二步：安装 Python 依赖
pip install aiohttp
```

</details>

搞定！✅ 跟 AI 说「扫号」「清死号」「扫描凭证」就能自动执行。

> **提示：** 同时包含 `cpa-codex-auth-sweep-skill.py`，可作为独立 MCP 服务器使用（`pip install mcp && python3 cpa-codex-auth-sweep-skill.py`）。

### CLI 使用方式

也可以直接在命令行使用：

```bash
# 常规扫描（只看不删）
python3 scanner.py --no-quarantine

# 扫描 + 一键删除 401 死号
python3 scanner.py --no-quarantine --delete-401 --yes

# 输出纯 JSON（供程序调用）
python3 scanner.py --output-json --no-quarantine
```

### 🖥️ 服务器部署

如果你在远程服务器（如 Ubuntu VPS）上部署了 [CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI)，可以直接在服务器上使用本工具扫描和清理凭证：

```bash
# 1. 在服务器上拉取项目
ssh your-server
cd ~
git clone https://github.com/paradoxie/cpa-codex-auth-sweep.git

# 2. 安装依赖
pip3 install aiohttp

# 3. 运行扫描
cd ~/cpa-codex-auth-sweep
python3 scanner.py --no-quarantine
```

扫描器会自动读取 `~/.cli-proxy-api` 目录下的凭证文件——这是 CLIProxyAPI 默认的 `auth-dir` 路径。

> **注意：** 如果 CLIProxyAPI 以非 root 用户运行（如 `ubuntu`），需指定完整路径：`--auth-dir /home/ubuntu/.cli-proxy-api`

### ⏰ 定时自动扫号（Cron 配置）

配置 cron 定时任务，自动扫描并清理失效凭证。

**第一步：打开 crontab 编辑器**

```bash
crontab -e
# 第一次使用会让你选编辑器，选 1（nano）最简单
```

**第二步：在文件末尾添加以下任一行**

```bash
# 每 12 小时执行一次（推荐 — 兼顾时效性和安全性）
0 */12 * * * cd ~/cpa-codex-auth-sweep && python3 scanner.py --no-quarantine --delete-401 --yes --auth-dir /home/ubuntu/.cli-proxy-api >> /tmp/codex-sweep.log 2>&1

# 每 6 小时执行一次（更积极）
0 */6 * * * cd ~/cpa-codex-auth-sweep && python3 scanner.py --no-quarantine --delete-401 --yes --auth-dir /home/ubuntu/.cli-proxy-api >> /tmp/codex-sweep.log 2>&1

# 每天凌晨 3 点执行一次（最保守）
0 3 * * * cd ~/cpa-codex-auth-sweep && python3 scanner.py --no-quarantine --delete-401 --yes --auth-dir /home/ubuntu/.cli-proxy-api >> /tmp/codex-sweep.log 2>&1
```

> ⚠️ **注意：** 请根据你实际的 CLIProxyAPI 认证目录路径调整 `--auth-dir` 参数。

**第三步：保存退出**（nano：`Ctrl+X` → `Y` → `Enter`）

**第四步：确认定时任务已生效**

```bash
crontab -l
```

**查看扫描日志：**

```bash
# 查看最新日志
cat /tmp/codex-sweep.log

# 实时跟踪日志
tail -f /tmp/codex-sweep.log
```

#### 扫描频率建议

| 频率 | Cron 表达式 | 适用场景 |
|------|------------|----------|
| 每 12 小时 | `0 */12 * * *` | ✅ 推荐 — 平衡时效与安全 |
| 每 6 小时 | `0 */6 * * *` | 凭证数量多、变动频繁 |
| 每天一次 | `0 3 * * *` | 保守策略 / 凭证较少 |

> **说明：** 首次清理后，扫描量会大幅下降——只有存活的凭证会被探测。例如：72 个凭证 → 删除 67 个 401 → 之后每次只探测 5 个。

### 🔧 常见问题排查

<details>
<summary><b>1. <code>pip3: command not found</code>（找不到 pip3 命令）</b></summary>

Ubuntu 20.04 等精简系统镜像默认未安装 `pip3`。

```bash
sudo apt update && sudo apt install python3-pip -y
pip3 install aiohttp
```

</details>

<details>
<summary><b>2. <code>Error: auth directory not found: /root/.cli-proxy-api</code>（找不到认证目录）</b></summary>

扫描器默认读取 `~/.cli-proxy-api`。如果 CLIProxyAPI 是以其他用户运行的（比如 `ubuntu`），`~` 会展开为该用户的 home 目录，而不是 `/root/`。

**解决方案：** 用 `--auth-dir` 指定正确的路径：

```bash
# 查看 CLIProxyAPI 配置中实际的 auth-dir 路径
cat /home/ubuntu/cliproxyapi/config.yaml | grep auth-dir

# 指定完整路径运行
python3 scanner.py --no-quarantine --auth-dir /home/ubuntu/.cli-proxy-api
```

**忘记路径了？用以下命令查找：**

```bash
# 查找运行中的 CLIProxyAPI 进程
ps aux | grep cli-proxy

# 查找配置文件
find / -name "config.yaml" -path "*cli*" 2>/dev/null
```

</details>

<details>
<summary><b>3. <code>module 'asyncio' has no attribute 'to_thread'</code>（Python 版本不兼容）</b></summary>

`asyncio.to_thread()` 需要 **Python 3.9+**，而 Ubuntu 20.04 自带的是 Python 3.8。

此问题已在最新版本中修复——代码已改用兼容 Python 3.8+ 的 `loop.run_in_executor()`。

```bash
# 更新到最新版本即可
cd ~/cpa-codex-auth-sweep
git pull origin main
```

如果使用旧版本，也可以手动修改 `scanner.py` 第 545 行：

```diff
- payload = await asyncio.to_thread(_load_json, path)
+ loop = asyncio.get_event_loop()
+ payload = await loop.run_in_executor(None, _load_json, path)
```

</details>

### 清理规则

只清理**明确失效**的认证文件，瞬时错误一律保留。

| 操作 | 条件 |
|------|-----|
| **保留**（瞬时错误） | `network error`、`timeout`、`parse error` |
| **清理**（确认失效） | HTTP 401 Unauthorized、`invalid auth`、`revoked` |

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|-------|
| `CODEX_CLIENT_ID` | 覆盖 OAuth Client ID | `app_EMoamEEZ73f0CkXaXp7hrann` |

## License

MIT
