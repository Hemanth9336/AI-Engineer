---
type: task
title: "Triage a traceback"
minutes: 30
---

## Set up

Set up creates `/root/mastery/047-triage` with the payments service source and `incident.log`: four services, retries, an unrelated earlier error, a deploy, and a run of failed checkouts.

```bash
rm -rf /root/mastery/047-triage && mkdir -p /root/mastery/047-triage/payments && cd /root/mastery/047-triage
cat > payments/__init__.py <<'EOF'

EOF
cat > payments/client.py <<'EOF'
"""Payments client: turns an order into a charge request for the card processor."""
import json
import urllib.request

PROCESSOR_URL = "https://processor.internal/v1/charges"
SUPPORTED = {"EUR", "USD", "GBP"}
TIMEOUT_S = 4


class ProcessorError(Exception):
    pass


def _post(payload):
    req = urllib.request.Request(PROCESSOR_URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        return json.load(resp)


def _minor_units(amount, currency):
    if currency not in SUPPORTED:
        raise ValueError(f"unsupported currency {currency}")
    return int(amount)


def _idempotency_key(req):
    return f"{req['order_id']}-{req['attempt']}"


def charge(req):
    amount = req["amount"]
    currency = req["currency"]
    payload = {
        "amount": _minor_units(amount, currency),
        "currency": currency,
        "idempotency_key": _idempotency_key(req),
    }
    result = _post(payload)
    if result.get("status") != "succeeded":
        raise ProcessorError(result.get("error", "unknown"))
    return result
EOF
cat > payments/server.py <<'EOF'
"""Payments HTTP handler."""
from payments import client


def handle(req):
    if req.get("path") != "/charge":
        return {"status": 404}
    try:
        return client.charge(req)
    except client.ProcessorError as e:
        return {"status": 402, "error": str(e)}
EOF
cat > incident.log <<'EOF'
2026-10-25T09:50:00.004Z worker ERROR job=770 smtp connection reset by peer
2026-10-25T09:55:01.002Z gateway INFO req=a1 POST /checkout 200 182ms
2026-10-25T09:55:03.417Z worker WARN job=771 retrying email attempt=2
2026-10-25T09:56:10.930Z payments INFO req=a2 charge ok amount=1299 currency=EUR
2026-10-25T09:56:10.951Z gateway INFO req=a2 POST /checkout 200 240ms
2026-10-25T09:57:44.001Z worker WARN job=771 retrying email attempt=3
2026-10-25T09:58:00.120Z orders INFO deploy finished version=v2.3.0
2026-10-25T09:58:13.010Z orders INFO req=c3 created order=5512 amount=4500
2026-10-25T09:58:13.022Z payments ERROR req=c3 charge failed
Traceback (most recent call last):
  File "payments/server.py", line 9, in handle
    return client.charge(req)
  File "payments/client.py", line 32, in charge
    currency = req["currency"]
KeyError: 'currency'
2026-10-25T09:58:13.030Z orders ERROR req=c3 payment call failed status=500
2026-10-25T09:58:13.041Z gateway ERROR req=c3 POST /checkout 502 upstream=orders
2026-10-25T09:58:20.508Z gateway INFO req=d0 GET /health 200 2ms
2026-10-25T09:58:31.300Z orders INFO req=d4 created order=5513 amount=1250
2026-10-25T09:58:31.311Z payments ERROR req=d4 charge failed
Traceback (most recent call last):
  File "payments/server.py", line 9, in handle
    return client.charge(req)
  File "payments/client.py", line 32, in charge
    currency = req["currency"]
KeyError: 'currency'
2026-10-25T09:58:31.320Z orders ERROR req=d4 payment call failed status=500
2026-10-25T09:58:31.333Z gateway ERROR req=d4 POST /checkout 502 upstream=orders
2026-10-25T09:58:40.000Z worker WARN job=772 retrying email attempt=1
2026-10-25T09:58:52.871Z orders INFO req=e5 created order=5514 amount=9900
2026-10-25T09:58:52.880Z payments ERROR req=e5 charge failed
Traceback (most recent call last):
  File "payments/server.py", line 9, in handle
    return client.charge(req)
  File "payments/client.py", line 32, in charge
    currency = req["currency"]
KeyError: 'currency'
2026-10-25T09:58:52.889Z orders ERROR req=e5 payment call failed status=500
2026-10-25T09:58:52.902Z gateway ERROR req=e5 POST /checkout 502 upstream=orders
2026-10-25T09:59:05.115Z gateway INFO req=f6 GET /catalog 200 35ms
2026-10-25T09:59:30.000Z gateway WARN error rate 31% over 1m on POST /checkout
EOF
wc -l incident.log && grep -c ERROR incident.log
```

