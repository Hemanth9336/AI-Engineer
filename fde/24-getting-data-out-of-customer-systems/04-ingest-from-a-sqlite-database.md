---
type: task
title: "Ingest from a SQLite database"
minutes: 7
---

## Set up

`kb.sqlite` holds the help center's `articles` table: `id, title, body, updated_at, deleted`. Rows are soft-deleted with `deleted = 1`.

```bash
mkdir -p /root/fde-lab/24-data
cd /root/fde-lab/24-data
python - <<'PYEOF'
import sqlite3
con = sqlite3.connect('kb.sqlite')
con.execute("DROP TABLE IF EXISTS articles")
con.execute("CREATE TABLE articles (id TEXT PRIMARY KEY, title TEXT, body TEXT, updated_at TEXT, deleted INTEGER)")
con.executemany("INSERT INTO articles VALUES (?, ?, ?, ?, ?)", [('kb-201', 'Missed delivery', 'After two failed attempts the parcel waits at the depot for 7 days.', '2026-02-01', 0), ('kb-202', 'Address changes', 'Change the address until the parcel leaves the depot.', '2026-02-03', 0), ('kb-203', 'Old fuel table', 'Superseded fuel table.', '2025-06-01', 1), ('kb-204', 'Weight limits', 'Standard pallets up to 800 kg.', '2026-02-05', 0), ('kb-205', 'Blank', '', '2026-02-06', 0)])
con.commit()
PYEOF
python -c "import sqlite3; print(sqlite3.connect('kb.sqlite').execute('SELECT COUNT(*) FROM articles').fetchone()[0], 'rows in kb.sqlite')"
```

## What to build

Write `/root/fde-lab/24-data/ingest_sqlite.py`, used as `python ingest_sqlite.py DB_FILE STORE_FILE`:

1. Query `articles` for rows with `deleted = 0` and a non-blank body, **ordered by id**, in SQL.
2. Records as in the CSV task, with `"source": "sqlite"`, embedded in one call.
3. Print `ingested N rows`.

```bash
cd /root/fde-lab/24-data
sqlite3 kb.sqlite 'SELECT id, deleted, length(body) FROM articles' 2>/dev/null || python -c "import sqlite3; print(sqlite3.connect('kb.sqlite').execute('SELECT id, deleted, length(body) FROM articles').fetchall())"
python ingest_sqlite.py kb.sqlite store-db.json
```

Use query parameters or fixed SQL - never build SQL by pasting in strings.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `WHERE deleted = 0 AND TRIM(COALESCE(body, '')) != '' ORDER BY id`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/24-data
cat > ingest_sqlite.py <<'EOF'
import json
import sqlite3
import sys

from openai import OpenAI

con = sqlite3.connect(sys.argv[1])
rows = con.execute(
    "SELECT id, title, body, updated_at FROM articles WHERE deleted = 0 AND TRIM(COALESCE(body, '')) != '' ORDER BY id"
).fetchall()
records = [{"id": i, "text": f"{t.strip()}. {b.strip()}", "source": "sqlite", "updated_at": u} for i, t, b, u in rows]
vectors = [d.embedding for d in OpenAI().embeddings.create(model="lab-embed", input=[r["text"] for r in records]).data] if records else []
for r, v in zip(records, vectors):
    r["embedding"] = v
json.dump(records, open(sys.argv[2], "w"))
print(f"ingested {len(records)} rows")

EOF
python ingest_sqlite.py kb.sqlite store-db.json
```

</details>

## Check your work

```bash
D=/root/fde-lab/24-data; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/ingest_sqlite.py 2>/dev/null && [ -s $D/ingest_sqlite.py ] && echo "✅ ingest_sqlite.py reads the key from the environment" || echo "❌ ingest_sqlite.py must not contain a key - let the SDK read it from the environment"
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
def ref(db):
    rows = sqlite3.connect(db).execute("SELECT id, title, body, updated_at FROM articles WHERE deleted = 0 AND TRIM(COALESCE(body, '')) != '' ORDER BY id").fetchall()
    return [{"id": i, "text": f"{t.strip()}. {b.strip()}", "source": "sqlite", "updated_at": u} for i, t, b, u in rows]
def verify(db, store, label):
    want, got = ref(db), load(store) or []
    ok([{k: r.get(k) for k in ("id", "text", "source", "updated_at")} for r in got] == want, f"{label}: live, non-blank rows in id order", f"{label}: expected {[r['id'] for r in want]} - got {[r.get('id') for r in got]}")
    if got and len(got) == len(want):
        ok(all(cos(r["embedding"], v) > 0.999 for r, v in zip(got, E([w["text"] for w in want]))), f"{label}: embeddings match the texts", f"{label}: each embedding should be the lab-embed vector of its text")
verify("kb.sqlite", "store-db.json", "kb.sqlite")
con = sqlite3.connect("/tmp/kb2.sqlite")
con.execute("DROP TABLE IF EXISTS articles")
con.execute("CREATE TABLE articles (id TEXT PRIMARY KEY, title TEXT, body TEXT, updated_at TEXT, deleted INTEGER)")
con.executemany("INSERT INTO articles VALUES (?, ?, ?, ?, ?)", [("z-9", " Zeta ", " Last by id. ", "2026-04-01", 0), ("a-1", "Alpha", "First by id.", "2026-04-02", 0), ("m-5", "Gone", "Deleted row.", "2026-04-03", 1), ("b-2", "Nulls", None, "2026-04-04", 0)])
con.commit()
rc, out, err = run("ingest_sqlite.py", "/tmp/kb2.sqlite", "/tmp/store-db2.json")
ok(rc == 0 and out == "ingested 2 rows", "a new database prints 'ingested 2 rows'", f"expected 'ingested 2 rows' - got {out!r} {err[-200:]}")
verify("/tmp/kb2.sqlite", "/tmp/store-db2.json", "a new database with NULL bodies and soft deletes")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Filter soft-deleted and blank rows in SQL, at the source.
- Order results explicitly - databases don't guarantee row order.
- Never build SQL from pasted strings; use fixed queries or parameters.
