---
type: task
title: "Build a tiny vector store in a JSON file"
minutes: 8
---

## Set up

```bash
mkdir -p /root/fde-lab/14-vectors
cd /root/fde-lab/14-vectors
cat > sentences.txt <<'EOF'
Reporting a damaged parcel. Report damage within 7 days of delivery through the claims page.
Changing a delivery address. You can change the delivery address until the parcel leaves the depot.
International shipping and customs. International parcels outside the EU need a commercial invoice.
Support hours. Customer support is open 8:00 to 18:00 CET, Monday to Friday.
Tracking a parcel. Enter the order id, for example MER-55120, on the tracking page.
Pallet weight limits. Standard pallets can weigh up to 800 kg and be up to 1.8 m high.
Dangerous goods. Lithium batteries, aerosols and flammable liquids are dangerous goods.
Invoices and payment terms. Business invoices are issued on the 1st of each month.
Missed delivery. If nobody is home, the driver leaves a card and tries again the next working day.
Scanner error codes. Error E-4417 on a handheld scanner means the label barcode is unreadable.
EOF
```

## What to build

Write `/root/fde-lab/14-vectors/index.py`, used as `python index.py INPUT_FILE STORE_FILE`:

1. Read the non-empty lines of INPUT_FILE (stripped).
2. Embed them all with `lab-embed` in **one** call.
3. Write STORE_FILE as a JSON list of `{"id": "s1", "text": ..., "embedding": [...]}`, numbering ids from `s1` in line order.
4. Print `indexed N records`.

```bash
cd /root/fde-lab/14-vectors
python index.py sentences.txt store.json
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `[{"id": f"s{i}", "text": t, "embedding": v} for i, (t, v) in enumerate(zip(lines, vectors), 1)]`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/14-vectors
cat > index.py <<'EOF'
import json
import sys

from openai import OpenAI

lines = [l.strip() for l in open(sys.argv[1]) if l.strip()]
vectors = [d.embedding for d in OpenAI().embeddings.create(model="lab-embed", input=lines).data]
records = [{"id": f"s{i}", "text": t, "embedding": v} for i, (t, v) in enumerate(zip(lines, vectors), 1)]
json.dump(records, open(sys.argv[2], "w"))
print(f"indexed {len(records)} records")
EOF
python index.py sentences.txt store.json
```

</details>

## Check your work

```bash
D=/root/fde-lab/14-vectors; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/index.py 2>/dev/null && [ -s $D/index.py ] && echo "✅ index.py reads the key from the environment" || echo "❌ index.py must not contain a key - let the SDK read it from the environment"
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
def verify(path, lines, label):
    s = load(path)
    good = isinstance(s, list) and [r.get("id") for r in s] == [f"s{i}" for i in range(1, len(lines) + 1)] and [r.get("text") for r in s] == lines
    ok(good, f"{label}: ids and texts are right", f"{label}: expected ids s1..s{len(lines)} with the stripped non-empty lines")
    if good:
        ref = E(lines)
        ok(all(len(r["embedding"]) == len(v) and cos(r["embedding"], v) > 0.999 for r, v in zip(s, ref)), f"{label}: embeddings are lab-embed vectors of the texts", f"{label}: each embedding should be the lab-embed vector of its text")
verify("store.json", [l.strip() for l in Path("sentences.txt").read_text().splitlines() if l.strip()], "store.json")
Path("/tmp/in2.txt").write_text("  Pallets up to 800 kg  \n\nCold chain at 2-8 C\nReturns within 30 days\n")
before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
rc, out, err = run("index.py", "/tmp/in2.txt", "/tmp/store2.json")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
ok(rc == 0 and out.strip() == "indexed 3 records", "a new file prints 'indexed 3 records'", f"expected 'indexed 3 records' - got {out!r} {err[-150:]}")
verify("/tmp/store2.json", ["Pallets up to 800 kg", "Cold chain at 2-8 C", "Returns within 30 days"], "new file")
ok(len([r for r in rows if r.get("api") == "embeddings"]) == 1, "all lines were embedded in one call", "embed every line in a single embeddings call")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A vector store is records of id, text, embedding and metadata.
- Embed at build time in batches; only the query is embedded at question time.
- Vector databases add scale, filters and updates - the concepts stay the same.
