---
type: task
title: "Query your collection"
minutes: 12
---

## Set up

```bash
ailab status
mkdir -p /root/rag-lab/09-chroma /root/answers
cd /root/rag-lab/09-chroma
[ -d db ] || { echo "db/ is missing - finish the previous task first"; false; }
```

## What to build

Write `/root/rag-lab/09-chroma/query_chroma.py`, used as `python query_chroma.py QUESTION [K]` (K defaults to 3):

1. It opens the `handbook` collection in `/root/rag-lab/09-chroma/db` with the `lab-embed` embedding function.
2. It queries with the question **text**.
3. It prints the top K, one per line: similarity (1 - distance) with 4 decimals, two spaces, chunk ID, two spaces, the `source` metadata, two spaces, the first 40 characters of the text with newlines replaced by spaces.

```bash
python query_chroma.py "Can I work from another country?" > /root/answers/09-results.txt
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `res = collection.query(query_texts=[question], n_results=k)` and then `res["ids"][0]`, `res["distances"][0]` ...
- Similarity is `1 - distance` for the cosine space.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-lab/09-chroma
cat > query_chroma.py <<'EOF'
import os
import sys

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

if len(sys.argv) < 2:
    print("usage: query_chroma.py QUESTION [K]", file=sys.stderr)
    sys.exit(2)
k = int(sys.argv[2]) if len(sys.argv) > 2 else 3
embed = OpenAIEmbeddingFunction(
    api_key_env_var="OPENAI_API_KEY", api_base=os.environ["OPENAI_BASE_URL"], model_name="lab-embed"
)
collection = chromadb.PersistentClient(path="/root/rag-lab/09-chroma/db").get_collection("handbook", embedding_function=embed)
res = collection.query(query_texts=[sys.argv[1]], n_results=k)
for cid, dist, doc, meta in zip(res["ids"][0], res["distances"][0], res["documents"][0], res["metadatas"][0]):
    print(f"{1 - dist:.4f}  {cid}  {meta['source']}  {doc[:40].replace(chr(10), ' ')}")
EOF
python query_chroma.py "Can I work from another country?" > /root/answers/09-results.txt
cat /root/answers/09-results.txt
```

</details>

## Check your work

```bash
D=/root/rag-lab/09-chroma; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/query_chroma.py 2>/dev/null && [ -s $D/query_chroma.py ] && echo "✅ query_chroma.py reads the key from the environment" || echo "❌ query_chroma.py must not contain a key - let the SDK read it from the environment"
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
chunks = {c["id"]: c["text"] for c in load("chunks.json") or []}
vecs = dict(zip(chunks, E(list(chunks.values())))) if chunks else {}
def expect(q, k):
    qv = E([q])[0]
    return sorted(((cos(qv, v), cid) for cid, v in vecs.items()), reverse=True)[:k]
def parse(out):
    res = []
    for line in out.splitlines():
        p = line.split("  ")
        try:
            res.append((float(p[0]), p[1].strip(), p[2].strip()))
        except (ValueError, IndexError):
            pass
    return res
saved = parse(Path("/root/answers/09-results.txt").read_text()) if Path("/root/answers/09-results.txt").exists() else []
ok(len(saved) == 3 and saved[0][1] == "handbook-001" and all(s[2] == "handbook.md" for s in saved), "09-results.txt has 3 hits with sources, handbook-001 first", "/root/answers/09-results.txt should list 3 hits as 'score  id  source  text', with handbook-001 first")
for q, k in [("What is the meal allowance when I travel?", "2"), ("When are core hours?", None)]:
    want = expect(q, int(k or 3))
    rc, out, err = run("query_chroma.py", q, *([k] if k else []))
    got = parse(out)
    ok(rc == 0 and [g[1] for g in got] == [c for _, c in want], f"'{q}' K={k or 'default'} -> {[c for _, c in want]}", f"'{q}' K={k or 'default'} should list {[c for _, c in want]} - got {[g[1] for g in got]} {err[-150:]}")
    ok(got and all(abs(g[0] - s) < 0.005 for g, (s, _) in zip(got, want)), "scores are 1 - distance (cosine similarity)", "print 1 - distance as the score")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- `collection.query(query_texts=[...], n_results=k)` embeds the question and returns lists per question.
- For the cosine space, similarity = 1 - distance.
- Metadata travels with every hit - the basis for showing sources and filtering.
