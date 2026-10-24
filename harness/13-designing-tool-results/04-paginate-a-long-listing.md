---
type: task
title: "Paginate a long listing"
minutes: 10
---

## Set up

`artifacts/` holds 230 build files. Listing them all at once would add every name to the context on every step.

```bash
mkdir -p /root/harness-lab/13-results
cd /root/harness-lab/13-results
python - <<'EOF'
import os
os.makedirs("logs", exist_ok=True)
for svc, n in (("search", 5000), ("billing", 1200)):
    with open(f"logs/{svc}.log", "w") as f:
        for i in range(n):
            ts = f"2026-03-14T{(i // 3600) % 24:02d}:{(i // 60) % 60:02d}:{i % 60:02d}Z"
            if i % 97 == 0:
                msg = f"ERROR {svc}: upstream timeout after 2000ms request_id=r{i:05d}"
                if i % 3 == 0:
                    msg += " trace=" + "frame;" * 180
            elif i % 31 == 0:
                msg = f"WARN {svc}: slow query {200 + i % 700}ms request_id=r{i:05d}"
            else:
                msg = f"INFO {svc}: GET /api/items/{i % 400} 200 {12 + i % 40}ms request_id=r{i:05d}"
            f.write(f"{ts} {msg}\n")
os.makedirs("artifacts", exist_ok=True)
for i in range(1, 231):
    open(f"artifacts/build-{i:04d}.tar.gz", "w").write("x")
EOF
ls artifacts | wc -l
```

## What to build

Add `list_artifacts(page=1, page_size=50)` to `/root/harness-lab/13-results/logtools.py`:

1. List the names in `artifacts/`, **sorted**.
2. Clamp `page_size` to 1-100. Work out the number of pages (at least 1).
3. If `page` isn't a whole number from 1 to the number of pages, return `error: page must be from 1 to <pages>`.
4. Otherwise return that page's names, one per line, then a footer:
   - not the last page: `page <p> of <pages> (<total> files). Call again with page=<p+1> for more.`
   - the last page: `page <p> of <pages> (<total> files). End of listing.`

```bash
cd /root/harness-lab/13-results
python -c "from logtools import list_artifacts as l; print(l()); print(l(page=5))"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `pages = max(1, -(-total // page_size))` is ceiling division.
- `names[(page - 1) * page_size : page * page_size]`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/13-results
cat > logtools.py <<'EOF'
from pathlib import Path

LOGS = Path(__file__).parent / "logs"
ART = Path(__file__).parent / "artifacts"


def read_log(service):
    """The old tool: returns the whole file."""
    return (LOGS / f"{service}.log").read_text()


def search_log(service, level="ERROR", contains=None, limit=20):
    path = LOGS / f"{service}.log"
    if not path.is_file():
        names = ", ".join(sorted(p.stem for p in LOGS.glob("*.log")))
        return f"error: no log for service {service!r}. Available: {names}"
    limit = max(1, min(int(limit), 50))
    lines = path.read_text().splitlines()
    hits = [l for l in lines if l.split(" ", 2)[1:2] == [level] and (not contains or contains.lower() in l.lower())]
    shown = [l[:200] for l in hits[:limit]]
    out = [f"{len(hits)} matching lines out of {len(lines)}; showing {len(shown)}"] + shown
    if len(hits) > len(shown):
        out.append("Narrow the search with contains= or raise limit (max 50).")
    return "\n".join(out)


def list_artifacts(page=1, page_size=50):
    names = sorted(p.name for p in ART.iterdir())
    page_size = max(1, min(int(page_size), 100))
    pages = max(1, -(-len(names) // page_size))
    if not isinstance(page, int) or not 1 <= page <= pages:
        return f"error: page must be from 1 to {pages}"
    chunk = names[(page - 1) * page_size: page * page_size]
    if page < pages:
        footer = f"page {page} of {pages} ({len(names)} files). Call again with page={page + 1} for more."
    else:
        footer = f"page {page} of {pages} ({len(names)} files). End of listing."
    return "\n".join(chunk + [footer])

EOF
python -c "from logtools import list_artifacts as l; print(l()); print(l(page=5))"
```

</details>

## Check your work

```bash
D=/root/harness-lab/13-results; cd $D 2>/dev/null || echo "❌ create $D"
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
sys.path.insert(0, '/opt/harness')
from labmock import MockModel
sys.path.insert(0, ".")
names = sorted(p.name for p in Path("artifacts").iterdir())
def expect(page=1, page_size=50):
    page_size = max(1, min(int(page_size), 100))
    pages = max(1, -(-len(names) // page_size))
    if not isinstance(page, int) or not 1 <= page <= pages:
        return f"error: page must be from 1 to {pages}"
    chunk = names[(page - 1) * page_size: page * page_size]
    tail = f"Call again with page={page + 1} for more." if page < pages else "End of listing."
    return "\n".join(chunk + [f"page {page} of {pages} ({len(names)} files). {tail}"])
try:
    from logtools import list_artifacts
except Exception as e:
    list_artifacts = None
    ok(False, "", f"logtools.py should define list_artifacts - {type(e).__name__}: {e}")
if list_artifacts:
    r = list_artifacts()
    ok(r == expect(), "page 1 shows 50 sorted names and tells the model how to get page 2", f"list_artifacts() should end with 'page 1 of 5 (230 files). Call again with page=2 for more.' - got ...{str(r)[-90:]!r}")
    r5 = list_artifacts(page=5)
    ok(r5 == expect(5), "the last page has the remaining 30 names and says End of listing.", f"page 5 should list build-0201..build-0230 and end 'End of listing.' - got ...{str(r5)[-90:]!r}")
    pages = [list_artifacts(page=p) for p in range(1, 6)]
    seen = [l for pg in pages for l in str(pg).splitlines()[:-1]]
    ok(seen == names, "walking pages 1-5 visits every file exactly once, in order", "pages 1-5 together should list all 230 files with no repeats or gaps")
    cases = [dict(page=2, page_size=100), dict(page=1, page_size=500), dict(page=3, page_size=0), dict(page=6), dict(page=0), dict(page="2")]
    bad = [c for c in cases if list_artifacts(**c) != expect(**c)]
    ok(not bad, "page_size is clamped to 1-100 and bad page numbers get a range error", f"wrong result for list_artifacts(**{bad[0]}): expected {expect(**bad[0])[-80:]!r}" if bad else "")
PYEOF
```

## What you learned

- Pagination lets the model pay only for the pages it actually reads.
- A footer with the page, total and exact next call makes the next step obvious; the last page says it's the end.
- Never truncate silently - always mark what was cut and how to get it.
