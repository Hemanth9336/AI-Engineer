---
type: task
title: "Measure your retrieval hit rate"
minutes: 10
---

## Set up

Set up gives you the 8 ops docs, `eval.json`, and `rag_lib.py` - a finished RAG library with `collection`, `index_docs()` and `answer()`, the same as topic 11's solution.

```bash
ailab status
mkdir -p /root/rag-lab/12-eval /root/answers
cd /root/rag-lab/12-eval
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
cat > eval.json <<'EOF'
[
  {
    "question": "When are production deploys allowed?",
    "source": "deploys.md",
    "expect": "Tuesday"
  },
  {
    "question": "How long are database backups kept?",
    "source": "backups.md",
    "expect": "35 days"
  },
  {
    "question": "How quickly must the primary on-call acknowledge a page?",
    "source": "oncall.md",
    "expect": "15 minutes"
  },
  {
    "question": "Who approves production access requests?",
    "source": "access.md",
    "expect": "team lead"
  },
  {
    "question": "When must the status page be updated during a SEV1?",
    "source": "incidents.md",
    "expect": "30 minutes"
  },
  {
    "question": "How often must secrets be rotated?",
    "source": "security.md",
    "expect": "90 days"
  },
  {
    "question": "At what percentage of the budget do cloud cost alerts fire?",
    "source": "costs.md",
    "expect": "80%"
  },
  {
    "question": "How many read replicas does the main database have?",
    "source": "databases.md",
    "expect": "two"
  },
  {
    "question": "What is the office wifi password?",
    "source": null,
    "expect": null
  },
  {
    "question": "Which band is playing at the summer party?",
    "source": null,
    "expect": null
  }
]
EOF
cat > rag_lib.py <<'EOF'
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
        print("usage: rag_lib.py index | rag_lib.py ask QUESTION", file=sys.stderr)
        sys.exit(2)
EOF
python -c "import rag_lib; print(rag_lib.index_docs(), 'chunks indexed')"
```

## What to build

Write `/root/rag-lab/12-eval/eval_retrieval.py`, used as `python eval_retrieval.py EVAL_FILE OUT_FILE [K]` (K defaults to 3):

1. For every item in EVAL_FILE that has a `source`, query `rag_lib.collection` with the question for K results.
2. A **hit** is when the item's `source` is among the sources of the results.
3. Write OUT_FILE as JSON:

   ```json
   { "k": 3, "total": 8, "hits": 8, "hit_rate": 1.0, "misses": [] }
   ```

   where each miss is `{"question", "expected", "got"}` (`got` = the list of retrieved sources), and `hit_rate` is `hits / total` rounded to 3 decimals.

```bash
python eval_retrieval.py eval.json /root/answers/12-retrieval.json
```

The checker also runs it on an eval file of its own.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `from rag_lib import collection`.
- `got = [m["source"] for m in res["metadatas"][0]]`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-lab/12-eval
cat > eval_retrieval.py <<'EOF'
import json
import sys

from rag_lib import collection

if len(sys.argv) < 3:
    print("usage: eval_retrieval.py EVAL_FILE OUT_FILE [K]", file=sys.stderr)
    sys.exit(2)
k = int(sys.argv[3]) if len(sys.argv) > 3 else 3
items = [i for i in json.load(open(sys.argv[1])) if i.get("source")]
hits, misses = 0, []
for item in items:
    res = collection.query(query_texts=[item["question"]], n_results=k)
    got = [m["source"] for m in res["metadatas"][0]]
    if item["source"] in got:
        hits += 1
    else:
        misses.append({"question": item["question"], "expected": item["source"], "got": got})
result = {"k": k, "total": len(items), "hits": hits, "hit_rate": round(hits / len(items), 3), "misses": misses}
json.dump(result, open(sys.argv[2], "w"), indent=2)
print(f"hit rate @{k}: {hits}/{len(items)}")
EOF
python eval_retrieval.py eval.json /root/answers/12-retrieval.json
cat /root/answers/12-retrieval.json
```

</details>

## Check your work

```bash
D=/root/rag-lab/12-eval; cd $D 2>/dev/null || echo "❌ create $D"
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
r = load("/root/answers/12-retrieval.json") or {}
ok(r.get("k") == 3 and r.get("total") == 8 and r.get("hits") == 8 and r.get("hit_rate") == 1.0 and r.get("misses") == [], "12-retrieval.json: k 3, 8 of 8 hits, hit rate 1.0", f"/root/answers/12-retrieval.json should report k 3, total 8, hits 8, hit_rate 1.0, misses [] - got {r}")
probe = [
    {"question": "How long are database backups kept?", "source": "backups.md", "expect": "35 days"},
    {"question": "When are production deploys allowed?", "source": "costs.md", "expect": "Tuesday"},
    {"question": "How often must secrets be rotated?", "source": "security.md", "expect": "90 days"},
    {"question": "What is the office wifi password?", "source": None, "expect": None},
]
Path("/tmp/probe-eval.json").write_text(json.dumps(probe))
rc, out, err = run("eval_retrieval.py", "/tmp/probe-eval.json", "/tmp/probe-out.json", "1")
p = load("/tmp/probe-out.json") or {}
ok(rc == 0 and p.get("k") == 1 and p.get("total") == 3 and p.get("hits") == 2 and p.get("hit_rate") == 0.667, "on a new eval file with K=1: 2 of 3 hits, hit rate 0.667", f"on the checker's eval file with K=1 expected total 3, hits 2, hit_rate 0.667 - got {p} {err[-150:]}")
miss = (p.get("misses") or [{}])[0]
ok(len(p.get("misses") or []) == 1 and miss.get("question") == "When are production deploys allowed?" and miss.get("expected") == "costs.md" and miss.get("got") == ["deploys.md"], "the miss lists question, expected and got", f"the miss should be the deploys question with expected costs.md and got ['deploys.md'] - got {p.get('misses')}")
PYEOF
```

## What you learned

- Hit rate @ k = share of answerable questions whose source is in the top k.
- It needs no chat model - measure retrieval on its own.
- The list of misses tells you exactly what to fix.
