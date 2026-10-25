#!/usr/bin/env bash
# Install everything the Harness Engineering skill uses on an Ubuntu 24.04 machine (run as root).
#
#   the FDE lab (gateway, ailab, Python venv, claude, lab-embed, mcp, lab-tiny) - installed or refreshed first
#   labmock: a scripted stand-in for a chat model, for testing harness code - /opt/harness/labmock.py
#   the work folder /root/harness-lab
#
# Then: ailab setup (first time only) and ailab test
set -euo pipefail

BASE=${AI_ENGINEER_RAW_BASE:-https://raw.githubusercontent.com/Hemanth9336/AI-Engineer/main/setup}

[ "$(id -u)" = 0 ] || { echo "run as root" >&2; exit 1; }

echo "== installing or refreshing the FDE lab"
curl -fsSL "$BASE/fde/install-tools.sh" | bash

echo "== installing labmock into /opt/harness"
mkdir -p /opt/harness
curl -fsSL "$BASE/harness/labmock.py" -o /opt/harness/labmock.py
chmod 644 /opt/harness/labmock.py

mkdir -p /root/harness-lab
/root/ai-lab/.venv/bin/python - <<'EOF'
import sys
sys.path.insert(0, "/opt/harness")
from labmock import MockModel
from openai import OpenAI
with MockModel(["labmock OK"]) as m:
    print(OpenAI(base_url=m.url, api_key="mock").chat.completions.create(model="lab-fast", messages=[{"role": "user", "content": "hi"}]).choices[0].message.content)
EOF
claude --version >/dev/null && echo "claude OK"

echo
echo "Harness lab is installed. Next:"
echo "  source ~/.bashrc"
[ -f /etc/ailab/config.yaml ] || echo "  ailab setup        # choose a provider for the chat models"
echo "  ailab test         # one short request to every lab model"
