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
python3 tp.py --no-quarantine

# Scan + delete all 401 expired credentials
python3 tp.py --no-quarantine --delete-401 --yes

# Output as JSON (for programmatic use)
python3 tp.py --output-json --no-quarantine
```

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

> **提示：** 同时包含 `cpa-codex-auth-sweep-skill.py`，可作为独立 MCP 服务器使用（`pip install mcp && python3 mcp_tp.py`）。

### CLI 使用方式

也可以直接在命令行使用：

```bash
# 常规扫描（只看不删）
python3 tp.py --no-quarantine

# 扫描 + 一键删除 401 死号
python3 tp.py --no-quarantine --delete-401 --yes

# 输出纯 JSON（供程序调用）
python3 tp.py --output-json --no-quarantine
```

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
