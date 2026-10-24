---
type: task
title: "Rebuild your pipeline on Chroma"
minutes: 17
---

## Scenario

The ops docs have doubled to 8 files and other teams want to call the assistant from their own scripts. Move the store to Chroma and expose the pipeline as functions.

## Set up

```bash
ailab status
mkdir -p /root/rag-lab/11-rag-chroma
cd /root/rag-lab/11-rag-chroma
mkdir -p docs
cat > docs/deploys.md <<'EOF'
# Deploys
Production deploys happen on Tuesdays and Thursdays at 14:00 UTC. Deploys are frozen for the last two weeks of December. To roll back a bad release, run shipit rollback with the service name.
EOF
cat > docs/oncall.md <<'EOF'
# On-call
The on-call rotation changes every Monday at 09:00 UTC. The primary on-call engineer must acknowledge a page within 15 minutes. If they do not, the page escalates to the secondary, and after another 15 minutes to the engineering manager.
EOF
cat > docs/backups.md <<'EOF'
# Backups
Database backups run every night at 02:00 UTC and are kept for 35 days. A restore test is run on the first Monday of every month to prove the backups work.
EOF
cat > docs/access.md <<'EOF'
# Production access
Request production access with an ACCESS ticket in Jira. Your team lead approves the request, and access expires automatically after 8 hours.
EOF
cat > docs/incidents.md <<'EOF'
# Incidents
A SEV1 is any outage that customers can see. During a SEV1 the incident commander updates the status page within 30 minutes of the start. A written postmortem is due within five business days.
EOF
cat > docs/security.md <<'EOF'
# Security
Secrets and API keys must be rotated every 90 days. Report phishing emails to the security team with the Report button in your mail client. Laptops must have disk encryption turned on.
EOF
cat > docs/costs.md <<'EOF'
# Cloud costs
Budget alerts fire when a team reaches 80% of its monthly cloud budget. Every resource must be tagged with its team and environment, or it is deleted after seven days.
EOF
cat > docs/databases.md <<'EOF'
# Databases
The main database is PostgreSQL 16, with the primary in eu-west-1 and two read replicas in other zones. Applications may open at most 500 connections in total.
EOF
ls docs
```

## What to build

Write `/root/rag-lab/11-rag-chroma/rag_chroma.py`:

1. A persistent Chroma client at `/root/rag-lab/11-rag-chroma/db` (built from the file's own location) with a collection `docs` in the cosine space, using `lab-embed` through the gateway.
2. `index_docs()` chunks every `docs/*.md` (500/100), upserts the chunks with IDs like `incidents-000` and metadata `{"source": "incidents.md", "index": 0}`, and returns the collection count.
3. `answer(question, k=4)` retrieves k chunks, asks `lab-fast` at `temperature=0` with the grounding rules, and **returns** a dict `{"question", "answer", "sources"}`. `sources` lists the retrieved files in rank order, without repeats. On a refusal, `answer` is exactly `I don't know based on the documents.` and `sources` is `[]`.
4. Commands: `python rag_chroma.py index` and `python rag_chroma.py ask QUESTION...` (prints the dict as JSON).

```bash
python rag_chroma.py index
python rag_chroma.py ask "When is a written postmortem due?"
```

The checker imports your module and calls `answer()` with questions you haven't seen.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `HERE = Path(__file__).resolve().parent`, then `HERE / "db"` and `HERE / "docs"`.
- Topic 09's collection code plus topic 10's prompt code is most of the file.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-lab/11-rag-chroma
cat > rag_chroma.py <<'EOF'
import json
import os
import sys
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from openai import OpenAI

HERE = Path(__file__).resolve().parent
REFUSAL = "I don't know based on the documents."
client = OpenAI()
embed = OpenAIEmbeddingFunction(
    api_key_env_var="OPENAI_API_KEY", api_base=os.environ["OPENAI_BASE_URL"], model_name="lab-embed"
)
collection = chromadb.PersistentClient(path=str(HERE / "db")).get_or_create_collection(
    "docs", embedding_function=embed, configuration={"hnsw": {"space": "cosine"}}
)


def chunk_text(text, size=500, overlap=100):
    chunks, start = [], 0
    while True:
        chunks.append(text[start:start + size])
        if start + size >= len(text):
            return chunks
        start += size - overlap


def index_docs(folder=HERE / "docs"):
    ids, docs, metas = [], [], []
    for path in sorted(Path(folder).glob("*.md")):
        for i, text in enumerate(chunk_text(path.read_text())):
            ids.append(f"{path.stem}-{i:03d}")
            docs.append(text)
            metas.append({"source": path.name, "index": i})
    collection.upsert(ids=ids, documents=docs, metadatas=metas)
    return collection.count()


def answer(question, k=4):
    res = collection.query(query_texts=[question], n_results=k)
    hits = list(zip(res["documents"][0], res["metadatas"][0]))
    context = "\n\n".join(f'<document source="{m["source"]}">\n{d}\n</document>' for d, m in hits)
    system = (
        "Answer the question using only the documents below. "
        f"If they do not contain the answer, reply exactly: {REFUSAL}\n\n{context}"
    )
    resp = client.chat.completions.create(
        model="lab-fast",
        temperature=0,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": question}],
    )
    text = resp.choices[0].message.content.strip()
    if "don't know based on the documents" in text.lower():
        return {"question": question, "answer": REFUSAL, "sources": []}
    return {"question": question, "answer": text, "sources": list(dict.fromkeys(m["source"] for _, m in hits))}


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "index":
        print(f"{index_docs()} chunks in the docs collection")
    elif len(sys.argv) >= 3 and sys.argv[1] == "ask":
        print(json.dumps(answer(" ".join(sys.argv[2:])), indent=2))
    else:
        print("usage: rag_chroma.py index | rag_chroma.py ask QUESTION", file=sys.stderr)
        sys.exit(2)
EOF
python rag_chroma.py index
python rag_chroma.py ask "When is a written postmortem due?"
```

</details>

## Check your work

```bash
D=/root/rag-lab/11-rag-chroma; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/rag_chroma.py 2>/dev/null && [ -s $D/rag_chroma.py ] && echo "✅ rag_chroma.py reads the key from the environment" || echo "❌ rag_chroma.py must not contain a key - let the SDK read it from the environment"
python - <<'PYEOF'
import json, math, os, subprocess, sys
from pathlib import Path
from openai import OpenAI
_C = OpenAI()
sys.excepthook = lambda t, e, tb: print(f"❌ check stopped: {t.__name__}: {e}")
def E(xs):
    return [d.embedding for d in _C.embeddings.create(model="lab-embed", input=xs).data]
def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))
def ok(cond, good, bad):
    print(("✅ " + good) if cond else ("❌ " + bad))
