#!/usr/bin/env bash
# Install everything the RAG skill uses on an Ubuntu 24.04 machine (run as root).
#
#   the AI Fundamentals lab (gateway, ailab, Python venv, claude) - installed first if it is missing, refreshed if not
#   a local embedding service (all-MiniLM-L6-v2 via Chroma's ONNX build) that the gateway serves as lab-embed
#   chromadb, langchain-chroma and langchain-text-splitters in /root/ai-lab/.venv
#   the work folders /root/rag-start and /root/rag-lab
#
# Then: ailab setup (first time only) and ailab test
set -euo pipefail

BASE=${AI_ENGINEER_RAW_BASE:-https://raw.githubusercontent.com/Hemanth9336/AI-Engineer/main/setup}
CHROMA=chromadb==1.5.9

[ "$(id -u)" = 0 ] || { echo "run as root" >&2; exit 1; }

if [ ! -x /usr/local/bin/ailab ] || [ ! -x /root/ai-lab/.venv/bin/python ]; then
  echo "== installing the AI Fundamentals lab first"
  curl -fsSL "$BASE/ai-fundamentals/install-tools.sh" | bash
else
  echo "== refreshing the gateway command, logger and profiles"
  curl -fsSL "$BASE/ai-fundamentals/ailab" -o /usr/local/bin/ailab && chmod +x /usr/local/bin/ailab
  curl -fsSL "$BASE/ai-fundamentals/ailab_logger.py" -o /usr/local/lib/ailab/ailab_logger.py
  for p in openrouter openai anthropic ollama; do
    curl -fsSL "$BASE/ai-fundamentals/profiles/$p.yaml" -o "/etc/ailab/profiles/$p.yaml"
  done
fi

echo "== installing the local embedding service"
[ -x /opt/ailab/embed/bin/python ] || python3 -m venv /opt/ailab/embed
/opt/ailab/embed/bin/pip install -q --upgrade pip
/opt/ailab/embed/bin/pip install -q "$CHROMA"
curl -fsSL "$BASE/rag/embed_server.py" -o /usr/local/lib/ailab/embed_server.py
/opt/ailab/embed/bin/python -c "from chromadb.utils.embedding_functions import DefaultEmbeddingFunction as E; print('embedding model ready, dimensions:', len(E()(['ready'])[0]))"

echo "== installing the RAG libraries into /root/ai-lab/.venv"
/root/ai-lab/.venv/bin/pip install -q "$CHROMA" 'langchain-chroma==1.1.0' 'langchain-text-splitters==1.1.3'

if [ -f /etc/ailab/config.yaml ] && ! grep -q 'lab-embed' /etc/ailab/config.yaml; then
  python3 - <<'EOF'
p = "/etc/ailab/config.yaml"
s = open(p).read()
entry = ('  - model_name: lab-embed\n'
         '    litellm_params: {model: openai/all-minilm-l6-v2, api_base: "http://127.0.0.1:4001/v1", api_key: local}\n')
s = s.replace("\nlitellm_settings:", entry + "\nlitellm_settings:", 1)
open(p, "w").write(s)
print("added lab-embed to /etc/ailab/config.yaml")
EOF
fi

mkdir -p /root/rag-start /root/rag-lab /root/answers
/root/ai-lab/.venv/bin/python -c "import chromadb, langchain_chroma, langchain_text_splitters; print('chromadb', chromadb.__version__)"

if [ -f /etc/ailab/config.yaml ]; then
  ailab restart
  ailab status || true
fi

echo
echo "RAG lab is installed. Next:"
echo "  source ~/.bashrc"
[ -f /etc/ailab/config.yaml ] || echo "  ailab setup        # choose a provider for the chat models (embeddings are local and free)"
echo "  ailab test         # one short request to every lab model, including lab-embed"
