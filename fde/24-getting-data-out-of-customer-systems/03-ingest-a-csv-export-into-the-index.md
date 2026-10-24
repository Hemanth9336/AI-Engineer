---
type: task
title: "Ingest a CSV export into the index"
minutes: 7
---

## Set up

`kb_export.csv` is a help-center export: `id,title,body,status,updated_at`. It contains quoted commas, an archived row, an empty body and a duplicate id.

```bash
mkdir -p /root/fde-lab/24-data
cd /root/fde-lab/24-data
cat > kb_export.csv <<'EOF'
id,title,body,status,updated_at
kb-101,Damage claims,"Report damage within 7 days, with photos of the item and packaging.",published,2026-01-10
kb-102,Support hours,Support is open 8:00 to 18:00 CET.,published,2026-01-04
kb-103,Old pricing,Prices valid until 2024.,archived,2024-12-01
kb-104,Pallet limits,,published,2026-01-12
kb-102,Support hours,"Support is open 8:00 to 18:00 CET, Monday to Friday.",published,2026-02-01
kb-105,Cold chain,Chilled goods travel between 2 and 8 degrees.,published,2026-01-20
EOF
```

## What to build

Write `/root/fde-lab/24-data/ingest_csv.py`, used as `python ingest_csv.py CSV_FILE STORE_FILE`:

1. Parse with the `csv` module.
2. Keep only rows whose `status` is `published` (case-insensitive) and whose body isn't blank.
3. For duplicate ids keep the row with the latest `updated_at` (ISO dates compare as strings).
4. Records: `{"id", "text": "<title>. <body>", "source": "csv", "updated_at", "embedding"}`, sorted by id, embedded in **one** `lab-embed` call.
5. Print `ingested N, skipped M` - M counts every row not kept (filtered rows and older duplicates).

```bash
cd /root/fde-lab/24-data
python ingest_csv.py kb_export.csv store.json
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `csv.DictReader(open(path, newline=""))` handles quoted commas.
- Strip title and body before building the text.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/24-data
cat > ingest_csv.py <<'EOF'
import csv
import json
import sys

from openai import OpenAI

latest = {}
skipped = 0
with open(sys.argv[1], newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        body = (row.get("body") or "").strip()
        if row["status"].strip().lower() != "published" or not body:
            skipped += 1
            continue
        prev = latest.get(row["id"])
        if prev is None or row["updated_at"] > prev["updated_at"]:
            if prev is not None:
                skipped += 1
            latest[row["id"]] = {"id": row["id"], "text": f"{row['title'].strip()}. {body}", "source": "csv", "updated_at": row["updated_at"]}
        else:
            skipped += 1
records = sorted(latest.values(), key=lambda r: r["id"])
vectors = [d.embedding for d in OpenAI().embeddings.create(model="lab-embed", input=[r["text"] for r in records]).data] if records else []
for r, v in zip(records, vectors):
    r["embedding"] = v
json.dump(records, open(sys.argv[2], "w"))
print(f"ingested {len(records)}, skipped {skipped}")

EOF
python ingest_csv.py kb_export.csv store.json
```

</details>

## Check your work

```bash
D=/root/fde-lab/24-data; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/ingest_csv.py 2>/dev/null && [ -s $D/ingest_csv.py ] && echo "✅ ingest_csv.py reads the key from the environment" || echo "❌ ingest_csv.py must not contain a key - let the SDK read it from the environment"
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
import csv
def ref(path):
    latest, skipped = {}, 0
    for row in csv.DictReader(open(path, newline="", encoding="utf-8")):
        body = (row.get("body") or "").strip()
        if row["status"].strip().lower() != "published" or not body:
            skipped += 1
            continue
        prev = latest.get(row["id"])
        if prev is None or row["updated_at"] > prev["updated_at"]:
            skipped += prev is not None
            latest[row["id"]] = {"id": row["id"], "text": f"{row['title'].strip()}. {body}", "source": "csv", "updated_at": row["updated_at"]}
        else:
            skipped += 1
    return sorted(latest.values(), key=lambda r: r["id"]), skipped
def verify(store, csv_path, label, out=None):
    want, skipped = ref(csv_path)
    got = load(store) or []
    ok([{k: r.get(k) for k in ("id", "text", "source", "updated_at")} for r in got] == want, f"{label}: the right records, latest version of each, sorted by id", f"{label}: expected {[(r['id'], r['updated_at']) for r in want]} - got {[(r.get('id'), r.get('updated_at')) for r in got]}")
    if got and len(got) == len(want):
        ok(all(cos(r["embedding"], v) > 0.999 for r, v in zip(got, E([w["text"] for w in want]))), f"{label}: embeddings match the texts", f"{label}: each embedding should be the lab-embed vector of its text")
    if out is not None:
        ok(out == f"ingested {len(want)}, skipped {skipped}", f"{label}: prints 'ingested {len(want)}, skipped {skipped}'", f"{label}: expected 'ingested {len(want)}, skipped {skipped}' - got {out!r}")
verify("store.json", "kb_export.csv", "kb_export.csv")
  Path('/tmp/kb2.csv').write_text('id,title,body,status,updated_at\nx-1,Returns,"Returns are accepted for 30 days, with packaging.",published,2026-03-01\nx-2,Draft page,Not ready.,draft,2026-03-02\nx-1,Returns,Older returns text.,published,2026-02-01\nx-3,Fuel surcharge,Applies when the diesel index rises.,PUBLISHED,2026-03-05\nx-4,Empty,   ,published,2026-03-06\n')

before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
rc, out, err = run("ingest_csv.py", "/tmp/kb2.csv", "/tmp/store-csv2.json")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
verify("/tmp/store-csv2.json", "/tmp/kb2.csv", "a new export", out if rc == 0 else err[-200:])
ok(len([r for r in rows if r.get("api") == "embeddings"]) == 1, "the export was embedded in one call", "embed all records in a single embeddings call")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Always parse CSV with a real parser - quoted commas are everywhere.
- Filter drafts, archived rows and blanks; keep the latest version of duplicates.
- Report what was skipped - it's how you find export problems.
