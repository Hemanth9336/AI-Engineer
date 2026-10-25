---
type: task
title: "Run a two helper team"
minutes: 23
---

## Set up

Set up creates `/root/mastery/073-helpers` with `api/routes.py` (five routes) and `docs/api.md` (five documented endpoints). They don't quite agree.

```bash
rm -rf /root/mastery/073-helpers && mkdir -p /root/mastery/073-helpers/api /root/mastery/073-helpers/docs && cd /root/mastery/073-helpers
cat > api/routes.py <<'EOF'
"""Routes for the orders service."""
from framework import route


@route("GET", "/health")
def health():
    return "ok"


@route("GET", "/orders", auth=True)
def list_orders():
    ...


@route("POST", "/orders", auth=True)
def create_order():
    ...


@route("DELETE", "/orders/<id>")
def delete_order(id):
    ...


@route("GET", "/export")
def export_all():
    ...
EOF
cat > docs/api.md <<'EOF'
# Orders API

| Method | Path | Description |
|---|---|---|
| GET | /health | Liveness probe |
| GET | /orders | List your orders |
| POST | /orders | Create an order |
| DELETE | /orders/<id> | Cancel an order |
| GET | /invoices | Download invoices |
EOF
jq --version
```

## What to build

1. Write `merge.py API_JSON DOCS_JSON`. It prints JSON with three sorted lists of `{method, path}`:
   - `undocumented`: in the routes but not the docs.
   - `missing`: documented but not routed.
   - `unauthenticated`: routes whose `auth` is false or missing.

   Compare methods case-insensitively.
2. Write `team.sh`.
   - Clean `team/` first.
   - Start two named helpers **in the background**: `claude -p ... --name <helper>`, with `--tools "Read,Glob,Grep,Write"`, `--permission-mode acceptEdits`, `--max-turns 8`, and `--output-format json` saved to `team/status/<helper>.json`.
     - `api-audit`:
       > You are the api-audit helper. Read api/routes.py and write team/api-audit.json as {"endpoints": [{"method": ..., "path": ..., "auth": true|false}]} with one entry per route. Write only that file.
     - `docs-audit`:
       > You are the docs-audit helper. Read docs/api.md and write team/docs-audit.json as {"documented": [{"method": ..., "path": ...}]} with one entry per documented endpoint. Write only that file.
   - `wait` for each one. Fail (exit 1, no report) if any helper exits non-zero, has an error envelope, or left no valid artifact.
   - Otherwise merge into `team/REPORT.json` and a readable `team/REPORT.md`.
3. Run `./team.sh`.

The checker confirms that the two helper sessions overlapped in time, and runs copies of your script with a helper that fails and with helpers that leave nothing behind.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `helper a "$P1" & pid_a=$!` starts a function in the background and records its PID; `wait "$pid_a"` returns that helper's exit code.
- Python sets do the merge: `routes - documented`, `documented - routes`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/073-helpers
cat > merge.py <<'EOF'
#!/usr/bin/env python3
"""merge.py API_JSON DOCS_JSON - compare routes with documentation and print the report as JSON."""
import json
import sys


def key(e):
    return (e["method"].upper(), e["path"])


api = json.load(open(sys.argv[1]))["endpoints"]
docs = json.load(open(sys.argv[2]))["documented"]
routes = {key(e) for e in api}
documented = {key(e) for e in docs}
as_list = lambda keys: [{"method": m, "path": p} for m, p in sorted(keys)]
print(json.dumps({
    "undocumented": as_list(routes - documented),
    "missing": as_list(documented - routes),
    "unauthenticated": as_list({key(e) for e in api if not e.get("auth")}),
}, indent=2))
EOF
cat > team.sh <<'EOF'
#!/usr/bin/env bash
# team.sh - run two read-only helpers in parallel, check each one, and merge their artifacts into team/REPORT.json
set -uo pipefail
cd "$(dirname "$0")"
rm -rf team && mkdir -p team/status

P_API='You are the api-audit helper. Read api/routes.py and write team/api-audit.json as {"endpoints": [{"method": ..., "path": ..., "auth": true|false}]} with one entry per route. Write only that file.'
P_DOCS='You are the docs-audit helper. Read docs/api.md and write team/docs-audit.json as {"documented": [{"method": ..., "path": ...}]} with one entry per documented endpoint. Write only that file.'

helper() {  # helper NAME PROMPT
  claude -p "$2" --name "$1" --tools "Read,Glob,Grep,Write" --permission-mode acceptEdits --max-turns 8 \
    --output-format json < /dev/null > "team/status/$1.json" 2> "team/status/$1.err"
}

