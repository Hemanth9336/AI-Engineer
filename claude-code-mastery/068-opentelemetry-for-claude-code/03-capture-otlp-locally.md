---
type: task
title: "Capture OTLP locally"
minutes: 20
---

## Set up

Set up creates `/root/mastery/068-otel` with a `notes.txt` to run one small task on.

```bash
rm -rf /root/mastery/068-otel && mkdir -p /root/mastery/068-otel && cd /root/mastery/068-otel
cat > notes.txt <<'EOF'
Meeting notes: the team agreed to move the weekly sync to Thursdays.
EOF
jq --version
```

## What to build

1. Write `collector.py PORT OUTDIR`, an HTTP server on `127.0.0.1`. It saves each POST to `/v1/metrics`, `/v1/logs` and `/v1/traces` as `OUTDIR/<signal>-<n>.json`, and answers `200 {}`.
2. Write `otel-run.sh PROMPT`. It runs `claude -p` (`--tools Read --max-turns 3 --output-format json`, saving `run.json`) with:
   - telemetry enabled;
   - the metrics, logs and traces exporters set to `otlp` (traces need the beta switch);
   - `http/json` to `http://127.0.0.1:14318`, with short export intervals;
   - `OTEL_RESOURCE_ATTRIBUTES="team=platform,lab=068"`;
   - every `OTEL_LOG_*` content switch left **off**.
3. Write `signals.py [OTLP_DIR]`. It writes `signals.json` with sorted `metrics`, `events` (the `event.name` values), `spans`, `resource` (`team`, `lab` and `service.name`), and `session_ids`. Skip unparsable files and name them on stderr.
4. Start the collector in the background, run the prompt below, wait a few seconds, stop the collector by its PID, then run `signals.py`:
   > Read notes.txt and say in one sentence what it is about. Context: Acme renewal: pricing tier Q-7741.

The checker confirms the prompt's context line never reached the collector, and runs `signals.py` on hidden payloads.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Exports are batched: lower `OTEL_METRIC_EXPORT_INTERVAL` and `OTEL_LOGS_EXPORT_INTERVAL`, and sleep a moment before stopping the collector.
- OTLP JSON attributes are lists of `{"key": ..., "value": {"stringValue": ...}}`. Take the one value in each `value` dict.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/068-otel
cat > collector.py <<'EOF'
#!/usr/bin/env python3
"""collector.py PORT OUTDIR - a minimal OTLP/HTTP JSON collector: saves each POST body as OUTDIR/<signal>-<n>.json."""
import itertools
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

port, out = int(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
counter = itertools.count(1)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        signal = self.path.rstrip("/").rsplit("/", 1)[-1]          # /v1/metrics -> metrics
        if signal in ("metrics", "logs", "traces"):
            (out / f"{signal}-{next(counter):04d}.json").write_bytes(body)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b"{}")


HTTPServer(("127.0.0.1", port), Handler).serve_forever()
EOF
cat > otel-run.sh <<'EOF'
#!/usr/bin/env bash
# otel-run.sh PROMPT - one headless run with OTLP metrics, events, and traces sent to the local collector.
set -euo pipefail
cd "$(dirname "$0")"
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp OTEL_LOGS_EXPORTER=otlp OTEL_TRACES_EXPORTER=otlp
export CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1
export OTEL_EXPORTER_OTLP_PROTOCOL=http/json
export OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:14318
export OTEL_METRIC_EXPORT_INTERVAL=1000 OTEL_LOGS_EXPORT_INTERVAL=500
export OTEL_RESOURCE_ATTRIBUTES="team=platform,lab=068"
unset OTEL_LOG_USER_PROMPTS OTEL_LOG_TOOL_DETAILS OTEL_LOG_TOOL_CONTENT OTEL_LOG_ASSISTANT_RESPONSES OTEL_LOG_RAW_API_BODIES
claude -p "${1:?usage: otel-run.sh PROMPT}" --tools Read --max-turns 3 --output-format json < /dev/null > run.json
jq -r '.result' run.json
EOF
cat > signals.py <<'EOF'
#!/usr/bin/env python3
"""signals.py [OTLP_DIR] - list the metric, event, and span names a collector received, plus the attributes on them."""
import json
import sys
from pathlib import Path

d = Path(sys.argv[1] if len(sys.argv) > 1 else "otlp")
metrics, events, spans, resource, sessions = set(), set(), set(), {}, set()


def attrs(items):
    out = {}
    for a in items or []:
        v = a.get("value") or {}
        out[a.get("key")] = next(iter(v.values()), None) if v else None
    return out


for f in sorted(d.glob("*.json")):
    try:
        doc = json.loads(f.read_text())
    except ValueError:
        print(f"skipped: {f}", file=sys.stderr)
        continue
    for kind, scopes, items in (("resourceMetrics", "scopeMetrics", "metrics"), ("resourceLogs", "scopeLogs", "logRecords"),
                                ("resourceSpans", "scopeSpans", "spans")):
        for r in doc.get(kind, []):
            resource.update(attrs((r.get("resource") or {}).get("attributes")))
            for s in r.get(scopes, []):
                for item in s.get(items, []):
                    if kind == "resourceMetrics":
                        metrics.add(item["name"])
                    elif kind == "resourceLogs":
                        a = attrs(item.get("attributes"))
                        events.add(a.get("event.name"))
                        sessions.add(a.get("session.id"))
                    else:
                        spans.add(item["name"])

