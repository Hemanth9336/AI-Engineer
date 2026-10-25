---
type: task
title: "Capture run metrics"
minutes: 30
---

## Set up

Set up creates `/root/mastery/066-obs` with a `CHANGES.md` and an `issue.txt` for two small flows.

```bash
rm -rf /root/mastery/066-obs && mkdir -p /root/mastery/066-obs && cd /root/mastery/066-obs
cat > CHANGES.md <<'EOF'
# Changes

- Added CSV export to the reports page.
- Fixed a crash when the cache directory is missing.
- Raised the upload limit to 50 MB.
EOF
cat > issue.txt <<'EOF'
Title: Upload fails for 60 MB video

Uploading a 60 MB file shows 'Request Entity Too Large'. Expected: a clear message about the 50 MB limit.
EOF
jq --version
```

## What to build

1. Write `run.sh FLOW -- CLAUDE_ARGS...`.
   - Run `claude <args> --output-format json` and save the envelope under `metrics/envelopes/`.
   - Append one row to `metrics/runs.jsonl`: `ts`, `flow`, `session_id`, `exit_code`, `subtype`, `is_error`, `cost_usd`, `duration_ms`, `num_turns`, `input_tokens`, `output_tokens`, `cache_read_tokens`, `models`, and `envelope` (the saved file's path).
   - Print `.result`, and exit with `claude`'s exit code.
   - If the output isn't a JSON envelope, still log a row with `subtype: "unparsable"` and exit non-zero.
2. Write `report.sh [RUNS_JSONL]`. It writes `metrics/report.json`: per flow, `runs`, `errors`, `cost_usd`, and `avg_duration_ms` (floored), most expensive first.
3. Run two flows, then `./report.sh`:
   - `./run.sh summarize -- -p 'Summarize CHANGES.md in one sentence.' --tools Read --max-turns 3`, twice.
   - `./run.sh triage -- -p 'Label the issue in issue.txt as bug, feature, or question. Reply with the label only.' --tools Read --max-turns 3`, once.

The checker runs copies of your wrapper with a `claude` that fails and one that prints garbage, and runs `report.sh` on hidden rows.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `jq -e 'type == "object"' file` fails both on invalid JSON and on JSON that isn't an object.
- `jq -s 'group_by(.flow) | map({flow: .[0].flow, runs: length, ...}) | sort_by(-.cost_usd)'` does the whole report.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/066-obs
cat > run.sh <<'EOF'
#!/usr/bin/env bash
# run.sh FLOW -- CLAUDE_ARGS... - run claude, keep its envelope, log one metrics row, print the result, keep the exit code.
set -uo pipefail
cd "$(dirname "$0")"
flow=${1:?usage: run.sh FLOW -- CLAUDE_ARGS...}
shift
[ "${1:-}" = "--" ] && shift
mkdir -p metrics/envelopes
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
n=$(( $(wc -l 2> /dev/null < metrics/runs.jsonl || echo 0) + 1 ))
envf="metrics/envelopes/$flow-$(date -u +%Y%m%dT%H%M%SZ)-$n.json"
rc=0
claude "$@" --output-format json < /dev/null > "$envf" || rc=$?

if jq -e 'type == "object"' "$envf" > /dev/null 2>&1; then
  jq -c --arg ts "$ts" --arg flow "$flow" --argjson rc "$rc" --arg env "$envf" '{
      ts: $ts, flow: $flow, session_id, exit_code: $rc, subtype, is_error,
      cost_usd: (.total_cost_usd // 0), duration_ms, num_turns,
      input_tokens: .usage.input_tokens, output_tokens: .usage.output_tokens,
      cache_read_tokens: .usage.cache_read_input_tokens, models: ((.modelUsage // {}) | keys), envelope: $env}' "$envf" >> metrics/runs.jsonl
  jq -r '.result // empty' "$envf"
else
  jq -nc --arg ts "$ts" --arg flow "$flow" --argjson rc "$rc" --arg env "$envf" \
    '{ts: $ts, flow: $flow, session_id: null, exit_code: $rc, subtype: "unparsable", is_error: true, cost_usd: 0, envelope: $env}' >> metrics/runs.jsonl
  echo "run.sh: claude output was not a JSON envelope (see $envf)" >&2
  [ "$rc" = 0 ] && rc=1
fi
exit "$rc"
EOF
cat > report.sh <<'EOF'
#!/usr/bin/env bash
# report.sh [RUNS_JSONL] - per-flow totals, most expensive first, to stdout and metrics/report.json
set -euo pipefail
cd "$(dirname "$0")"
runs=${1:-metrics/runs.jsonl}
mkdir -p metrics
jq -s 'group_by(.flow) | map({
    flow: .[0].flow, runs: length, errors: (map(select(.is_error)) | length),
    cost_usd: (map(.cost_usd // 0) | add), avg_duration_ms: ((map(.duration_ms // 0) | add) / length | floor)})
  | sort_by(-.cost_usd)' "$runs" > metrics/report.json
jq -r '.[] | "\(.flow)\t\(.runs) runs\t\(.errors) errors\t$\(.cost_usd)\t\(.avg_duration_ms) ms avg"' metrics/report.json
EOF
chmod +x run.sh report.sh
./run.sh summarize -- -p 'Summarize CHANGES.md in one sentence.' --tools Read --max-turns 3
./run.sh summarize -- -p 'Summarize CHANGES.md in one sentence.' --tools Read --max-turns 3
./run.sh triage -- -p 'Label the issue in issue.txt as bug, feature, or question. Reply with the label only.' --tools Read --max-turns 3
./report.sh
```

</details>

## Check your work

```bash
D=/root/mastery/066-obs; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
def envelope(sid, err=False, cost=0.01, turns=2, result="done"):
    return json.dumps({"type": "result", "subtype": "error_during_execution" if err else "success", "is_error": err, "result": result,
                       "session_id": sid, "num_turns": turns, "duration_ms": 1200, "total_cost_usd": cost,
                       "usage": {"input_tokens": 1000, "output_tokens": 50, "cache_read_input_tokens": 200}, "modelUsage": {"lab-fast": {}}})

import shutil
rows = events("metrics/runs.jsonl")
ok([r.get("flow") for r in rows] == ["summarize", "summarize", "triage"], "metrics/runs.jsonl has a row for each of the three runs", f"run the three commands through ./run.sh - flows {[r.get('flow') for r in rows]}")
good = True
for r in rows:
    e = load(r.get("envelope") or "") or {}
    good = good and e.get("session_id") == r.get("session_id") and r.get("cost_usd") == e.get("total_cost_usd") and r.get("num_turns") == e.get("num_turns") \
        and r.get("input_tokens") == (e.get("usage") or {}).get("input_tokens") and r.get("exit_code") == 0 and r.get("ts")
ok(rows and good, "each row matches its saved envelope: session, cost, turns, tokens, exit code", "copy the fields from the envelope you saved under metrics/envelopes/ and keep its path in envelope")
rep = load("metrics/report.json") or []
ok([x.get("flow") for x in rep] and {x.get("flow"): x.get("runs") for x in rep} == {"summarize": 2, "triage": 1},
   "metrics/report.json totals the runs per flow", f"./report.sh should group runs.jsonl by flow - got {rep}")
def copy(t):
    shutil.copy("run.sh", t); shutil.copy("report.sh", t)
with tempfile.TemporaryDirectory() as t:
    copy(t)
    rc, so_, se = sh(["./run.sh", "nightly", "--", "-p", "x"], cwd=t, env=stub(t, "echo '" + envelope("s-boom", err=True, cost=0.2) + "'; exit 1"))
    r = events(Path(t, "metrics/runs.jsonl"))
    ok(rc == 1 and r and r[-1].get("is_error") is True and r[-1].get("exit_code") == 1 and r[-1].get("session_id") == "s-boom" and r[-1].get("cost_usd") == 0.2,
       "a failed run is logged with its error, session, and cost, and run.sh exits 1", f"log failures too and pass claude's exit code through - rc {rc}, rows {r}")
    rc, so_, se = sh(["./run.sh", "nightly", "--", "-p", "x"], cwd=t, env=stub(t, "echo 'Segmentation fault'; exit 0"))
    r = events(Path(t, "metrics/runs.jsonl"))
    ok(rc != 0 and len(r) == 2 and r[-1].get("subtype") == "unparsable", "output that isn't an envelope still gets a row (subtype unparsable) and a non-zero exit",
       f"never drop a run - rc {rc}, rows {len(r)}, last {r[-1:] }")
    rc, so_, se = sh(["./run.sh", "nightly", "--", "-p", "x"], cwd=t, env=stub(t, "echo '" + envelope("s-ok", result="the answer") + "'"))
    ok(rc == 0 and so_.strip() == "the answer", "on success run.sh prints just the result text", f"print .result to stdout - got {so_.strip()[:80]!r}")
with tempfile.TemporaryDirectory() as t:
    copy(t)
    Path(t, "m.jsonl").write_text("".join(json.dumps(x) + "\n" for x in [
        {"flow": "a", "is_error": False, "cost_usd": 0.10, "duration_ms": 1000}, {"flow": "b", "is_error": True, "cost_usd": 0.50, "duration_ms": 3000},
        {"flow": "a", "is_error": False, "cost_usd": 0.20, "duration_ms": 2000}, {"flow": "c", "is_error": False, "cost_usd": 0.05, "duration_ms": 500}]))
    rc, so_, se = sh(["./report.sh", "m.jsonl"], cwd=t)
    rep = load(Path(t, "metrics/report.json")) or []
    ok([x.get("flow") for x in rep] == ["b", "a", "c"] and rep[0].get("errors") == 1 and abs(rep[1].get("cost_usd", 0) - 0.30) < 1e-9 and rep[1].get("avg_duration_ms") == 1500,
       "report.sh on hidden rows: most expensive flow first, with error counts and average duration", f"sort flows by cost (descending) with runs, errors, cost_usd, avg_duration_ms - got {rep}")
PYEOF
```

## What you learned

- Route every run through one wrapper that saves the envelope and appends a JSON Lines row, so no run goes unmeasured.
- Log failures and unreadable output too, and pass the exit code through so observability never hides errors.
- Aggregate with jq -s and group_by; follow session_id to the transcript for the why.
