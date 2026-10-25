---
type: task
title: "Produce an onboarding document for a seeded repo"
minutes: 30
---

## Set up

Set up creates `/root/mastery/039-onboard`, a small shipping API: config read from environment variables, a route table, a Makefile, and one test.

```bash
rm -rf /root/mastery/039-onboard && mkdir -p /root/mastery/039-onboard/app /root/mastery/039-onboard/tests && cd /root/mastery/039-onboard
cat > README.md <<'EOF'
# shipping-api

Internal shipping quotes and labels.
EOF
cat > app/__init__.py <<'EOF'

EOF
cat > app/config.py <<'EOF'
import os

DB_URL = os.environ.get("SHIP_DB_URL", "sqlite:///ship.db")
PORT = int(os.environ.get("SHIP_PORT", "8080"))
CARRIER_TIMEOUT_S = float(os.environ.get("SHIP_CARRIER_TIMEOUT_S", "4.5"))
LABEL_FORMAT = os.environ.get("SHIP_LABEL_FORMAT", "pdf")
EOF
cat > app/routes.py <<'EOF'
from app import labels, quotes

ROUTES = {
    ("GET", "/health"): lambda req: {"ok": True},
    ("POST", "/quotes"): quotes.create_quote,
    ("GET", "/quotes/{id}"): quotes.get_quote,
    ("POST", "/labels"): labels.create_label,
}
EOF
cat > app/quotes.py <<'EOF'
RATES_CENTS_PER_KG = {"standard": 450, "express": 1200}
_QUOTES = {}


def create_quote(req):
    kg, speed = req["weight_kg"], req.get("speed", "standard")
    quote = {"id": str(len(_QUOTES) + 1), "cents": round(kg * RATES_CENTS_PER_KG[speed])}
    _QUOTES[quote["id"]] = quote
    return quote


def get_quote(req):
    return _QUOTES[req["id"]]
EOF
cat > app/labels.py <<'EOF'
from app import config


def create_label(req):
    return {"quote_id": req["quote_id"], "format": config.LABEL_FORMAT}
EOF
cat > app/server.py <<'EOF'
"""Entry point: python3 -m app.server"""
import json
from wsgiref.simple_server import make_server

from app import config
from app.routes import ROUTES


def app(environ, start_response):
    key = (environ["REQUEST_METHOD"], environ["PATH_INFO"])
    handler = ROUTES.get(key)
    if handler is None:
        start_response("404 Not Found", [("Content-Type", "application/json")])
        return [b'{"error": "not found"}']
    start_response("200 OK", [("Content-Type", "application/json")])
    return [json.dumps(handler({})).encode()]


def main():
    make_server("", config.PORT, app).serve_forever()


if __name__ == "__main__":
    main()
EOF
cat > Makefile <<'EOF'
test:
	python3 -m unittest -q

run:
	python3 -m app.server

check:
	python3 -m compileall -q app
EOF
cat > tests/__init__.py <<'EOF'

EOF
cat > tests/test_quotes.py <<'EOF'
import unittest

from app import quotes


class QuoteTest(unittest.TestCase):
    def test_standard(self):
        self.assertEqual(quotes.create_quote({"weight_kg": 2})["cents"], 900)
EOF
make test
```

## What to build

Have Claude write the onboarding document a new engineer would want, in a form a script can verify.

1. Run Claude headless in `/root/mastery/039-onboard` with only `Read`, `Glob`, `Grep`, and `Write` allowed, saving `onboard.json`:
   > Write ONBOARDING.md for a new engineer on this repo. Use exactly these sections: ## Run it, ## Configuration (a table of every environment variable and its default, from app/config.py), ## HTTP routes (every route as METHOD /path, from app/routes.py), ## Tests, ## Where to start. State only facts you read in the files, and name the file each section comes from.
2. Read `ONBOARDING.md`. If a fact is wrong, re-run with a sharper prompt or fix it by hand - but the final file must be one the checker can verify.

