---
type: task
title: "Embed your chunks"
minutes: 10
---

## Set up

```bash
ailab status
mkdir -p /root/rag-lab/07-chunking
cd /root/rag-lab/07-chunking
cat > handbook.md <<'EOF'
# Northwind Employee Handbook

## Working hours
Core hours are 10:00 to 16:00 in your local time zone. Outside core hours you can plan your own day, as long as your team knows when to reach you. Meetings should not be booked before 09:00 or after 17:00.

## Vacation
New employees get 20 vacation days per year, rising to 25 days after three years. Request leave in the HR portal at least two weeks ahead for anything longer than three days. Unused days can be carried over until 31 March of the next year.

## Sick leave
If you are sick, tell your manager before 10:00 on the first day. You do not need a doctor's note for absences of up to three days. Longer absences need a note from a doctor.

## Remote work
You can work from home whenever you like. Working from another country is allowed for up to 30 days per year, and you must tell HR before you travel so that tax and insurance stay correct.

## Expenses
Submit expenses within 30 days through the finance app, with a photo of every receipt. Meals while travelling are covered up to 60 euros per day. Anything above 500 euros needs approval from your manager before you spend it.

## Laptops and security
Every laptop must use full-disk encryption and lock after five minutes of inactivity. If your laptop is lost or stolen, report it to the IT service desk within one hour so it can be wiped remotely. Never store customer data on USB drives.

## Learning budget
Each employee has a learning budget of 1,000 euros per year for courses, books and conferences. Ask your manager before booking anything above 300 euros.

## Leaving the company
Give four weeks of notice in writing to your manager and HR. Return your laptop and badge on your last day.
EOF
[ -f chunks.json ] || python - <<'EOF'
import json
text = open("handbook.md").read()
chunks, start = [], 0
while True:
    chunks.append(text[start:start + 500])
    if start + 500 >= len(text):
        break
    start += 400
json.dump([{"id": f"handbook-{i:03d}", "index": i, "text": c} for i, c in enumerate(chunks)], open("chunks.json", "w"), indent=2)
print(len(chunks), "chunks written to chunks.json")
EOF
```

## What to build

Write `/root/rag-lab/07-chunking/embed_chunks.py` that:

1. Reads `chunks.json`.
2. Embeds all chunk texts with `lab-embed` in **one** call.
3. Writes `vectors.json`: a list of `{"id", "text", "embedding"}`, in the same order as the chunks.
4. Prints how many chunks it embedded.

```bash
python embed_chunks.py
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `input=[c["text"] for c in chunks]` - one call for all.
- `zip(chunks, resp.data)` pairs each chunk with its vector.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-lab/07-chunking
cat > embed_chunks.py <<'EOF'
import json

from openai import OpenAI

client = OpenAI()
chunks = json.load(open("chunks.json"))
resp = client.embeddings.create(model="lab-embed", input=[c["text"] for c in chunks])
records = [{"id": c["id"], "text": c["text"], "embedding": d.embedding} for c, d in zip(chunks, resp.data)]
json.dump(records, open("vectors.json", "w"))
print(f"{len(records)} chunks embedded")
EOF
python embed_chunks.py
```

</details>

## Check your work

```bash
D=/root/rag-lab/07-chunking; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/embed_chunks.py 2>/dev/null && [ -s $D/embed_chunks.py ] && echo "✅ embed_chunks.py reads the key from the environment" || echo "❌ embed_chunks.py must not contain a key - let the SDK read it from the environment"
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
chunks = load("chunks.json") or []
vecs = load("vectors.json") or []
ok(len(vecs) == len(chunks) > 0 and [v.get("id") for v in vecs] == [c["id"] for c in chunks] and [v.get("text") for v in vecs] == [c["text"] for c in chunks], "vectors.json has one record per chunk, in order", "vectors.json needs id and text for every chunk, in the same order as chunks.json")
ok(vecs and all(len(v.get("embedding") or []) == 384 for v in vecs), "every record has a 384-number embedding", "every record needs a 384-number embedding")
if vecs and len(vecs) == len(chunks):
    real = E([c["text"] for c in chunks])
    ok(all(cos(v["embedding"], r) > 0.999 for v, r in zip(vecs, real)), "each vector belongs to its own chunk", "a vector doesn't match its chunk - keep the order when pairing")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")]
ok(any(r.get("api") == "embeddings" and r.get("inputs") == len(chunks) and r.get("client", "").startswith("OpenAI/Python") for r in rows), "all chunks were embedded in one call", f"embed all {len(chunks)} chunks in ONE lab-embed call")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Embed all chunks in one batch call; results come back in input order.
- Indexing (chunk, embed, store) runs once; querying runs per question.
- Keep id, text and embedding together so a search hit can show its text.
