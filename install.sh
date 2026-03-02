#!/usr/bin/env bash
# --------------------------------------------------
# cpa-codex-auth-sweep  —  One-line Skill Installer
# --------------------------------------------------
set -euo pipefail

REPO="https://github.com/paradoxie/cpa-codex-auth-sweep.git"
SKILL_DIR="${SKILL_DIR:-$HOME/.gemini/antigravity/skills/cpa-codex-auth-sweep}"

echo "📦 Installing cpa-codex-auth-sweep …"

# Clone or update
if [ -d "$SKILL_DIR/.git" ]; then
  echo "→ Skill directory exists, pulling latest …"
  git -C "$SKILL_DIR" pull --ff-only
else
  echo "→ Cloning into $SKILL_DIR …"
  mkdir -p "$(dirname "$SKILL_DIR")"
  git clone "$REPO" "$SKILL_DIR"
fi

# Install Python dependency
echo "→ Installing Python dependency (aiohttp) …"
pip install aiohttp -q

echo ""
echo "✅ Done! Tell your AI: \"扫号\" or \"sweep accounts\" to start scanning."
