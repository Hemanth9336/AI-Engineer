---
type: task
title: "Query the store"
minutes: 12
---

## Set up

```bash
ailab status
mkdir -p /root/rag-lab/08-vector-store /root/answers
cd /root/rag-lab/08-vector-store
[ -f store.db ] || { echo "store.db is missing - finish the previous task first"; false; }
```

## What to build

Write `/root/rag-lab/08-vector-store/query_store.py`, used as `python query_store.py QUESTION [K]` (K defaults to 3):

1. It embeds **only the question** with `lab-embed` (chunk vectors come from `store.db`).
2. It scores every stored chunk with cosine similarity.
3. It prints the top K, best first, one per line: score with 4 decimals, two spaces, chunk ID, two spaces, the first 60 characters of the text with newlines replaced by spaces.

```bash
python query_store.py "What should I do if my laptop is stolen?" > /root/answers/08-results.txt
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `json.loads(row[2])` turns the stored text back into a list.
- Read K with `int(sys.argv[2]) if len(sys.argv) > 2 else 3`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-lab/08-vector-store
cat > query_store.py <<'EOF'
import json
import math
import sqlite3
import sys

from openai import OpenAI

client = OpenAI()


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def search(question, k=3):
    qv = client.embeddings.create(model="lab-embed", input=question).data[0].embedding
    rows = sqlite3.connect("store.db").execute("SELECT id, text, embedding FROM chunks").fetchall()
    scored = [(cosine(qv, json.loads(emb)), cid, text) for cid, text, emb in rows]
    return sorted(scored, reverse=True)[:k]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: query_store.py QUESTION [K]", file=sys.stderr)
        sys.exit(2)
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    for score, cid, text in search(sys.argv[1], k):
        print(f"{score:.4f}  {cid}  {text[:60].replace(chr(10), ' ')}")
EOF
python query_store.py "What should I do if my laptop is stolen?" > /root/answers/08-results.txt
cat /root/answers/08-results.txt
```

</details>

## Check your work

```bash
D=/root/rag-lab/08-vector-store; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/query_store.py 2>/dev/null && [ -s $D/query_store.py ] && echo "✅ query_store.py reads the key from the environment" || echo "❌ query_store.py must not contain a key - let the SDK read it from the environment"
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
import sqlite3
stored = [(cid, json.loads(e)) for cid, e in sqlite3.connect("store.db").execute("SELECT id, embedding FROM chunks")]
def expect(q, k):
    qv = E([q])[0]
    return sorted(((cos(qv, v), cid) for cid, v in stored), reverse=True)[:k]
def parse(out):
    res = []
    for line in out.splitlines():
        parts = line.split("  ")
        try:
            res.append((float(parts[0]), parts[1].strip()))
        except (ValueError, IndexError):
            pass
    return res
saved = parse(Path("/root/answers/08-results.txt").read_text()) if Path("/root/answers/08-results.txt").exists() else []
ok(len(saved) == 3 and saved[0][1] == "handbook-003", "08-results.txt has 3 hits, handbook-003 first", "/root/answers/08-results.txt should list 3 hits with handbook-003 (the laptop rules) first")
for q, k in [("What is the meal allowance when I travel?", "2"), ("When are core hours?", None)]:
    want = expect(q, int(k or 3))
    before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
    rc, out, err = run("query_store.py", q, *([k] if k else []))
    new = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
    got = parse(out)
    ok(rc == 0 and [c for _, c in got] == [c for _, c in want] and all(abs(a - b) < 0.001 for (a, _), (b, _) in zip(got, want)), f"'{q}' K={k or 'default'} -> {[c for _, c in want]}", f"'{q}' K={k or 'default'} should print {[c for _, c in want]} with their scores - got {[c for _, c in got]} {err[-150:]}")
    ok(sum(r.get("inputs", 0) for r in new if r.get("api") == "embeddings") == 1, "only the question was embedded", "query_store.py should embed only the question - chunk vectors come from store.db")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Querying embeds only the question; stored vectors are reused.
- A flat search compares against every vector - fine for thousands, slow for millions.
- Real vector databases add approximate indexes like HNSW for speed.
