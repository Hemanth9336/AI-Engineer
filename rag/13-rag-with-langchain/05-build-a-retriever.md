---
type: task
title: "Build a retriever"
minutes: 10
---

## Set up

```bash
ailab status
cd /root/rag-lab/13-langchain
[ -f splits.json ] || { echo "splits.json is missing - finish the previous task first"; false; }
```

## What to build

Write `/root/rag-lab/13-langchain/retriever.py`:

1. A LangChain `Chroma` store with collection `handbook`, persisted in `/root/rag-lab/13-langchain/db` (built from the file's own location), cosine space, and `OpenAIEmbeddings(model="lab-embed", check_embedding_ctx_length=False)`.
2. `build_store()` loads `splits.json` as `Document`s with `source` metadata, adds them with their IDs, and returns how many chunks the store holds. Re-running must not duplicate.
3. `get_retriever(k=3)` returns `store.as_retriever(...)` for k results.
4. Commands: `python retriever.py index` and `python retriever.py search QUESTION...` (prints `id  source  first 50 characters` per hit).

```bash
python retriever.py index
python retriever.py search "How much is the learning budget?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `HERE = Path(__file__).resolve().parent` and `persist_directory=str(HERE / "db")`.
- `len(store.get()["ids"])` counts the stored chunks.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-lab/13-langchain
cat > retriever.py <<'EOF'
import json
import sys
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

HERE = Path(__file__).resolve().parent
embeddings = OpenAIEmbeddings(model="lab-embed", check_embedding_ctx_length=False)
store = Chroma(
    collection_name="handbook",
    embedding_function=embeddings,
    persist_directory=str(HERE / "db"),
    collection_configuration={"hnsw": {"space": "cosine"}},
)


def build_store():
    splits = json.load(open(HERE / "splits.json"))
    docs = [Document(page_content=s["text"], metadata={"source": s["source"]}) for s in splits]
    store.add_documents(docs, ids=[s["id"] for s in splits])
    return len(store.get()["ids"])


def get_retriever(k=3):
    return store.as_retriever(search_kwargs={"k": k})


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "index":
        print(build_store(), "chunks in the handbook collection")
    elif len(sys.argv) >= 3 and sys.argv[1] == "search":
        for d in get_retriever().invoke(" ".join(sys.argv[2:])):
            print(f"{d.id}  {d.metadata['source']}  {d.page_content[:50].replace(chr(10), ' ')}")
    else:
        print("usage: retriever.py index | retriever.py search QUESTION", file=sys.stderr)
        sys.exit(2)
EOF
python retriever.py index
python retriever.py search "How much is the learning budget?"
```

</details>

## Check your work

```bash
D=/root/rag-lab/13-langchain; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/retriever.py 2>/dev/null && [ -s $D/retriever.py ] && echo "✅ retriever.py reads the key from the environment" || echo "❌ retriever.py must not contain a key - let the SDK read it from the environment"
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
os.chdir("/tmp")
sys.path.insert(0, "/root/rag-lab/13-langchain")
m = importlib.import_module("retriever")
n1, n2 = m.build_store(), m.build_store()
splits = load("/root/rag-lab/13-langchain/splits.json") or []
ok(n1 == n2 == len(splits) == 5, "build_store() returns 5 and re-runs don't duplicate", f"build_store() should return {len(splits)} both times - got {n1}, {n2}")
import chromadb
c = chromadb.PersistentClient(path="/root/rag-lab/13-langchain/db").get_collection("handbook")
ok((c.configuration.get("hnsw") or {}).get("space") == "cosine", "the collection uses the cosine space", "create the store with collection_configuration={'hnsw': {'space': 'cosine'}} (rm -rf db first)")
vec = dict(zip([s["id"] for s in splits], E([s["text"] for s in splits])))
for q, k in [("Can I work from another country?", 2), ("What is the meal allowance when I travel?", 3)]:
    qv = E([q])[0]
    want = [i for _, i in sorted(((cos(qv, v), i) for i, v in vec.items()), reverse=True)[:k]]
    docs = m.get_retriever(k=k).invoke(q)
    got = [d.id for d in docs]
    ok(got == want and all(d.metadata.get("source") == "handbook.md" for d in docs), f"get_retriever(k={k}) for '{q}' -> {want}", f"get_retriever(k={k}).invoke('{q}') should return {want} with source metadata - got {got}")
rc, out, err = run("/root/rag-lab/13-langchain/retriever.py", "search", "How much is the learning budget?")
ok(rc == 0 and out.splitlines()[:1] and out.splitlines()[0].startswith("handbook-003  handbook.md  "), "python retriever.py search prints id, source and text, best first", f"python retriever.py search 'How much is the learning budget?' should start with 'handbook-003  handbook.md  ...' - got {out[:120]!r} {err[-150:]}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- `Chroma(..., embedding_function=OpenAIEmbeddings(...))` is LangChain's wrapper over the same database.
- Set `check_embedding_ctx_length=False` for non-OpenAI embedding models.
- A retriever is a Runnable: question in, `Document`s out.
