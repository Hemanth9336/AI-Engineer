---
type: task
title: "Call your tool through claude -p"
minutes: 12
---

## Set up

```bash
mkdir -p /root/harness-lab/35-mcp/runs
cd /root/harness-lab/35-mcp
[ -f server.py ] && [ -f .mcp.json ] && echo 'server.py and .mcp.json found' || echo 'build and register the server first (previous task)'
```

## What to build

1. From the project folder, ask Claude Code about an incident, allowing only that one MCP tool. The project's `.mcp.json` loads your server:

```bash
cd /root/harness-lab/35-mcp
claude -p "Is INC-4471 still open? Ask opsdesk" --allowedTools mcp__opsdesk__incident_status \
  --max-turns 4 --output-format stream-json --verbose > runs/inc-4471.jsonl
jq -r 'select(.type == "result") | .result' runs/inc-4471.jsonl
```

2. Scripted runs (CI, evals) shouldn't depend on whatever servers happen to be registered. Write `/root/harness-lab/35-mcp/ci-mcp.json` with just `opsdesk` (absolute paths), then run from **another folder** with `--mcp-config ... --strict-mcp-config`:

```bash
cd /root/harness-lab/35-mcp
cat > ci-mcp.json <<EOF
{"mcpServers": {"opsdesk": {"command": "$(command -v python)", "args": ["/root/harness-lab/35-mcp/server.py"]}}}
EOF
cd /tmp
claude -p "Which opsdesk incidents are open right now?" --mcp-config /root/harness-lab/35-mcp/ci-mcp.json --strict-mcp-config \
  --allowedTools mcp__opsdesk__list_open_incidents --max-turns 4 > /root/harness-lab/35-mcp/open.txt
cat /root/harness-lab/35-mcp/open.txt
tail -3 /root/harness-lab/35-mcp/calls.log
```

`calls.log` proves both answers came through your server, not from the model's imagination.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `ci-mcp.json` has the same shape as `.mcp.json`: `{"mcpServers": {"opsdesk": {"command": ..., "args": [...]}}}`.
- `--strict-mcp-config` ignores every other MCP configuration - only the file's servers load.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/35-mcp
claude -p "Is INC-4471 still open? Ask opsdesk" --allowedTools mcp__opsdesk__incident_status \
  --max-turns 4 --output-format stream-json --verbose > runs/inc-4471.jsonl
jq -r 'select(.type == "result") | .result' runs/inc-4471.jsonl
cd /root/harness-lab/35-mcp
cat > ci-mcp.json <<EOF
{"mcpServers": {"opsdesk": {"command": "$(command -v python)", "args": ["/root/harness-lab/35-mcp/server.py"]}}}
EOF
cd /tmp
claude -p "Which opsdesk incidents are open right now?" --mcp-config /root/harness-lab/35-mcp/ci-mcp.json --strict-mcp-config \
  --allowedTools mcp__opsdesk__list_open_incidents --max-turns 4 > /root/harness-lab/35-mcp/open.txt
cat /root/harness-lab/35-mcp/open.txt
tail -3 /root/harness-lab/35-mcp/calls.log
```

</details>

## Check your work

```bash
D=/root/harness-lab/35-mcp; cd $D 2>/dev/null || echo "❌ create $D"
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
import tempfile
def claude(prompt, *flags, cwd="."):
    cmd = ["claude", "-p", prompt, *flags, "--max-turns", "6", "--output-format", "stream-json", "--verbose"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=240, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return 124, [], "timed out"
    ev = []
    for line in r.stdout.splitlines():
        try:
            ev.append(json.loads(line))
        except ValueError:
            pass
    return r.returncode, ev, r.stderr
def events(path):
    try:
        return [json.loads(l) for l in open(path) if l.strip()]
    except Exception:
        return []
def blocks(e):
    c = (e.get("message") or {}).get("content")
    return c if isinstance(c, list) else []
def calls(ev):
    return [b for e in ev if e.get("type") == "assistant" for b in blocks(e) if b.get("type") == "tool_use"]
def result(ev):
    return next((e for e in ev if e.get("type") == "result"), {})
def init(ev):
    return next((e for e in ev if e.get("type") == "system" and e.get("subtype") == "init"), {})
def gw_claude(tool):
    rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")]
    return any(str(x.get("client", "")).startswith("claude-cli") and tool in (x.get("tool_calls") or []) for x in rows)

ev = events("runs/inc-4471.jsonl")
cs = calls(ev)
ok(any(c["name"] == "mcp__opsdesk__incident_status" and c["input"].get("incident_id") == "INC-4471" for c in cs) and "mitigated" in (result(ev).get("result") or ""), "runs/inc-4471.jsonl: Claude Code called mcp__opsdesk__incident_status and answered from it", f"runs/inc-4471.jsonl should call mcp__opsdesk__incident_status for INC-4471 - got {[c.get('name') for c in cs]}")
ok("INC-4502" in Path("open.txt").read_text() if Path("open.txt").exists() else False, "open.txt lists the open incidents from list_open_incidents", "save the answer to 'Which opsdesk incidents are open right now?' to open.txt")
cfg = (load("ci-mcp.json") or {}).get("mcpServers", {})
ok(list(cfg) == ["opsdesk"] and str((cfg.get("opsdesk") or {}).get("command", "")).startswith("/"), "ci-mcp.json defines only opsdesk, with an absolute command", f"ci-mcp.json should define just opsdesk - got {list(cfg)}")
before = Path("calls.log").read_text().count("INC-4502") if Path("calls.log").exists() else 0
rc, ev, err = claude("What is the status of INC-4502? Ask opsdesk", "--mcp-config", str(Path("ci-mcp.json").resolve()), "--strict-mcp-config", "--allowedTools", "mcp__opsdesk__incident_status", cwd=tempfile.mkdtemp())
after = Path("calls.log").read_text().count("INC-4502") if Path("calls.log").exists() else 0
servers = [(s.get("name"), s.get("status")) for s in init(ev).get("mcp_servers", [])]
ok(servers == [("opsdesk", "connected")], "with --strict-mcp-config from another folder, only opsdesk loads and it connects", f"expected only opsdesk connected - got {servers} {err[-200:]}")
ok(rc == 0 and after > before and "investigat" in (result(ev).get("result") or ""), "a new question about INC-4502 went through your server and the answer uses its data", f"calls for INC-4502 {before}->{after}, answer {(result(ev).get('result') or '')[:200]!r}")
ok(gw_claude("mcp__opsdesk__incident_status"), "the gateway logged Claude Code calling mcp__opsdesk__incident_status", "no claude-cli request that called mcp__opsdesk__incident_status")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- MCP tools appear in the harness as `mcp__<server>__<tool>` and go through the same permission rules.
- `--mcp-config FILE --strict-mcp-config` gives scripted runs an exact, reproducible tool set.
- Check the server's own log to prove the answer came through your tool.
