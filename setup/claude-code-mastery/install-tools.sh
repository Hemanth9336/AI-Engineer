#!/usr/bin/env bash
# Install everything the Claude Code Mastery skill uses on an Ubuntu 24.04 machine (run as root).
#
#   git, jq, curl, ripgrep, python3 + venv      - the tools the tasks and checkers call
#   bubblewrap, socat                           - Claude Code's Bash sandbox on Linux (topics 006, 029)
#   cron                                        - scheduled runs (topics 022, 061)
#   Node.js 22 + mcp-server-filesystem          - the filesystem MCP server (topics 031, 032)
#   Claude Code (native installer)              - the `claude` command
#   /root/mastery/.venv: mcp 1.30.0, claude-agent-sdk, pyyaml - first on PATH, so `python3` imports them
#   ~/.config/ailab/env                         - the settings scheduled scripts load (kept if it already exists)
#   the work folder /root/mastery
#   Codex CLI (optional, INSTALL_CODEX=1)       - topic 037 compares workflows; its checker works without it
#
# Then: run `claude` once and sign in (or use the AI Fundamentals lab gateway, see setup/README.md step 8).
set -euo pipefail

[ "$(id -u)" = 0 ] || { echo "run as root" >&2; exit 1; }
export DEBIAN_FRONTEND=noninteractive

echo "== installing system packages"
apt-get update -qq
apt-get install -y -qq git jq curl ca-certificates ripgrep python3 python3-venv bubblewrap socat cron >/dev/null
service cron start >/dev/null 2>&1 || true

if ! command -v node >/dev/null || [ "$(node -p 'process.versions.node.split(".")[0]')" -lt 22 ]; then
  echo "== installing Node.js 22"
  curl -fsSL https://deb.nodesource.com/setup_22.x | bash - >/dev/null
  apt-get install -y -qq nodejs >/dev/null
fi

echo "== installing the filesystem MCP server"
npm install -g -s @modelcontextprotocol/server-filesystem >/dev/null

if [ "${INSTALL_CODEX:-0}" = 1 ]; then
  echo "== installing the Codex CLI (optional)"
  npm install -g -s @openai/codex >/dev/null
fi

if ! command -v claude >/dev/null; then
  echo "== installing Claude Code"
  curl -fsSL https://claude.ai/install.sh | bash
fi
export PATH="$HOME/.local/bin:$PATH"

echo "== creating /root/mastery and its Python venv"
mkdir -p /root/mastery
[ -x /root/mastery/.venv/bin/python ] || python3 -m venv /root/mastery/.venv
/root/mastery/.venv/bin/pip install -q --upgrade pip
/root/mastery/.venv/bin/pip install -q 'mcp==1.30.0' claude-agent-sdk pyyaml

grep -q 'mastery/.venv/bin' /root/.bashrc 2>/dev/null || cat >> /root/.bashrc <<'EOF'
# Claude Code Mastery lab
export PATH="/root/mastery/.venv/bin:$HOME/.local/bin:$PATH"
EOF

mkdir -p /root/.config/ailab
if [ ! -f /root/.config/ailab/env ]; then
  cat > /root/.config/ailab/env <<'EOF'
# Settings for scripts that run outside your shell (cron, CI-style wrappers).
# Signed in with a Claude account? Nothing else is needed here.
# Using a gateway instead? Add ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN lines - never commit this file.
EOF
  chmod 600 /root/.config/ailab/env
fi
grep -q 'mastery/.venv/bin' /root/.config/ailab/env || \
  echo 'export PATH="/root/mastery/.venv/bin:$HOME/.local/bin:$PATH"' >> /root/.config/ailab/env

git config --global user.name >/dev/null || git config --global user.name "Lab Learner"
git config --global user.email >/dev/null || git config --global user.email "learner@lab.local"

/root/mastery/.venv/bin/python -c 'import mcp.server.fastmcp, claude_agent_sdk, yaml; print("python packages OK")'
command -v mcp-server-filesystem >/dev/null && echo "mcp-server-filesystem OK"
command -v bwrap >/dev/null && command -v socat >/dev/null && echo "sandbox tools OK"
echo "node $(node --version)"
claude --version
command -v codex >/dev/null && codex --version || echo "codex not installed (optional: INSTALL_CODEX=1)"

echo
echo "Claude Code Mastery lab is installed. Next:"
echo "  source ~/.bashrc"
echo "  claude             # first run: sign in with your Claude account (it remembers you after that)"
echo "If you installed the AI Fundamentals lab, Claude Code can use its gateway instead - no sign-in needed."
