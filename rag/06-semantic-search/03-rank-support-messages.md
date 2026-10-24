---
type: task
title: "Rank support messages"
minutes: 13
---

## Scenario

Northwind support gets hundreds of messages a day. Before building an assistant, the team wants a tool that finds the past messages most like a new one.

## Set up

```bash
ailab status
mkdir -p /root/rag-lab/06-search /root/answers
cd /root/rag-lab/06-search
cat > messages.txt <<'EOF'
I can't log in to my account, it keeps saying my password is wrong.
You charged my credit card twice for the same order.
How do I change the email address on my profile?
The mobile app crashes every time I open the camera.
Can I get a refund for a subscription I forgot to cancel?
My package was marked delivered but it never arrived.
Is there a dark mode in the desktop app?
The website is extremely slow this morning.
I'd like to delete my account and all my data.
Where can I download my invoices for last year?
EOF
wc -l messages.txt
```

## What to build

`messages.txt` holds 10 support messages, one per line. Write `/root/rag-lab/06-search/search.py`, used as `python search.py QUERY...`:

1. It reads the messages and embeds them **plus the query in a single `lab-embed` call**.
2. It scores every message against the query with cosine similarity.
3. It prints the **top 3**, best first, one per line, as the score with 4 decimals, two spaces, then the message:

   ```text
   0.6123  You charged my credit card twice for the same order.
   ```

Save one search:

```bash
python search.py "I was billed two times for one purchase" > /root/answers/06-top3.txt
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `messages = [l.strip() for l in open("messages.txt") if l.strip()]`.
- Embed `messages + [query]`, then `vectors[:-1]` and `vectors[-1]`.
- `print(f"{score:.4f}  {text}")`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-lab/06-search
cat > search.py <<'EOF'
import math
import sys

from openai import OpenAI

client = OpenAI()


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


if len(sys.argv) < 2:
    print("usage: search.py QUERY", file=sys.stderr)
    sys.exit(2)
query = " ".join(sys.argv[1:])
messages = [line.strip() for line in open("messages.txt") if line.strip()]
vectors = [d.embedding for d in client.embeddings.create(model="lab-embed", input=messages + [query]).data]
scored = sorted(zip((cosine(vectors[-1], v) for v in vectors[:-1]), messages), reverse=True)
for score, text in scored[:3]:
    print(f"{score:.4f}  {text}")
EOF
python search.py "I was billed two times for one purchase" > /root/answers/06-top3.txt
cat /root/answers/06-top3.txt
```

</details>

## Check your work

```bash
D=/root/rag-lab/06-search; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/search.py 2>/dev/null && [ -s $D/search.py ] && echo "✅ search.py reads the key from the environment" || echo "❌ search.py must not contain a key - let the SDK read it from the environment"
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
msgs = [l.strip() for l in open("messages.txt") if l.strip()]
vecs = E(msgs)
def expect(q):
    qv = E([q])[0]
    return sorted(zip((cos(qv, v) for v in vecs), msgs), reverse=True)[:3]
def parse(out):
    rows = []
    for line in out.splitlines():
        score, _, text = line.partition("  ")
        try:
            rows.append((float(score), text.strip()))
        except ValueError:
            pass
    return rows
saved = parse(Path("/root/answers/06-top3.txt").read_text()) if Path("/root/answers/06-top3.txt").exists() else []
ok(len(saved) == 3 and saved[0][1] == "You charged my credit card twice for the same order.", "06-top3.txt has 3 results, double charge first", "/root/answers/06-top3.txt should hold 3 lines 'score  message', with the double-charge message first")
for q in ["the app keeps dying when I take a photo", "I never received my parcel"]:
    want = expect(q)
    before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
    rc, out, err = run("search.py", *q.split())
    rows = parse(out)
    new = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
    emb = [r for r in new if r.get("api") == "embeddings"]
    ok(rc == 0 and [t for _, t in rows] == [t for _, t in want], f"'{q}' -> the right top 3 in order", f"'{q}' should rank: {[t for _, t in want]} - got {[t for _, t in rows]} {err[-150:]}")
    ok(len(rows) == 3 and all(abs(a[0] - b[0]) < 0.001 for a, b in zip(rows, want)), "scores are cosine similarities with 4 decimals", "the printed scores don't match cosine similarity")
    ok(len(emb) == 1 and emb[0].get("inputs") == 11, "messages and query embedded in one call", f"embed messages + query in ONE lab-embed call (saw {len(emb)} calls)")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Semantic search = embed candidates once, embed the query, score, sort, keep top k.
- It finds matches that share meaning but no words; keywords still win for exact IDs.
- Batch the query with the candidates to save requests.
