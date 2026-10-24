---
type: task
title: "Trim a huge tool result to what matters"
minutes: 9
---

## Set up

`logs/search.log` has 5,000 lines (`<timestamp> <LEVEL> <service>: <message>`), mostly INFO. A few ERROR lines carry a very long `trace=`.

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
ls -la logs && wc -l logs/*.log
```

## What to build

Write `/root/harness-lab/13-results/logtools.py` with `search_log(service, level="ERROR", contains=None, limit=20)`:

1. Read `logs/<service>.log`. If it doesn't exist, return `error: no log for service '<x>'. Available: billing, search` (the log names, sorted).
2. Keep the lines whose **level** (the second space-separated field) equals `level` and, if `contains` is given, that contain it (case-insensitive).
3. Clamp `limit` to 1-50. Show the first `limit` matches, each cut to its first **200** characters.
4. Return one string: a header `<matches> matching lines out of <total>; showing <shown>`, the lines, and - only if some matches weren't shown - a last line `Narrow the search with contains= or raise limit (max 50).`

Compare the size against reading the whole file:

```bash
cd /root/harness-lab/13-results
python -c "
from logtools import search_log
full = open('logs/search.log').read()
r = search_log('search')
print(len(full), 'chars ->', len(r), 'chars'); print(r[:600])"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `l.split(" ", 2)[1]` is the level field.
- `limit = max(1, min(int(limit), 50))`.
- Count matches before cutting the list, so the header can say how many there were.

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
python -c "
from logtools import search_log
full = open('logs/search.log').read()
r = search_log('search')
print(len(full), 'chars ->', len(r), 'chars'); print(r[:600])"
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
def expect(service, level="ERROR", contains=None, limit=20):
    p = Path(f"logs/{service}.log")
    if not p.is_file():
        return f"error: no log for service {service!r}. Available: billing, search"
    limit = max(1, min(int(limit), 50))
    lines = p.read_text().splitlines()
    hits = [l for l in lines if l.split(" ", 2)[1:2] == [level] and (not contains or contains.lower() in l.lower())]
    shown = [l[:200] for l in hits[:limit]]
    out = [f"{len(hits)} matching lines out of {len(lines)}; showing {len(shown)}"] + shown
    if len(hits) > len(shown):
        out.append("Narrow the search with contains= or raise limit (max 50).")
    return "\n".join(out)
try:
    from logtools import search_log
except Exception as e:
    search_log = None
    ok(False, "", f"logtools.py should define search_log - {type(e).__name__}: {e}")
if search_log:
    r = search_log("search")
    ok(r == expect("search"), "default call: ERROR lines, 20 shown, header and hint", f"search_log('search') should start {expect('search')[:120]!r} - got {str(r)[:160]!r}")
    ok(len(r) < 5000 and len(Path("logs/search.log").read_text()) > 80 * len(r), "the result is over 80x smaller than the whole log", f"the default result is {len(r)} chars")
    ok(all(len(l) <= 200 for l in r.splitlines()), "no line is longer than 200 characters", "long lines (the trace= ones) should be cut to 200 characters")
    cases = [("search", "WARN", None, 5), ("billing", "ERROR", None, 20), ("search", "ERROR", "R00970", 20), ("search", "INFO", None, 500), ("search", "ERROR", None, 0)]
    bad = [c for c in cases if search_log(*c) != expect(*c)]
    ok(not bad, "level, contains (case-insensitive), the limit clamp and the no-hint case all work", f"wrong result for search_log{bad[0] if bad else ''}: expected {expect(*bad[0])[:150]!r}" if bad else "")
    e = search_log("payments")
    ok(e == "error: no log for service 'payments'. Available: billing, search", "an unknown service lists the available logs", f"got {e!r}")
PYEOF
```

## What you learned

- Tool results stay in context and are paid for on every later step.
- Filter at the source, cap counts, cut long lines, and say what was left out.
- A result that tells the model how to get more beats one that dumps everything.
