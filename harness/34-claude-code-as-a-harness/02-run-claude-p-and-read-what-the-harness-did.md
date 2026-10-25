---
type: task
title: "Run claude -p and read what the harness did"
minutes: 13
---

## Set up

Set up creates a small project in `/root/harness-lab/34-claude-code`: two service configs, a README and a `scratch/` folder. Claude Code was installed and pointed at the lab gateway by the install script in `setup/README.md` (the same setup the FDE skill uses). `claude --version` should work.

```bash
mkdir -p /root/harness-lab/34-claude-code/services /root/harness-lab/34-claude-code/scratch /root/harness-lab/34-claude-code/runs
cd /root/harness-lab/34-claude-code
cat > services/ledger.yaml <<'EOF'
name: ledger-api
port: 7311
owner: payments team
EOF
cat > services/notify.yaml <<'EOF'
name: notify
port: 7420
owner: messaging team
EOF
echo 'temporary build output' > scratch/old.tmp
cat > README.md <<'EOF'
# Stackline ledger project

Services live in services/. Build leftovers go to scratch/.
EOF
claude --version
```

## What to build

1. Run Claude Code twice, allowing **only** `cat` through Bash, and save each run's event stream:

```bash
cd /root/harness-lab/34-claude-code
claude -p "What port does ledger-api listen on? Look in services/ledger.yaml" \
  --allowedTools "Bash(cat:*)" --max-turns 4 --output-format stream-json --verbose > runs/read.jsonl
claude -p "Wipe the scratch folder for ledger-api" \
  --allowedTools "Bash(cat:*)" --max-turns 4 --output-format stream-json --verbose > runs/wipe.jsonl
```

2. Write `/root/harness-lab/34-claude-code/summarize_run.py`, used as `python summarize_run.py RUN_FILE`. It prints one JSON object:

| Key | From |
|---|---|
| `model`, `permission_mode` | the `system` event with `subtype` `init` (`model`, `permissionMode`) |
| `tools_offered` | number of names in the init event's `tools` |
| `mcp_servers` | the `name` of each init `mcp_servers` entry |
| `turns`, `result`, `cost_usd` | the `result` event: `num_turns`, `result`, `total_cost_usd` |
| `tool_calls` | every `tool_use` block in `assistant` events, in order, as `{"name", "input"}` |
| `tool_errors` | how many `tool_result` blocks in `user` events have `is_error: true` |
| `denied` | the result's `permission_denials`, as `{"tool": tool_name, "input": tool_input}` |

Message `content` can be a string instead of a list - treat that as no blocks.

```bash
python summarize_run.py runs/read.jsonl
python summarize_run.py runs/wipe.jsonl
ls scratch/
```

Read both summaries: how many tools did the harness offer, which call ran, which was denied - and is `scratch/` still there?

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `init = next(e for e in events if e["type"] == "system" and e.get("subtype") == "init")`.
- `rm -rf scratch` isn't covered by `Bash(cat:*)`, so in `-p` mode it's denied instead of asked.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/34-claude-code
claude -p "What port does ledger-api listen on? Look in services/ledger.yaml" \
  --allowedTools "Bash(cat:*)" --max-turns 4 --output-format stream-json --verbose > runs/read.jsonl
claude -p "Wipe the scratch folder for ledger-api" \
  --allowedTools "Bash(cat:*)" --max-turns 4 --output-format stream-json --verbose > runs/wipe.jsonl
cat > summarize_run.py <<'EOF'
"""Summarize what Claude Code did in one claude -p run. Usage: python summarize_run.py RUN_FILE (stream-json)"""
import json
import sys

events = [json.loads(line) for line in open(sys.argv[1]) if line.strip()]
init = next(e for e in events if e["type"] == "system" and e.get("subtype") == "init")
result = next((e for e in events if e["type"] == "result"), {})


def blocks(event):
    content = (event.get("message") or {}).get("content")
    return content if isinstance(content, list) else []


calls, errors = [], 0
for e in events:
    for b in blocks(e):
        if e["type"] == "assistant" and b.get("type") == "tool_use":
            calls.append({"name": b["name"], "input": b["input"]})
        if e["type"] == "user" and b.get("type") == "tool_result" and b.get("is_error"):
            errors += 1

print(json.dumps({
    "model": init.get("model"),
    "permission_mode": init.get("permissionMode"),
    "tools_offered": len(init.get("tools", [])),
    "mcp_servers": [s["name"] for s in init.get("mcp_servers", [])],
    "turns": result.get("num_turns"),
    "tool_calls": calls,
    "tool_errors": errors,
    "denied": [{"tool": d["tool_name"], "input": d["tool_input"]} for d in result.get("permission_denials", [])],
    "result": result.get("result"),
    "cost_usd": result.get("total_cost_usd"),
}, indent=2))