helper api-audit "$P_API" & pid_api=$!
helper docs-audit "$P_DOCS" & pid_docs=$!

fail=0
for pair in "api-audit:$pid_api" "docs-audit:$pid_docs"; do
  name=${pair%%:*} pid=${pair##*:}
  wait "$pid" || { echo "helper $name exited non-zero" >&2; fail=1; }
  jq -e '.is_error == false' "team/status/$name.json" > /dev/null 2>&1 || { echo "helper $name: error or unreadable envelope" >&2; fail=1; }
  jq -e 'type == "object"' "team/$name.json" > /dev/null 2>&1 || { echo "helper $name left no valid team/$name.json" >&2; fail=1; }
done
[ "$fail" = 0 ] || { echo "team failed; no report written" >&2; exit 1; }

python3 merge.py team/api-audit.json team/docs-audit.json > team/REPORT.json
jq -r '"# API audit", "", "## Undocumented", (.undocumented[] | "- \(.method) \(.path)"), "",
       "## Documented but missing", (.missing[] | "- \(.method) \(.path)"), "",
       "## No auth", (.unauthenticated[] | "- \(.method) \(.path)")' team/REPORT.json > team/REPORT.md
cat team/REPORT.md
EOF
chmod +x team.sh merge.py
./team.sh
```

</details>

## Check your work

```bash
D=/root/mastery/073-helpers; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
python3 - <<'PYEOF'
import glob, hashlib, json, os, re, subprocess, sys, tempfile
from pathlib import Path
sys.excepthook = lambda t, e, tb: print(f"❌ check stopped: {t.__name__}: {e}")
def ok(cond, good, bad):
    print(("✅ " + good) if cond else ("❌ " + bad))
def load(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None
def text(p):
    try:
        return Path(p).read_text()
    except Exception:
        return ""
def sha(p):
    try:
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    except Exception:
        return None
def sh(cmd, cwd=None, env=None, input=None, timeout=60):
    try:
        r = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, cwd=cwd, input=input,
                           timeout=timeout, env=dict(os.environ, **(env or {})))
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timed out"
def sessions(d):
    # Claude Code saves every session (console or -p) as ~/.claude/projects/<dir>/<id>.jsonl, one JSON row per event
    real, out = os.path.realpath(d), []
    for f in sorted(glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")), key=os.path.getmtime):
        rows = []
        for line in open(f, errors="replace"):
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
        if any(r.get("cwd") and os.path.realpath(r["cwd"]) == real for r in rows):
            out.append(rows)
    return out
def ran(pat, d=None):
    return [rows for rows in sessions(d or os.getcwd()) if any(re.search(pat, p, re.I | re.S) for p in prompts(rows))]
def content(r):
    c = (r.get("message") or {}).get("content")
    return c if isinstance(c, list) else ([{"type": "text", "text": c}] if isinstance(c, str) else [])
def prompts(rows):
    return [b.get("text", "") for r in rows if r.get("type") == "user" and not r.get("isMeta") for b in content(r) if b.get("type") == "text"]
def uses(rows):
    return [b for r in rows if r.get("type") == "assistant" for b in content(r) if b.get("type") == "tool_use"]
def results(rows):
    return [b for r in rows if r.get("type") == "user" for b in content(r) if b.get("type") == "tool_result"]
def models(rows):
    return {(r.get("message") or {}).get("model") for r in rows if r.get("type") == "assistant"} - {None, "<synthetic>"}
def is_haiku(m):
    return bool(m) and ("haiku" in m.lower() or m == os.environ.get("ANTHROPIC_DEFAULT_HAIKU_MODEL"))
def events(p):
    out = []
    for line in text(p).splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out
def init(ev):
    return next((e for e in ev if e.get("type") == "system" and e.get("subtype") == "init"), {})
def result(ev):
    return next((e for e in ev if e.get("type") == "result"), {})
def ev_uses(ev):
    return [b for e in ev if e.get("type") == "assistant" for b in content(e) if b.get("type") == "tool_use"]
def stub(t, body):
    b = Path(t, "bin"); b.mkdir(exist_ok=True)
    p = b / "claude"; p.write_text("#!/usr/bin/env bash\n" + body + "\n"); p.chmod(0o755)
    return {"PATH": f"{b}:{os.environ['PATH']}"}

import shutil, datetime
rep = load("team/REPORT.json") or {}
pairs = lambda k: sorted((e.get("method"), e.get("path")) for e in rep.get(k) or [])
ok(pairs("undocumented") == [("GET", "/export")] and pairs("missing") == [("GET", "/invoices")]
   and pairs("unauthenticated") == [("DELETE", "/orders/<id>"), ("GET", "/export"), ("GET", "/health")],
   "team/REPORT.json: /export undocumented, /invoices missing, three routes without auth", f"run ./team.sh - REPORT.json is {rep}")
a, d = load("team/api-audit.json") or {}, load("team/docs-audit.json") or {}
ok(len(a.get("endpoints") or []) == 5 and len(d.get("documented") or []) == 5 and (load("team/status/api-audit.json") or {}).get("type") == "result"
   and (load("team/status/docs-audit.json") or {}).get("type") == "result",
   "each helper left its artifact and its envelope in team/", "each helper writes team/<name>.json; keep each envelope in team/status/<name>.json")
def span(rows):
    ts = [datetime.datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00")) for r in rows if r.get("timestamp")]
    return (min(ts), max(ts)) if ts else None
runs = {}
for rows in sessions("."):
    ps = " ".join(prompts(rows))
    for name in ("api-audit", "docs-audit"):
        if f"You are the {name} helper" in ps:
            runs[name] = span(rows)
both = runs.get("api-audit") and runs.get("docs-audit")
ok(both and runs["api-audit"][0] <= runs["docs-audit"][1] and runs["docs-audit"][0] <= runs["api-audit"][1],
   "the two helper sessions ran at the same time", f"start both helpers in the background (&) and then wait - sessions {runs}")
src = text("team.sh")
ok(re.search(r"--name\s+\"?\$?\{?1", src) or ("--name api-audit" in src and "--name docs-audit" in src), "helpers are named with --name", "give each helper a --name")
def copy(t):
    for f in ("team.sh", "merge.py"):
        shutil.copy(f, t)
    shutil.copytree("api", Path(t, "api")); shutil.copytree("docs", Path(t, "docs"))
OKENV = '{"type":"result","subtype":"success","is_error":false,"result":"ok","session_id":"s"}'
with tempfile.TemporaryDirectory() as t:
    copy(t)
    body = ('case "$*" in *docs-audit*) echo \'{"type":"result","subtype":"error_during_execution","is_error":true,"session_id":"s"}\'; exit 1;; esac\n'
            'mkdir -p team && echo \'{"endpoints": []}\' > team/api-audit.json\necho \'' + OKENV + "'")
    rc, so_, se = sh(["./team.sh"], cwd=t, env=stub(t, body), timeout=120)
    ok(rc == 1 and not Path(t, "team/REPORT.json").exists() and "docs-audit" in se, "one failing helper fails the team and no report is written",
       f"check every helper's exit code and envelope - rc {rc}, stderr {se.strip()[-150:]!r}")
with tempfile.TemporaryDirectory() as t:
    copy(t)
    Path(t, "team").mkdir(); Path(t, "team/docs-audit.json").write_text('{"documented": []}')
    rc, so_, se = sh(["./team.sh"], cwd=t, env=stub(t, "echo '" + OKENV + "'"), timeout=120)
    ok(rc == 1 and not Path(t, "team/REPORT.json").exists(), "helpers that succeed but leave no artifact (and a stale one from before) fail the team",
       f"clean team/ before starting and require each artifact - rc {rc}")
with tempfile.TemporaryDirectory() as t:
    shutil.copy("merge.py", t)
    Path(t, "a.json").write_text(json.dumps({"endpoints": [{"method": "get", "path": "/a", "auth": True}, {"method": "PUT", "path": "/b"}]}))
    Path(t, "d.json").write_text(json.dumps({"documented": [{"method": "GET", "path": "/a"}, {"method": "GET", "path": "/c"}]}))
    rc, so_, se = sh([sys.executable, "merge.py", "a.json", "d.json"], cwd=t)
    try:
        h = json.loads(so_)
    except ValueError:
        h = {}
    ok(h.get("undocumented") == [{"method": "PUT", "path": "/b"}] and h.get("missing") == [{"method": "GET", "path": "/c"}]
       and h.get("unauthenticated") == [{"method": "PUT", "path": "/b"}],
       "merge.py on hidden artifacts: methods compared case-insensitively, a missing auth counts as no auth", f"merge.py should print the three lists - got {so_.strip()[:200]}")
PYEOF
```

## What you learned

- Unattended fan-out works best as parallel helpers that each leave a fixed-name artifact, merged by deterministic code.
- Check every helper's exit code, envelope, and artifact, and clean old artifacts first; any failure fails the team.
- Interactive coordination between sessions uses SendMessage, @-mentions, and crossSessionInbound; the same tool also reaches subagents and teammates.