## What to build

1. Look first yourself: `grep -n ERROR incident.log`. Which error is first, and which one is first **on the checkout path**?
2. Write `triage.schema.json` requiring:
   - `incident_start`, `service`, `exception` (exactly as logged), `location` (`file:line`), `trigger`,
   - `consequences` (services), `failed_requests` (integer), `red_herrings`, `root_cause`, and `fix_plan` (at least 2 steps).
3. Run Claude headless with `Read`, `Grep`, and `Bash(grep *)`, the schema, and `--max-turns 10`, saving `triage.json`:
   > Triage incident.log. Find the first error in the chain behind the failing POST /checkout requests, read its traceback, open the source line it points to, find what changed just before, count the failed checkout requests, and list unrelated errors as red herrings. Answer with evidence from the log and the code.
4. Write `render_triage.py <run.json>` to turn the structured answer into `TRIAGE.md`, with headings for the root cause, fix plan, and red herrings.

The checker derives every answer from the log and the source itself: the first chain error, the innermost frame, the deploy version, the 502 count, and the red herring.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- The very first ERROR line is not on any request path - it has no req= field.
- The innermost frame is the last `File ...` line before the exception.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/047-triage
grep -n ERROR incident.log | head -5
cat > triage.schema.json <<'EOF'
{
  "type": "object",
  "properties": {
    "incident_start": { "type": "string", "description": "timestamp of the first error in the failing request chain" },
    "service": { "type": "string" },
    "exception": { "type": "string", "description": "exception line exactly as logged" },
    "location": { "type": "string", "description": "file:line where it was raised" },
    "trigger": { "type": "string", "description": "the change that started it, with its timestamp" },
    "consequences": { "type": "array", "items": { "type": "string" }, "description": "services the failure propagated to" },
    "failed_requests": { "type": "integer" },
    "red_herrings": { "type": "array", "items": { "type": "string" } },
    "root_cause": { "type": "string" },
    "fix_plan": { "type": "array", "items": { "type": "string" }, "minItems": 2 }
  },
  "required": ["incident_start", "service", "exception", "location", "trigger", "consequences", "failed_requests", "red_herrings", "root_cause", "fix_plan"],
  "additionalProperties": false
}
EOF
cat > render_triage.py <<'EOF'
#!/usr/bin/env python3
"""render_triage.py <run.json> - turn the structured triage into TRIAGE.md. Exit 1 if the run has no structured output."""
import json
import sys

run = json.load(open(sys.argv[1]))
t = run.get("structured_output")
if run.get("subtype") != "success" or not isinstance(t, dict):
    sys.exit("triage: no structured output")
lines = ["# Incident triage", "",
         f"- **Started:** {t['incident_start']}",
         f"- **Service:** {t['service']}",
         f"- **Exception:** `{t['exception']}` at `{t['location']}`",
         f"- **Trigger:** {t['trigger']}",
         f"- **Propagated to:** {', '.join(t['consequences'])}",
         f"- **Failed checkout requests:** {t['failed_requests']}", "",
         "## Root cause", "", t["root_cause"], "",
         "## Fix plan", "", *[f"{i}. {s}" for i, s in enumerate(t["fix_plan"], 1)], "",
         "## Red herrings", "", *[f"- {r}" for r in t["red_herrings"]], ""]
open("TRIAGE.md", "w").write("\n".join(lines))
print("\n".join(lines))
EOF
claude -p 'Triage incident.log. Find the first error in the chain behind the failing POST /checkout requests, read its traceback, open the source line it points to, find what changed just before, count the failed checkout requests, and list unrelated errors as red herrings. Answer with evidence from the log and the code.' --allowedTools Read Grep "Bash(grep *)" --max-turns 10 --output-format json --json-schema "$(cat triage.schema.json)" < /dev/null > triage.json
python3 render_triage.py triage.json
```

</details>

## Check your work

```bash
D=/root/mastery/047-triage; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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

