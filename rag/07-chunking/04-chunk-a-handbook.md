---
type: task
title: "Chunk a handbook"
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
wc -c handbook.md
```

## What to build

Write `/root/rag-lab/07-chunking/chunk.py`:

1. A function `chunk_text(text, size=500, overlap=100)` that returns a list of character windows: they start at 0 and step by `size - overlap`, and the last chunk reaches the end of the text. `chunk_text("abcdefghij", 4, 1)` must return `["abcd", "defg", "ghij"]`.
2. When run as `python chunk.py FILE SIZE OVERLAP`, it writes `chunks.json` in the current folder: a list of `{"id", "index", "text"}`, where `id` is the file name without its extension plus a 3-digit index (`handbook-000`, `handbook-001`, ...).
3. Importing it must not run the command-line part.

Then run:

```bash
python chunk.py handbook.md 500 100
```

The checker also runs your chunker on a different file and different sizes.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Loop: append `text[start:start + size]`; stop when `start + size >= len(text)`; otherwise `start += size - overlap`.
- `Path(sys.argv[1]).stem` gives `handbook` from `handbook.md`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-lab/07-chunking
cat > chunk.py <<'EOF'
import json
import sys
from pathlib import Path


def chunk_text(text, size=500, overlap=100):
    chunks, start = [], 0
    while True:
        chunks.append(text[start:start + size])
        if start + size >= len(text):
            return chunks
        start += size - overlap


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("usage: chunk.py FILE SIZE OVERLAP", file=sys.stderr)
        sys.exit(2)
    path, size, overlap = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    chunks = chunk_text(path.read_text(), size, overlap)
    records = [{"id": f"{path.stem}-{i:03d}", "index": i, "text": c} for i, c in enumerate(chunks)]
    Path("chunks.json").write_text(json.dumps(records, indent=2))
    print(f"{len(records)} chunks written to chunks.json")
EOF
python chunk.py handbook.md 500 100
```

</details>

## Check your work

```bash
D=/root/rag-lab/07-chunking; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/chunk.py 2>/dev/null && [ -s $D/chunk.py ] && echo "✅ chunk.py reads the key from the environment" || echo "❌ chunk.py must not contain a key - let the SDK read it from the environment"
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
import importlib, shutil, tempfile
m = importlib.import_module("chunk")
ct = m.chunk_text
ok(ct("abcdefghij", 4, 1) == ["abcd", "defg", "ghij"], "chunk_text('abcdefghij', 4, 1) is right", f"chunk_text('abcdefghij', 4, 1) should be ['abcd', 'defg', 'ghij'], got {ct('abcdefghij', 4, 1)}")
ok(ct("short", 500, 100) == ["short"], "short text gives one chunk", "chunk_text('short', 500, 100) should be ['short']")
ok(ct("abcdefghijk", 4, 0) == ["abcd", "efgh", "ijk"], "overlap 0 and a short last chunk work", "chunk_text('abcdefghijk', 4, 0) should be ['abcd', 'efgh', 'ijk']")
text = Path("handbook.md").read_text()
want = ct(text, 500, 100)
got = load("chunks.json") or []
ok(len(got) == 5 and [c.get("text") for c in got] == want, "chunks.json holds the 5 handbook chunks", f"chunks.json should hold the {len(want)} chunks of handbook.md at 500/100")
ok([c.get("id") for c in got] == [f"handbook-{i:03d}" for i in range(len(got))] and [c.get("index") for c in got] == list(range(len(got))), "IDs are handbook-000 ... with matching index", "each chunk needs id handbook-000, handbook-001, ... and index 0, 1, ...")
ok(all(want[i][-100:] == want[i + 1][:100] for i in range(len(want) - 1)), "neighbouring chunks overlap by 100 characters", "neighbouring chunks should share 100 characters")
tmp = Path(tempfile.mkdtemp())
shutil.copy("chunk.py", tmp)
(tmp / "notes.txt").write_text("0123456789" * 7)
rc, out, err = run("chunk.py", "notes.txt", "30", "10", cwd=tmp)
other = load(tmp / "chunks.json") or []
ok(rc == 0 and [c.get("id") for c in other] == ["notes-000", "notes-001", "notes-002"] and [len(c["text"]) for c in other] == [30, 30, 30], "the chunker works on a new file with new sizes", f"python chunk.py notes.txt 30 10 on a 70-character file should give notes-000..002 {err[-150:]}")
shutil.rmtree(tmp)
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Chunk = a small, focused piece; each gets its own embedding.
- Windows start every size - overlap characters; overlap keeps boundary facts whole.
- Every chunk gets a stable ID made of the source name and its position.