The checker parses `app/config.py`, `app/routes.py`, and the `Makefile` and compares: every env var with its real default, every route and no invented ones, only real `make` targets, and every backticked path existing.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Tables and `METHOD /path` lines are easy to verify; paragraphs are not.
- If the checker flags an invented path, the prompt's 'only facts you read' line is the lever.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/039-onboard
claude -p 'Write ONBOARDING.md for a new engineer on this repo. Use exactly these sections: ## Run it, ## Configuration (a table of every environment variable and its default, from app/config.py), ## HTTP routes (every route as METHOD /path, from app/routes.py), ## Tests, ## Where to start. State only facts you read in the files, and name the file each section comes from.' --allowedTools Read Glob Grep Write --output-format json < /dev/null > onboard.json
jq -r .result onboard.json
cat ONBOARDING.md
```

</details>

## Check your work

```bash
D=/root/mastery/039-onboard; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
def transcript(sid):
    for f in glob.glob(os.path.expanduser(f"~/.claude/projects/*/{sid}.jsonl")):
        rows = []
        for line in open(f, errors="replace"):
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
        return f, rows
    return None, []
def rtext(b):
    c = b.get("content")
    return c if isinstance(c, str) else " ".join(x.get("text", "") for x in (c or []) if isinstance(x, dict))
def result_for(rows, pred):
    ids = [u["id"] for u in uses(rows) if pred(u)]
    return [b for b in results(rows) if b.get("tool_use_id") in ids]
def run_rows(p):
    env = load(p) or {}
    return transcript(env.get("session_id") or "none")[1]

doc = text("ONBOARDING.md")
secs = ["## Run it", "## Configuration", "## HTTP routes", "## Tests", "## Where to start"]
ok(doc and all(s in doc for s in secs), "ONBOARDING.md has all five sections", f"ONBOARDING.md is missing {[s for s in secs if s not in doc]}")
env = re.findall(r'os\.environ\.get\("([A-Z_]+)",\s*"([^"]*)"\)', text("app/config.py"))
lines = doc.splitlines()
miss = [f"{k}={v}" for k, v in env if not any(k in l and v in l for l in lines)]
ok(env and not miss, f"every environment variable appears with its real default ({len(env)})", f"missing or wrong defaults: {miss}")
routes = re.findall(r'\("(GET|POST|PUT|DELETE|PATCH)",\s*"([^"]+)"\)', text("app/routes.py"))
rmiss = [f"{m} {p}" for m, p in routes if f"{m} {p}" not in doc]
ok(routes and not rmiss, f"every route appears as METHOD /path ({len(routes)})", f"missing routes: {rmiss}")
documented = set(re.findall(r'^(?:GET|POST|PUT|DELETE|PATCH) (/\S*)', "\n".join(re.sub(r"^[-*\s`]+", "", l) for l in lines), re.M))
extra = sorted(p.rstrip("`") for p in documented if p.rstrip("`") not in {p2 for _, p2 in routes})
ok(not extra, "no invented routes", f"these routes are not in app/routes.py: {extra}")
targets = set(re.findall(r"^([A-Za-z][\w-]*):", text("Makefile"), re.M))
said = set(re.findall(r"make ([A-Za-z][\w-]*)", doc))
ok({"test", "run"} <= said and said <= targets, "every make target mentioned exists (and test and run are covered)", f"make targets mentioned {sorted(said)}, Makefile has {sorted(targets)}")
paths = [t for t in re.findall(r"`([^`\s]+)`", doc) if ":" not in t and not t.startswith("/") and re.fullmatch(r"[\w.-]+(/[\w.{}-]*)*", t) and ("/" in t or t.endswith(".py"))]
ghost = [p for p in paths if not os.path.exists(p)]
ok(paths and not ghost, f"every file path in backticks exists ({len(paths)})", f"these paths don't exist: {ghost}")
start = doc.split("## Where to start")[-1] if "## Where to start" in doc else ""
ok(any(p in start for p in paths if os.path.exists(p)), "Where to start points at real files", "## Where to start should name real files to read first")
rows = run_rows("onboard.json")
read = {os.path.basename((u.get("input") or {}).get("file_path", "")) for u in uses(rows) if u.get("name") == "Read"}
ok({"config.py", "routes.py"} <= read, "Claude read app/config.py and app/routes.py before writing", f"onboard.json should come from a run that read config.py and routes.py - it read {sorted(read)}")
wr = result_for(rows, lambda u: u.get("name") == "Write" and (u.get("input") or {}).get("file_path", "").endswith("ONBOARDING.md"))
ok(wr and not wr[-1].get("is_error"), "Claude wrote ONBOARDING.md itself", "ONBOARDING.md should be written by the headless run")
PYEOF
```

## What you learned

- Explore with read-only tools, then write from what was actually read.
- Ask for facts in checkable shapes: tables, METHOD /path, make targets, real paths.
- Verify the document against the source before anyone relies on it.
