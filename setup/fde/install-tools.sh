#!/usr/bin/env bash
# Install everything the AI Forward Deployed Engineer skill uses on an Ubuntu 24.04 machine (run as root).
#
#   the RAG lab (gateway, ailab, Python venv, claude, lab-embed, Chroma, LangChain) - installed or refreshed first
#   lab-tiny: lab-mini with a 2,048-token input window, so you can hit a context limit cheaply
#   mcp (the Model Context Protocol SDK) and jsonschema in /root/ai-lab/.venv
#   the work folder /root/fde-lab
#
# Then: ailab setup (first time only) and ailab test
set -euo pipefail

BASE=${AI_ENGINEER_RAW_BASE:-https://raw.githubusercontent.com/Hemanth9336/AI-Engineer/main/setup}

[ "$(id -u)" = 0 ] || { echo "run as root" >&2; exit 1; }

echo "== installing or refreshing the RAG lab"
curl -fsSL "$BASE/rag/install-tools.sh" | bash

echo "== installing the FDE libraries into /root/ai-lab/.venv"
/root/ai-lab/.venv/bin/pip install -q 'mcp==1.30.0' 'jsonschema==4.26.0'

if [ -f /etc/ailab/config.yaml ]; then
  python3 - <<'EOF'
import re
p = "/etc/ailab/config.yaml"
s = open(p).read()
changed = False
if "lab-tiny" not in s:
    m = re.search(r"  - model_name: lab-mini\n    litellm_params: (\{.*\})\n", s)
    if m:
        entry = f"  - model_name: lab-tiny\n    litellm_params: {m.group(1)}\n    model_info: {{max_input_tokens: 2048}}\n"
        s = s.replace("\nlitellm_settings:", "\n" + entry + "\nlitellm_settings:", 1).replace("\n\n  - model_name: lab-tiny", "\n  - model_name: lab-tiny")
        changed = True
if "enable_pre_call_checks" not in s:
    s = s.replace("\ngeneral_settings:", "\nrouter_settings:\n  enable_pre_call_checks: true\n\ngeneral_settings:", 1)
    changed = True
if changed:
    open(p, "w").write(s)
    print("added lab-tiny and the context-window check to /etc/ailab/config.yaml")
EOF
fi

mkdir -p /root/fde-lab
/root/ai-lab/.venv/bin/python -c "import mcp, jsonschema, chromadb, langchain_openai; print('FDE libraries ready')"

if [ -f /etc/ailab/config.yaml ]; then
  ailab restart
  ailab status || true
fi

echo
echo "FDE lab is installed. Next:"
echo "  source ~/.bashrc"
[ -f /etc/ailab/config.yaml ] || echo "  ailab setup        # choose a provider for the chat models"
echo "  ailab test         # one short request to every lab model, including lab-tiny and lab-embed"
