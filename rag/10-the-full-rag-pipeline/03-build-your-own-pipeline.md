---
type: task
title: "Build your own pipeline"
minutes: 17
---

## Scenario

The Northwind ops team keeps short markdown docs about deploys, on-call, backups and access. Build the first version of their docs assistant - entirely by hand, with the pieces you've already written.

## Set up

```bash
ailab status
mkdir -p /root/rag-lab/10-pipeline /root/answers
cd /root/rag-lab/10-pipeline
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
ls docs
```

## What to build

Write `/root/rag-lab/10-pipeline/rag.py` with two commands:

- `python rag.py index` chunks every `docs/*.md` file (500/100), embeds all chunks with `lab-embed` in one call, and upserts them into `store.db` - a table `chunks (id TEXT PRIMARY KEY, source TEXT, text TEXT, embedding TEXT)`, where `source` is the file name (for example `deploys.md`). Re-running it must not duplicate rows.
- `python rag.py ask QUESTION...` retrieves the top **2** chunks, sends them in `<document source="...">` tags with the grounding rules to `lab-fast` at `temperature=0`, and prints the answer, a blank line, and `Sources: ` followed by the retrieved source files, comma-separated, in rank order with no repeats. If the model refuses, it prints exactly `I don't know based on the documents.` and **no** sources line.

Then:

```bash
python rag.py index
python rag.py ask "How do I roll back a bad release?" > /root/answers/10-rollback.txt
python rag.py ask "What is the office wifi password?" > /root/answers/10-wifi.txt
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Reuse `chunk_text` from topic 07, the SQLite upsert from topic 08 and the grounded prompt from topic 03.
- `list(dict.fromkeys(sources))` removes repeats and keeps the order.
- Compare the refusal loosely, then print the exact sentence yourself.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-lab/10-pipeline
cat > rag.py <<'EOF'
import json
import math
import sqlite3
import sys
from pathlib import Path

from openai import OpenAI

REFUSAL = "I don't know based on the documents."
client = OpenAI()
db = sqlite3.connect("store.db")
db.execute("CREATE TABLE IF NOT EXISTS chunks (id TEXT PRIMARY KEY, source TEXT, text TEXT, embedding TEXT)")


def chunk_text(text, size=500, overlap=100):
    chunks, start = [], 0
    while True:
        chunks.append(text[start:start + size])
        if start + size >= len(text):
            return chunks
        start += size - overlap


def embed(texts):
    return [d.embedding for d in client.embeddings.create(model="lab-embed", input=texts).data]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def index(folder="docs"):
    records = []
    for path in sorted(Path(folder).glob("*.md")):
        for i, text in enumerate(chunk_text(path.read_text())):
            records.append((f"{path.stem}-{i:03d}", path.name, text))
    vectors = embed([text for _, _, text in records])
    db.executemany(
        "INSERT OR REPLACE INTO chunks (id, source, text, embedding) VALUES (?, ?, ?, ?)",
        [(cid, src, text, json.dumps(v)) for (cid, src, text), v in zip(records, vectors)],
    )
    db.commit()
    return len(records)


def retrieve(question, k=2):
    qv = embed([question])[0]
    rows = db.execute("SELECT source, text, embedding FROM chunks").fetchall()
    return sorted(((cosine(qv, json.loads(e)), src, text) for src, text, e in rows), reverse=True)[:k]


def answer(question, k=2):
    hits = retrieve(question, k)
    context = "\n\n".join(f'<document source="{src}">\n{text}\n</document>' for _, src, text in hits)
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
        return REFUSAL, []
    return text, list(dict.fromkeys(src for _, src, _ in hits))


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "index":
        print(f"indexed {index()} chunks")
    elif len(sys.argv) >= 3 and sys.argv[1] == "ask":
        text, sources = answer(" ".join(sys.argv[2:]))
        print(text)
        if sources:
            print()
            print("Sources: " + ", ".join(sources))
    else:
        print("usage: rag.py index | rag.py ask QUESTION", file=sys.stderr)
        sys.exit(2)
EOF
python rag.py index
python rag.py ask "How do I roll back a bad release?" > /root/answers/10-rollback.txt
python rag.py ask "What is the office wifi password?" > /root/answers/10-wifi.txt
cat /root/answers/10-rollback.txt /root/answers/10-wifi.txt
```

</details>

## Check your work

```bash
D=/root/rag-lab/10-pipeline; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/rag.py 2>/dev/null && [ -s $D/rag.py ] && echo "✅ rag.py reads the key from the environment" || echo "❌ rag.py must not contain a key - let the SDK read it from the environment"
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
REFUSAL = "I don't know based on the documents."
def rows():
    try:
        return sqlite3.connect("store.db").execute("SELECT id, source, text FROM chunks").fetchall()
    except Exception:
        return []
r = rows()
ok(len(r) == 4 and sorted(x[1] for x in r) == ["access.md", "backups.md", "deploys.md", "oncall.md"], "store.db holds the 4 doc chunks with their sources", f"store.db should hold one chunk per doc (4) with source = the file name - has {len(r)}")
rc, out, err = run("rag.py", "index")
ok(rc == 0 and len(rows()) == 4, "re-indexing keeps 4 rows", f"python rag.py index again should keep 4 rows {err[-150:]}")
def parts(out):
    body, _, src = out.rpartition("Sources:")
    return (body.strip(), [s.strip() for s in src.split(",")]) if _ else (out.strip(), [])
a, s = parts(Path("/root/answers/10-rollback.txt").read_text() if Path("/root/answers/10-rollback.txt").exists() else "")
ok("shipit rollback" in a and s and s[0] == "deploys.md", "10-rollback.txt answers with shipit rollback, deploys.md first in Sources", "/root/answers/10-rollback.txt should answer from deploys.md and end with 'Sources: deploys.md, ...'")
ok(Path("/root/answers/10-wifi.txt").exists() and Path("/root/answers/10-wifi.txt").read_text().strip() == REFUSAL, "10-wifi.txt is exactly the refusal, no sources", f"/root/answers/10-wifi.txt should be exactly: {REFUSAL}")
for q, want, src in [("When does the on-call rotation change?", "Monday", "oncall.md"), ("Who approves production access requests?", "team lead", "access.md")]:
    rc, out, err = run("rag.py", "ask", q)
    a, s = parts(out)
    ok(rc == 0 and want.lower() in a.lower() and s[:1] == [src] and len(s) == len(set(s)) <= 2, f"'{q}' -> answered from {src}", f"'{q}' should be answered from {src} with 'Sources: {src}, ...' - got {out[-200:]!r} {err[-150:]}")
rc, out, err = run("rag.py", "ask", "Which band is playing at the summer party?")
ok(rc == 0 and out.strip() == REFUSAL, "an unanswerable question gets exactly the refusal and no sources", f"'Which band is playing at the summer party?' should print only: {REFUSAL} - got {out[-200:]!r}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and .temperature == 0 and .system and (.client | startswith("OpenAI/Python")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged a grounded lab-fast call at temperature 0" || echo "❌ the gateway has no lab-fast call at temperature 0 with a system message from your script"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- RAG = index (chunk, embed, store) + retrieve (embed question, top k) + generate (grounded prompt).
- Label each chunk with its source and show sources under the answer.
- Refusals carry no sources; index and ask are separate commands.
