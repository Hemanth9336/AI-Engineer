#!/usr/bin/env bash
# Install everything the AI Fundamentals skill uses on an Ubuntu 24.04 machine (run as root).
#
#   the lab AI gateway: LiteLLM in /opt/ailab/venv, the request logger, four provider profiles, and the ailab command
#   a Python venv at /root/ai-lab/.venv with the openai, anthropic and langchain libraries the tasks import
#   claude (Claude Code), pointed at the gateway instead of an Anthropic account
#   a private lab key in /root/.config/ailab/env (mode 600), loaded by ~/.bashrc
#
# After it finishes, run: ailab setup
set -euo pipefail

RAW=${AI_ENGINEER_RAW:-https://raw.githubusercontent.com/Hemanth9336/AI-Engineer/main/setup/ai-fundamentals}

[ "$(id -u)" = 0 ] || { echo "run as root" >&2; exit 1; }

export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq python3 python3-venv python3-pip curl jq git ca-certificates openssl bsdextrautils >/dev/null

python3 -m venv /opt/ailab/venv
/opt/ailab/venv/bin/pip install -q --upgrade pip
/opt/ailab/venv/bin/pip install -q 'litellm[proxy]==1.106.3'

mkdir -p /root/ai-lab /root/answers /var/log/ailab /etc/ailab/profiles /usr/local/lib/ailab /root/.config/ailab
python3 -m venv /root/ai-lab/.venv
/root/ai-lab/.venv/bin/pip install -q --upgrade pip
/root/ai-lab/.venv/bin/pip install -q 'openai==2.54.0' 'anthropic==1.17.0' 'langchain==1.4.7' 'langchain-openai==1.7.2'

curl -fsSL "$RAW/ailab_logger.py" -o /usr/local/lib/ailab/ailab_logger.py
for p in openrouter openai anthropic ollama; do
  curl -fsSL "$RAW/profiles/$p.yaml" -o "/etc/ailab/profiles/$p.yaml"
done
curl -fsSL "$RAW/ailab" -o /usr/local/bin/ailab
chmod +x /usr/local/bin/ailab

if ! command -v claude >/dev/null && [ ! -x /root/.local/bin/claude ]; then
  curl -fsSL https://claude.ai/install.sh | bash
fi
[ -f /root/.claude.json ] || echo '{"hasCompletedOnboarding": true}' > /root/.claude.json

umask 077
if [ ! -f /root/.config/ailab/env ]; then
  KEY="sk-lab-$(openssl rand -hex 16)"
  cat > /root/.config/ailab/env <<EOF
# AI Fundamentals lab settings - loaded by ~/.bashrc. Never commit, print or paste this file.
export LAB_AI_URL=http://localhost:4000
export LAB_AI_KEY=$KEY
export OPENAI_BASE_URL=\$LAB_AI_URL/v1
export OPENAI_API_KEY=\$LAB_AI_KEY
export ANTHROPIC_BASE_URL=\$LAB_AI_URL
export ANTHROPIC_AUTH_TOKEN=\$LAB_AI_KEY
export ANTHROPIC_MODEL=lab-fast
export ANTHROPIC_DEFAULT_HAIKU_MODEL=lab-mini
export ANTHROPIC_DEFAULT_SONNET_MODEL=lab-fast
export ANTHROPIC_DEFAULT_OPUS_MODEL=lab-smart
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export PATH=/root/ai-lab/.venv/bin:/root/.local/bin:\$PATH
EOF
fi
chmod 600 /root/.config/ailab/env
umask 022

grep -q 'ailab/env' /root/.bashrc 2>/dev/null || cat >> /root/.bashrc <<'EOF'

# AI Fundamentals lab
[ -f ~/.config/ailab/env ] && . ~/.config/ailab/env
EOF

. /root/.config/ailab/env
python -c "import openai, anthropic, langchain; print('openai', openai.__version__, '| anthropic', anthropic.__version__, '| langchain', langchain.__version__)"
claude --version
echo
echo "AI Fundamentals lab is installed. Next:"
echo "  source ~/.bashrc"
echo "  ailab setup        # choose a provider and paste its key - it is stored for the gateway only"
echo "  ailab test         # one short request to each of the five lab models"
