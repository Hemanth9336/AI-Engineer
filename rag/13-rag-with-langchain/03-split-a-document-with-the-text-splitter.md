---
type: task
title: "Split a document with the text splitter"
minutes: 10
---

## Set up

```bash
ailab status
mkdir -p /root/rag-lab/13-langchain
cd /root/rag-lab/13-langchain
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
python -c "import langchain_text_splitters, langchain_chroma, langchain_openai; print('langchain ready')"
```

## What to build

Write `/root/rag-lab/13-langchain/split.py` that:

1. Splits `handbook.md` with `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)`, attaching the metadata `{"source": "handbook.md"}`.
2. Writes `splits.json`: a list of `{"id", "source", "text"}` with IDs `handbook-000`, `handbook-001`, ...
3. Prints the number of splits and their lengths.

```bash
python split.py
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `splitter.create_documents([text], metadatas=[{"source": "handbook.md"}])`.
- Each `Document` has `.page_content` and `.metadata`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-lab/13-langchain
cat > split.py <<'EOF'
import json

from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
docs = splitter.create_documents([open("handbook.md").read()], metadatas=[{"source": "handbook.md"}])
splits = [{"id": f"handbook-{i:03d}", "source": d.metadata["source"], "text": d.page_content} for i, d in enumerate(docs)]
json.dump(splits, open("splits.json", "w"), indent=2)
print(len(splits), "splits", [len(s["text"]) for s in splits])
EOF
python split.py
```

</details>

## Check your work

```bash
D=/root/rag-lab/13-langchain; cd $D 2>/dev/null || echo "❌ create $D"
grep -q 'RecursiveCharacterTextSplitter' split.py 2>/dev/null && echo "✅ split.py uses RecursiveCharacterTextSplitter" || echo "❌ use RecursiveCharacterTextSplitter in split.py"
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
from langchain_text_splitters import RecursiveCharacterTextSplitter
want = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100).split_text(Path("handbook.md").read_text())
got = load("splits.json") or []
ok([s.get("text") for s in got] == want, f"splits.json holds the {len(want)} recursive splits", f"splits.json should hold the {len(want)} splits from RecursiveCharacterTextSplitter(500, 100)")
ok(got and [s.get("id") for s in got] == [f"handbook-{i:03d}" for i in range(len(got))] and all(s.get("source") == "handbook.md" for s in got), "IDs are handbook-000 ... and every split has source handbook.md", "each split needs id handbook-NNN and source handbook.md")
ok(got and all(s["text"].startswith("#") for s in got), "every split starts at a heading", "the splits should start at headings - check chunk_size and chunk_overlap")
PYEOF
```

## What you learned

- LangChain splitters return `Document`s: page_content plus metadata.
- The recursive splitter cuts at paragraphs, then lines, then words - structure-aware chunks.
- Better chunks give sharper vectors and higher scores for matching questions.