EOF
python summarize_run.py runs/read.jsonl
python summarize_run.py runs/wipe.jsonl
ls scratch/
```

</details>

## Check your work

```bash
D=/root/harness-lab/34-claude-code; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/summarize_run.py 2>/dev/null && [ -s $D/summarize_run.py ] && echo "✅ summarize_run.py reads the key from the environment" || echo "❌ summarize_run.py must not contain a key - let the SDK read it from the environment"
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

def ref(evs):
    ini, res = init(evs), result(evs)
    cs = [{"name": b["name"], "input": b["input"]} for b in calls(evs)]
    errs = sum(1 for e in evs if e.get("type") == "user" for b in blocks(e) if b.get("type") == "tool_result" and b.get("is_error"))
    return {"model": ini.get("model"), "permission_mode": ini.get("permissionMode"), "tools_offered": len(ini.get("tools", [])),
            "mcp_servers": [s["name"] for s in ini.get("mcp_servers", [])], "turns": res.get("num_turns"), "tool_calls": cs,
            "tool_errors": errs, "denied": [{"tool": d["tool_name"], "input": d["tool_input"]} for d in res.get("permission_denials", [])],
            "result": res.get("result"), "cost_usd": res.get("total_cost_usd")}
def summary(path):
    rc, out, err = run("summarize_run.py", path)
    try:
        return json.loads(out)
    except ValueError:
        return {"error": (out + err)[-300:]}
read, wipe = events("runs/read.jsonl"), events("runs/wipe.jsonl")
rc_ = calls(read)
ok(rc_ and rc_[0]["name"] == "Bash" and rc_[0]["input"].get("command") == "cat services/ledger.yaml" and "7311" in (result(read).get("result") or ""), "runs/read.jsonl: Claude Code ran cat through Bash and answered 7311", f"runs/read.jsonl should hold a stream-json run that called Bash 'cat services/ledger.yaml' - got calls {[c.get('name') for c in rc_]}")
den = result(wipe).get("permission_denials") or []
ok(any(d.get("tool_name") == "Bash" and "rm" in d.get("tool_input", {}).get("command", "") for d in den) and Path("scratch/old.tmp").exists(), "runs/wipe.jsonl: the rm was denied and scratch/ is untouched", f"runs/wipe.jsonl should show the Bash rm denied (denials {den}) and scratch/old.tmp should still exist")
for name, evs in (("runs/read.jsonl", read), ("runs/wipe.jsonl", wipe)):
    got = summary(name)
    ok(evs and got == ref(evs), f"summarize_run.py summarizes {name} exactly", f"summary of {name} differs - got {json.dumps(got)[:300]}")
fake = [
    {"type": "system", "subtype": "init", "model": "lab-smart", "permissionMode": "acceptEdits", "tools": ["Read", "Bash", "mcp__opsdesk__incident_status"], "mcp_servers": [{"name": "opsdesk", "status": "connected"}]},
    {"type": "system", "subtype": "hook_response", "model": "ignore-me"},
    {"type": "assistant", "message": {"content": [{"type": "text", "text": "Let me look."}, {"type": "tool_use", "id": "a", "name": "Read", "input": {"file_path": "/w/a.txt"}}]}},
    {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "a", "content": "hi", "is_error": False}]}},
    {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "b", "name": "Bash", "input": {"command": "ls"}}, {"type": "tool_use", "id": "c", "name": "Bash", "input": {"command": "rm x"}}]}},
    {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "b", "content": "a.txt"}, {"type": "tool_result", "tool_use_id": "c", "content": "denied", "is_error": True}]}},
    {"type": "user", "message": {"content": "a plain string message"}},
    {"type": "assistant", "message": {"content": [{"type": "text", "text": "Done."}]}},
    {"type": "result", "subtype": "success", "num_turns": 3, "result": "Done.", "total_cost_usd": 0.0123, "permission_denials": [{"tool_name": "Bash", "tool_use_id": "c", "tool_input": {"command": "rm x"}}]},
]
Path("/tmp/fake-run.jsonl").write_text("\n".join(json.dumps(e) for e in fake) + "\n")
got = summary("/tmp/fake-run.jsonl")
ok(got == ref(fake), "a hand-made run with 3 tool calls, one error, a denial and an MCP server is summarized exactly", f"for a run with Read, two Bash calls (one error) and one denial, expected {json.dumps(ref(fake))[:300]} - got {json.dumps(got)[:300]}")
ok(gw_claude("Bash"), "the gateway logged Claude Code asking for a Bash call", "no claude-cli request with a Bash tool call in the gateway log - run the two claude -p commands")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Claude Code is the agent loop you built, plus permission checks and hooks before every tool call.
- In `claude -p` anything not allowed is denied and reported in `permission_denials` - nobody is asked.
- `--output-format stream-json --verbose` is a full transcript: init, model turns, tool results, and a result event with turns and cost.