log = text("incident.log").splitlines()
chain = [l for l in log if " ERROR " in l and "req=" in l]
first = chain[0].split()[0] if chain else None
svc = chain[0].split()[1] if chain else None
exc = next((l.strip() for l in log if re.match(r"^\w+(Error|Exception): ", l.strip())), None)
frames = re.findall(r'File "([^"]+)", line (\d+)', "\n".join(log))
loc = f"{frames[1][0]}:{frames[1][1]}" if len(frames) > 1 else None
deploy = next((l for l in log if "deploy finished" in l), "")
ver = re.search(r"version=(\S+)", deploy).group(1) if deploy else None
failed = len({re.search(r"req=(\w+)", l).group(1) for l in log if " gateway ERROR " in l and " 502 " in l})
herring = next((l for l in log if " ERROR " in l and "req=" not in l), "")
run = load("triage.json") or {}
t = run.get("structured_output") or {}
sc = load("triage.schema.json") or {}
ok(set(sc.get("required") or []) >= {"incident_start", "service", "exception", "location", "trigger", "failed_requests", "fix_plan"}, "triage.schema.json requires every triage field", "triage.schema.json should require all the triage fields")
ok(run.get("subtype") == "success" and isinstance(t, dict) and t, "triage.json has a structured triage", "triage.json should be a --json-schema run with structured_output")
ok(t.get("incident_start") == first, f"incident start is the first error in the checkout chain ({first})", f"incident_start should be {first}, not {t.get('incident_start')!r} - the smtp error is not on the checkout path")
ok(t.get("service") == svc, f"the failing service is {svc}", f"service should be {svc} - got {t.get('service')!r}")
ok(t.get("exception") == exc, f"the exception is quoted exactly: {exc}", f"exception should be {exc!r} - got {t.get('exception')!r}")
src_line = ""
if loc:
    f_, n_ = loc.rsplit(":", 1)
    src = text(f_).splitlines()
    src_line = src[int(n_) - 1] if len(src) >= int(n_) else ""
ok(t.get("location") == loc and "currency" in src_line, f"the location {loc} matches the traceback and the source line", f"location should be {loc} (the innermost frame) - got {t.get('location')!r}")
ok(ver and ver in str(t.get("trigger", "")), f"the trigger names the {ver} deploy", f"trigger should name the deploy just before the first error ({ver})")
cons = {c.lower() for c in t.get("consequences") or []}
ok({"orders", "gateway"} <= cons, "consequences include orders and gateway", f"the failure propagated to orders and gateway - got {sorted(cons)}")
ok(t.get("failed_requests") == failed, f"failed_requests is {failed}", f"count the distinct checkout requests that got a 502 - expected {failed}, got {t.get('failed_requests')!r}")
rh = " ".join(t.get("red_herrings") or []).lower()
ok("smtp" in rh or (herring and herring.split()[0] in rh), "the smtp error is listed as a red herring", "list the unrelated worker smtp error under red_herrings")
fp = t.get("fix_plan") or []
ok(len(fp) >= 2 and any("currency" in s.lower() or "validat" in s.lower() for s in fp) and any("roll" in s.lower() or "revert" in s.lower() or "default" in s.lower() for s in fp),
   "the fix plan has a mitigation and a durable fix", "fix_plan needs an immediate mitigation (roll back or default) and a durable fix (validate currency)")
md = text("TRIAGE.md")
ok(md and str(t.get("location")) in md and str(t.get("incident_start")) in md and "## Fix plan" in md, "TRIAGE.md renders the triage", "render triage.json into TRIAGE.md with render_triage.py")
rows = transcript(run.get("session_id") or "none")[1]
looked = [u for u in uses(rows) if u.get("name") == "Read" and (u.get("input") or {}).get("file_path", "").endswith("payments/client.py")]
ok(looked, "Claude opened payments/client.py at the traceback's frame", "the triage run should open the source file the traceback points to")
PYEOF
```

## What you learned

- Triage finds the first error on the failing chain, not the loudest or the earliest overall.
- Read tracebacks bottom-up and confirm the frame in the source.
- A structured triage with evidence can be checked field by field.