def load(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None
def run(*args, cwd=None):
    r = subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=cwd)
    return r.returncode, r.stdout.strip(), r.stderr.strip()
import importlib
REFUSAL = "I don't know based on the documents."
os.chdir("/tmp")
sys.path.insert(0, "/root/rag-lab/11-rag-chroma")
m = importlib.import_module("rag_chroma")
n = m.index_docs()
n2 = m.index_docs()
ok(n == n2 == 8, "index_docs() returns 8 and stays 8 when re-run (even from another folder)", f"index_docs() should return 8 both times - got {n}, {n2}")
import chromadb
c = chromadb.PersistentClient(path="/root/rag-lab/11-rag-chroma/db").get_collection("docs")
ok((c.configuration.get("hnsw") or {}).get("space") == "cosine", "the docs collection uses the cosine space", "create the docs collection with the cosine space")
g = c.get(ids=["incidents-000"], include=["metadatas"])
ok(g["metadatas"] == [{"source": "incidents.md", "index": 0}], "chunks carry source and index metadata", "chunk incidents-000 needs metadata {'source': 'incidents.md', 'index': 0}")
for q, want, src in [("How many connections may applications open in total?", "500", "databases.md"), ("What happens to untagged cloud resources?", "seven days", "costs.md"), ("How do I report a phishing email?", None, "security.md")]:
    r = m.answer(q) if want else m.answer(q, k=1)
    good = isinstance(r, dict) and set(r) >= {"question", "answer", "sources"} and r["question"] == q
    ok(good and (want is None or want in r["answer"]) and r["sources"][:1] == [src] and len(r["sources"]) == len(set(r["sources"])) <= (4 if want else 1),
       f"answer('{q[:40]}...'{'' if want else ', k=1'}) -> sources start with {src}", f"answer('{q}') should return a dict answered from {src} - got {r!r}"[:400])
r = m.answer("Which band is playing at the summer party?")
ok(isinstance(r, dict) and r.get("answer") == REFUSAL and r.get("sources") == [], "an unanswerable question returns the exact refusal and no sources", f"expected answer = {REFUSAL} and sources = [] - got {r!r}")
rc, out, err = run("/root/rag-lab/11-rag-chroma/rag_chroma.py", "ask", "When is a written postmortem due?")
try:
    j = json.loads(out)
except ValueError:
    j = {}
ok(rc == 0 and "five business days" in j.get("answer", "") and j.get("sources", [""])[0] == "incidents.md", "python rag_chroma.py ask prints the dict as JSON", f"python rag_chroma.py ask QUESTION should print the result as JSON - got {out[-200:]!r}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and .temperature == 0 and .system and (.client | startswith("OpenAI/Python")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged a grounded lab-fast call at temperature 0" || echo "❌ the gateway has no lab-fast call at temperature 0 with a system message from your script"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Clear interfaces let you swap the store without touching chunking or generation.
- Expose RAG as `index_docs()` and `answer()` returning a dict - wrappers come later.
- Build paths from `Path(__file__)` so the module works from any folder.
