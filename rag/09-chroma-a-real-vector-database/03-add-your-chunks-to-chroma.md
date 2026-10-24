---
type: task
title: "Add your chunks to Chroma"
minutes: 12
---

## Set up

Set up gives you `handbook.md` and `chunks.json` - the same 5 chunks from topic 07.

```bash
ailab status
mkdir -p /root/rag-lab/09-chroma
cd /root/rag-lab/09-chroma
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
python -c "import chromadb; print('chromadb', chromadb.__version__)"
```

## What to build

Write `/root/rag-lab/09-chroma/load_chroma.py` that:

1. Opens a persistent Chroma client at `/root/rag-lab/09-chroma/db`.
2. Gets or creates a collection named `handbook` with the **cosine** space, using `lab-embed` through the gateway as its embedding function (key read from the environment).
3. Upserts every chunk from `chunks.json` - ID, text, and metadata `{"source": "handbook.md", "index": N}`.
4. Prints the collection count.

Running it twice must still leave exactly 5 chunks.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `OpenAIEmbeddingFunction(api_key_env_var="OPENAI_API_KEY", api_base=os.environ["OPENAI_BASE_URL"], model_name="lab-embed")`.
- `configuration={"hnsw": {"space": "cosine"}}` in `get_or_create_collection`.
- Made the collection with the wrong space? `rm -rf db` and run again.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-lab/09-chroma
cat > load_chroma.py <<'EOF'
import json
import os

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

embed = OpenAIEmbeddingFunction(
    api_key_env_var="OPENAI_API_KEY",
    api_base=os.environ["OPENAI_BASE_URL"],
    model_name="lab-embed",
)
client = chromadb.PersistentClient(path="/root/rag-lab/09-chroma/db")
collection = client.get_or_create_collection(
    "handbook", embedding_function=embed, configuration={"hnsw": {"space": "cosine"}}
)
chunks = json.load(open("/root/rag-lab/09-chroma/chunks.json"))
collection.upsert(
    ids=[c["id"] for c in chunks],
    documents=[c["text"] for c in chunks],
    metadatas=[{"source": "handbook.md", "index": c["index"]} for c in chunks],
)
print(collection.count(), "chunks in", collection.name)
EOF
python load_chroma.py
python load_chroma.py
```

</details>

## Check your work

```bash
D=/root/rag-lab/09-chroma; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/load_chroma.py 2>/dev/null && [ -s $D/load_chroma.py ] && echo "✅ load_chroma.py reads the key from the environment" || echo "❌ load_chroma.py must not contain a key - let the SDK read it from the environment"
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
import chromadb
chunks = load("chunks.json") or []
def col():
    return chromadb.PersistentClient(path="/root/rag-lab/09-chroma/db").get_collection("handbook")
try:
    c = col()
except Exception as e:
    c = None
    print(f"❌ no collection named handbook in /root/rag-lab/09-chroma/db ({e})")
if c:
    ok(c.count() == len(chunks) == 5, "the handbook collection holds 5 chunks", f"the collection should hold {len(chunks)} chunks (has {c.count()})")
    ok((c.configuration.get("hnsw") or {}).get("space") == "cosine", "the collection uses the cosine space", "create the collection with configuration={'hnsw': {'space': 'cosine'}} (rm -rf db first)")
    got = c.get(ids=[ch["id"] for ch in chunks], include=["documents", "metadatas", "embeddings"])
    by = {i: (d, m, e) for i, d, m, e in zip(got["ids"], got["documents"], got["metadatas"], got["embeddings"])}
    ok(all(i in by and by[i][0] == ch["text"] for i, ch in zip([ch["id"] for ch in chunks], chunks)), "IDs and texts match chunks.json", "upsert each chunk with its id and text from chunks.json")
    ok(all(by.get(ch["id"], (0, {}, 0))[1] == {"source": "handbook.md", "index": ch["index"]} for ch in chunks), "every chunk has source and index metadata", "each chunk needs metadata {'source': 'handbook.md', 'index': N}")
    if by:
        e0 = list(by.get("handbook-003", (0, 0, []))[2])
        ok(len(e0) == 384 and cos(e0, E([chunks[3]["text"]])[0]) > 0.999, "Chroma embedded the chunks with lab-embed", "the stored vectors aren't lab-embed vectors - pass the OpenAIEmbeddingFunction for lab-embed")
rc, out, err = run("load_chroma.py")
ok(rc == 0 and col().count() == len(chunks), "running load_chroma.py again keeps 5 chunks", f"running load_chroma.py again should keep {len(chunks)} chunks {err[-150:]}")
PYEOF
jq -se 'any(.[]; .ok and .api == "embeddings" and .model == "lab-embed" and (.client | startswith("OpenAI/Python")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ Chroma called lab-embed through the gateway" || echo "❌ the gateway has no lab-embed call from Chroma"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Chroma: a PersistentClient holds collections of ids, documents, metadatas and vectors.
- OpenAIEmbeddingFunction points Chroma at any OpenAI-compatible endpoint, like the gateway.
- Set the cosine space when the collection is created; upsert keeps re-runs idempotent.
