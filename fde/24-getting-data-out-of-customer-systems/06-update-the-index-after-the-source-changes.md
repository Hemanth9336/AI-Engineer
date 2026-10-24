---
type: task
title: "Update the index after the source changes"
minutes: 8
---

## Set up

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
rm -f synced.json
```

## What to build

Write `/root/fde-lab/24-data/sync.py`, used as `python sync.py DB_FILE STORE_FILE`, which performs an **incremental** sync:

- Load the store if it exists (otherwise start empty), and read the eligible rows as in the previous task.
- Work out `added`, `updated` (same id, different `updated_at`), `removed` and the unchanged count.
- Embed **only** added and updated records, in one call - and make no embeddings call at all when there's nothing to embed.
- Write the store sorted by id, keeping unchanged records' embeddings as they were.
- Print `{"added": [...], "updated": [...], "removed": [...], "unchanged": N}` with sorted id lists.

```bash
cd /root/fde-lab/24-data
python sync.py kb.sqlite synced.json        # first run: everything is added
python - <<'PY'
import sqlite3
con = sqlite3.connect("kb.sqlite")
con.execute("UPDATE articles SET body = 'Standard pallets up to 750 kg from April.', updated_at = '2026-03-30' WHERE id = 'kb-204'")
con.execute("UPDATE articles SET deleted = 1 WHERE id = 'kb-202'")
con.execute("INSERT INTO articles VALUES ('kb-206', 'Holiday deliveries', 'No deliveries on public holidays.', '2026-03-31', 0)")
con.commit()
PY
python sync.py kb.sqlite synced.json        # second run: one of each
python sync.py kb.sqlite synced.json        # third run: nothing to do
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Index both sides by id: `store = {r["id"]: r for r in ...}`, `current = {...}`.
- Guard the embeddings call with `if todo:`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/24-data
cat > sync.py <<'EOF'
import json
import sqlite3
import sys
from pathlib import Path

from openai import OpenAI

db, store_path = sys.argv[1], Path(sys.argv[2])
store = {r["id"]: r for r in json.loads(store_path.read_text())} if store_path.exists() else {}
con = sqlite3.connect(db)
rows = con.execute(
    "SELECT id, title, body, updated_at FROM articles WHERE deleted = 0 AND TRIM(COALESCE(body, '')) != '' ORDER BY id"
).fetchall()
current = {i: {"id": i, "text": f"{t.strip()}. {b.strip()}", "source": "sqlite", "updated_at": u} for i, t, b, u in rows}

added = sorted(i for i in current if i not in store)
updated = sorted(i for i in current if i in store and store[i]["updated_at"] != current[i]["updated_at"])
removed = sorted(i for i in store if i not in current)
todo = added + updated
if todo:
    vectors = OpenAI().embeddings.create(model="lab-embed", input=[current[i]["text"] for i in todo]).data
    for i, v in zip(todo, vectors):
        store[i] = {**current[i], "embedding": v.embedding}
for i in removed:
    del store[i]
store_path.write_text(json.dumps([store[i] for i in sorted(store)]))
print(json.dumps({"added": added, "updated": updated, "removed": removed, "unchanged": len(current) - len(todo)}))

EOF
python sync.py kb.sqlite synced.json
python - <<'PY'
import sqlite3
con = sqlite3.connect("kb.sqlite")
con.execute("UPDATE articles SET body = 'Standard pallets up to 750 kg from April.', updated_at = '2026-03-30' WHERE id = 'kb-204'")
con.execute("UPDATE articles SET deleted = 1 WHERE id = 'kb-202'")
con.execute("INSERT INTO articles VALUES ('kb-206', 'Holiday deliveries', 'No deliveries on public holidays.', '2026-03-31', 0)")
con.commit()
PY
python sync.py kb.sqlite synced.json
python sync.py kb.sqlite synced.json
```

</details>

## Check your work

```bash
D=/root/fde-lab/24-data; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/sync.py 2>/dev/null && [ -s $D/sync.py ] && echo "✅ sync.py reads the key from the environment" || echo "❌ sync.py must not contain a key - let the SDK read it from the environment"
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
db, st = "/tmp/sync-check.sqlite", "/tmp/sync-check.json"
Path(st).unlink(missing_ok=True)
con = sqlite3.connect(db)
con.execute("DROP TABLE IF EXISTS articles")
con.execute("CREATE TABLE articles (id TEXT PRIMARY KEY, title TEXT, body TEXT, updated_at TEXT, deleted INTEGER)")
con.executemany("INSERT INTO articles VALUES (?, ?, ?, ?, ?)", [("p1", "One", "First text.", "2026-01-01", 0), ("p2", "Two", "Second text.", "2026-01-01", 0), ("p3", "Three", "Third text.", "2026-01-01", 0), ("p4", "Four", "Fourth.", "2026-01-01", 1)])
con.commit()
def sync():
    before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
    rc, out, err = run("sync.py", db, st)
    rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
    emb = [r.get("inputs") for r in rows if r.get("api") == "embeddings"]
    try:
        return json.loads(out), emb
    except ValueError:
        return {"error": out[:150] + err[-150:]}, emb
r, emb = sync()
ok(r == {"added": ["p1", "p2", "p3"], "updated": [], "removed": [], "unchanged": 0} and emb == [3], "first run adds every live row in one embeddings call", f"first run: expected 3 added and one embeddings call with 3 inputs - got {r}, calls {emb}")
kept = {x["id"]: x["embedding"] for x in load(st) or []}
con.execute("UPDATE articles SET body = 'Second text, revised.', updated_at = '2026-02-01' WHERE id = 'p2'")
con.execute("UPDATE articles SET deleted = 1 WHERE id = 'p3'")
con.execute("UPDATE articles SET deleted = 0, updated_at = '2026-02-02' WHERE id = 'p4'")
con.execute("INSERT INTO articles VALUES ('p5', 'Five', 'Fifth.', '2026-02-03', 0)")
con.commit()
r, emb = sync()
ok(r == {"added": ["p4", "p5"], "updated": ["p2"], "removed": ["p3"], "unchanged": 1} and emb == [3], "second run: 2 added, 1 updated, 1 removed, 1 unchanged - only 3 texts embedded", f"second run: expected added [p4, p5], updated [p2], removed [p3], unchanged 1 and one call with 3 inputs - got {r}, calls {emb}")
s = load(st) or []
ok([x["id"] for x in s] == ["p1", "p2", "p4", "p5"] and s[0]["embedding"] == kept.get("p1") and "revised" in s[1]["text"] and cos(s[1]["embedding"], E([s[1]["text"]])[0]) > 0.999, "the store is sorted, unchanged embeddings are reused and updated ones re-embedded", f"store should be p1, p2, p4, p5 with p1's old embedding and p2 re-embedded - got {[x.get('id') for x in s]}")
r, emb = sync()
ok(r == {"added": [], "updated": [], "removed": [], "unchanged": 4} and emb == [], "a run with no changes makes no embeddings call", f"third run: expected nothing to do and no embeddings call - got {r}, calls {emb}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Incremental sync needs a stable id and a change marker like updated_at.
- Handle adds, updates and deletes - forgotten deletes keep withdrawn content alive.
- Embed only what changed, and report the counts as monitoring.
