#!/usr/bin/env bash
# Install everything the Claude Code Fundamentals skill uses on an Ubuntu 24.04 machine (run as root).
#
#   git, jq, curl, python3 + venv          - the tools the tasks and checkers call
#   Node.js 22                             - recorded in topic 01 (the CLI itself does not need it)
#   Claude Code (native installer)         - the `claude` command
#   /root/cc-lab/.venv with mcp 1.30.0     - put first on PATH, so `python3` can import mcp (topic 15)
#   the work folder /root/cc-lab
#
# Then: run `claude` once and sign in.
set -euo pipefail

[ "$(id -u)" = 0 ] || { echo "run as root" >&2; exit 1; }
export DEBIAN_FRONTEND=noninteractive

echo "== installing system packages"
apt-get update -qq
apt-get install -y -qq git jq curl ca-certificates python3 python3-venv >/dev/null

if ! command -v node >/dev/null || [ "$(node -p 'process.versions.node.split(".")[0]')" -lt 22 ]; then
  echo "== installing Node.js 22"
  curl -fsSL https://deb.nodesource.com/setup_22.x | bash - >/dev/null
  apt-get install -y -qq nodejs >/dev/null
fi

if ! command -v claude >/dev/null; then
  echo "== installing Claude Code"
  curl -fsSL https://claude.ai/install.sh | bash
fi
export PATH="$HOME/.local/bin:$PATH"

echo "== creating /root/cc-lab and its Python venv"
mkdir -p /root/cc-lab
[ -x /root/cc-lab/.venv/bin/python ] || python3 -m venv /root/cc-lab/.venv
/root/cc-lab/.venv/bin/pip install -q --upgrade pip
/root/cc-lab/.venv/bin/pip install -q 'mcp==1.30.0'

grep -q 'cc-lab/.venv/bin' /root/.bashrc 2>/dev/null || cat >> /root/.bashrc <<'EOF'
# Claude Code Fundamentals lab
export PATH="/root/cc-lab/.venv/bin:$HOME/.local/bin:$PATH"
EOF

git config --global user.name >/dev/null || git config --global user.name "Lab Learner"
git config --global user.email >/dev/null || git config --global user.email "learner@lab.local"

/root/cc-lab/.venv/bin/python -c 'import mcp.server.fastmcp; print("mcp OK")'
echo "node $(node --version)"
claude --version

echo
echo "Claude Code lab is installed. Next:"
echo "  source ~/.bashrc"
echo "  claude             # first run: sign in with your Claude account (it remembers you after that)"
echo "If you already installed the AI Fundamentals lab, Claude Code can use the lab gateway instead:"
echo "  its ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN are already in your environment - no sign-in needed."