out = {"metrics": sorted(metrics), "events": sorted(e for e in events if e), "spans": sorted(spans),
       "resource": {k: resource[k] for k in sorted(resource) if k in ("service.name", "team", "lab")},
       "session_ids": sorted(s for s in sessions if s)}
Path("signals.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
EOF
chmod +x collector.py otel-run.sh signals.py
rm -rf otlp
python3 collector.py 14318 otlp & echo $! > collector.pid
sleep 1
./otel-run.sh 'Read notes.txt and say in one sentence what it is about. Context: Acme renewal: pricing tier Q-7741.'
sleep 3
kill "$(cat collector.pid)" && rm collector.pid
python3 signals.py otlp
```

</details>

## Check your work

```bash
D=/root/mastery/068-otel; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
SECRET = 'Acme renewal: pricing tier Q-7741'
PORT = 14318

import shutil, socket, time
files = sorted(glob.glob("otlp/*.json"))
kinds = {Path(f).name.split("-")[0] for f in files}
ok(kinds >= {"metrics", "logs", "traces"}, "the collector saved metrics, logs, and traces payloads in otlp/", f"run collector.py, then ./otel-run.sh with all three exporters - otlp/ has {sorted(kinds)}")
sig = load("signals.json") or {}
need_m = {"claude_code.session.count", "claude_code.cost.usage", "claude_code.token.usage"}
ok(need_m <= set(sig.get("metrics") or []), "signals.json lists the session, cost, and token metrics", f"metrics should include {sorted(need_m)} - got {sig.get('metrics')}")
ok({"user_prompt", "api_request"} <= set(sig.get("events") or []) and "claude_code.interaction" in (sig.get("spans") or []),
   "signals.json lists the user_prompt and api_request events and the interaction span", f"events {sig.get('events')}, spans {sig.get('spans')}")
run = load("run.json") or {}
ok(run.get("session_id") and sig.get("session_ids") == [run["session_id"]] and (sig.get("resource") or {}).get("team") == "platform",
   "events carry the run's session id, and your resource attribute team=platform arrived", f"signals.json session_ids {sig.get('session_ids')} vs run.json {run.get('session_id')}, resource {sig.get('resource')}")
blob = "".join(text(f) for f in files)
ok(files and SECRET not in blob and "<REDACTED>" in blob, "the prompt text never left the machine - user_prompt arrived redacted",
   "leave OTEL_LOG_USER_PROMPTS unset so prompts are exported as <REDACTED>")
src = text("otel-run.sh")
ok(not re.search(r"^\s*export\s+[^#\n]*OTEL_LOG_(USER_PROMPTS|TOOL_CONTENT|ASSISTANT_RESPONSES|RAW_API_BODIES)=1", src, re.M) and "CLAUDE_CODE_ENABLE_TELEMETRY=1" in src,
   "otel-run.sh enables telemetry without turning on any content logging", "set CLAUDE_CODE_ENABLE_TELEMETRY=1 and don't export OTEL_LOG_* content switches")
s = socket.socket()
busy = s.connect_ex(("127.0.0.1", PORT)) == 0
s.close()
ok(not busy, f"the collector was stopped afterwards (port {PORT} is free)", f"stop your collector when the run is done - something still listens on {PORT}")
with tempfile.TemporaryDirectory() as t:
    shutil.copy("signals.py", t)
    Path(t, "o").mkdir()
    Path(t, "o", "metrics-1.json").write_text(json.dumps({"resourceMetrics": [{"resource": {"attributes": [{"key": "team", "value": {"stringValue": "x"}}]},
        "scopeMetrics": [{"metrics": [{"name": "claude_code.lines_of_code.count"}]}]}]}))
    Path(t, "o", "logs-2.json").write_text(json.dumps({"resourceLogs": [{"scopeLogs": [{"logRecords": [{"attributes": [
        {"key": "event.name", "value": {"stringValue": "tool_result"}}, {"key": "session.id", "value": {"stringValue": "s-9"}}]}]}]}]}))
    Path(t, "o", "traces-3.json").write_text("{truncated")
    rc, so_, se = sh([sys.executable, "signals.py", "o"], cwd=t)
    h = load(Path(t, "signals.json")) or {}
    ok(rc == 0 and h.get("metrics") == ["claude_code.lines_of_code.count"] and h.get("events") == ["tool_result"] and h.get("session_ids") == ["s-9"] and "traces-3" in se,
       "signals.py on hidden payloads: names extracted, the truncated file skipped and named", f"signals.py DIR should parse OTLP JSON and skip bad files - rc {rc}, got {h}, stderr {se.strip()[:100]!r}")
PYEOF
```

## What you learned

- CLAUDE_CODE_ENABLE_TELEMETRY plus the OTEL_* exporter variables send metrics, events, and (beta) traces to any OTLP collector.
- Signals carry session.id and your OTEL_RESOURCE_ATTRIBUTES, so you can slice cost and usage by team without touching content.
- Prompts are exported redacted by default; every OTEL_LOG_* switch you turn on sends real content to your backend.
