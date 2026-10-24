---
type: task
title: "Build the store"
minutes: 12
---

## Set up

Set up gives you `handbook.md`, `chunks.json` and `vectors.json` - the same 5 chunks and vectors you made in topic 07.

```bash
ailab status
mkdir -p /root/rag-lab/08-vector-store
cd /root/rag-lab/08-vector-store
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
python - <<'EOF'
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
python - <<'EOF'
import json
from openai import OpenAI
chunks = json.load(open("chunks.json"))
resp = OpenAI().embeddings.create(model="lab-embed", input=[c["text"] for c in chunks])
json.dump([{"id": c["id"], "text": c["text"], "embedding": d.embedding} for c, d in zip(chunks, resp.data)], open("vectors.json", "w"))
print(len(chunks), "vectors written to vectors.json")
EOF
```

## What to build

Write `/root/rag-lab/08-vector-store/build_store.py` that:

1. Creates `store.db` with a table `chunks (id TEXT PRIMARY KEY, text TEXT, embedding TEXT)` if it doesn't exist.
2. Upserts every record from `vectors.json`, storing the embedding as JSON text.
3. Prints how many chunks the table now holds.

It must be **idempotent**: running it twice leaves exactly 5 rows.

```bash
python build_store.py
python build_store.py
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `INSERT OR REPLACE INTO chunks (id, text, embedding) VALUES (?, ?, ?)`.
- Don't forget `db.commit()`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-lab/08-vector-store
cat > build_store.py <<'EOF'
import json
import sqlite3

db = sqlite3.connect("store.db")
db.execute("CREATE TABLE IF NOT EXISTS chunks (id TEXT PRIMARY KEY, text TEXT, embedding TEXT)")
records = json.load(open("vectors.json"))
db.executemany(
    "INSERT OR REPLACE INTO chunks (id, text, embedding) VALUES (?, ?, ?)",
    [(r["id"], r["text"], json.dumps(r["embedding"])) for r in records],
)
db.commit()
print(db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0], "chunks stored")
EOF
python build_store.py
python build_store.py
```

</details>

## Check your work

```bash
D=/root/rag-lab/08-vector-store; cd $D 2>/dev/null || echo "❌ create $D"
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
def rows():
    db = sqlite3.connect("store.db")
    try:
        return db.execute("SELECT id, text, embedding FROM chunks ORDER BY id").fetchall()
    finally:
        db.close()
vecs = load("vectors.json") or []
try:
    got = rows()
except Exception as e:
    got = []
    print(f"❌ store.db needs a table chunks(id, text, embedding): {e}")
ok(len(got) == len(vecs) == 5 and [r[0] for r in got] == [v["id"] for v in vecs], "store.db holds the 5 chunks", f"store.db should hold the {len(vecs)} chunks from vectors.json (has {len(got)})")
ok(got and all(r[1] == v["text"] and json.loads(r[2]) == v["embedding"] for r, v in zip(got, vecs)), "text and JSON embeddings match vectors.json", "store the text and the embedding as JSON text, unchanged")
db = sqlite3.connect("store.db")
pk = [c for c in db.execute("PRAGMA table_info(chunks)") if c[1] == "id"]
db.close()
ok(pk and pk[0][5] == 1, "id is the primary key", "make id the PRIMARY KEY so IDs can't repeat")
rc, out, err = run("build_store.py")
rc2, out2, err2 = run("build_store.py")
ok(rc == rc2 == 0 and len(rows()) == len(vecs), "running build_store.py again keeps 5 rows - idempotent", f"running build_store.py twice more should still leave {len(vecs)} rows {err2[-150:]}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A vector store keeps id, text, embedding (and metadata) and answers top-k queries.
- `INSERT OR REPLACE` with an ID primary key is an upsert - re-runs don't duplicate.
- Indexing jobs must be idempotent.
