---
type: task
title: "Capture an SDK run and its result metadata"
minutes: 23
---

## Set up

Set up creates `/root/mastery/059-sdk` with three incident write-ups in `docs/`, and confirms `claude-agent-sdk` imports.

```bash
rm -rf /root/mastery/059-sdk && mkdir -p /root/mastery/059-sdk/docs && cd /root/mastery/059-sdk
cat > docs/incident-1.md <<'EOF'
# Incident 1 - 12 September

The search index ran out of disk. Queries failed for 40 minutes until the old shards were deleted.
EOF
cat > docs/incident-2.md <<'EOF'
# Incident 2 - 3 October

Card payments failed for 25 minutes. Root cause: the TLS certificate on the payments gateway expired; renewal had been manual.
EOF
cat > docs/incident-3.md <<'EOF'
# Incident 3 - 19 October

A bad feature flag sent all traffic to the canary pool. Rolled back after 9 minutes.
EOF
python3 -c "import claude_agent_sdk as s; print('claude-agent-sdk', s.__version__)"
```

## What to build

1. Write `run_agent.py [--max-turns N] [--out FILE] PROMPT`, using `claude_agent_sdk.query` (don't shell out to `claude`).
   - Options: `cwd` = the script's folder, `allowed_tools` `Read`, `Glob`, `Grep`, `disallowed_tools` `Bash`, `Write`, `Edit`, `max_turns` (default 8), and `max_budget_usd` 0.50.
   - Write `transcript.jsonl`, one JSON row per message:
     - `system`, with its `session_id`.
     - `assistant`, with its text and tool names.
     - `user`, with its tool-result error flags.
     - `result`.
   - Write `--out` (default `result.json`) from the `ResultMessage`. Fields: `subtype`, `is_error`, `result`, `num_turns`, `duration_ms`, `total_cost_usd`, `input_tokens`, `output_tokens`, `session_id`, and `tools_used` (every tool name, in order).
   - Exit codes:
     - 0 on success, 1 on an error result.
     - 2 when no result arrived at all; write `{"subtype": "no_result", ...}` in that case.
2. Run it and keep `result.json`:
   > Using the files in docs/, which incident was caused by an expired certificate? Answer in one sentence.

The checker re-runs your script with `--max-turns 1`. That should give exit 1 and an `error_max_turns` file, not a traceback. It also sends a prompt that makes the model try Bash.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- On an error result the SDK yields the ResultMessage and then raises ResultError. Save the message inside the loop, and catch the exception around it.
- `ResultMessage.usage` is a plain dict; `.get("input_tokens")` reads it.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/059-sdk
cat > run_agent.py <<'EOF'
#!/usr/bin/env python3
"""run_agent.py [--max-turns N] [--out FILE] PROMPT - a read-only agent over this folder that records every run."""
import argparse
import asyncio
import json
import sys
from pathlib import Path

from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions, ClaudeSDKError, ResultError, ResultMessage,
                              SystemMessage, TextBlock, ToolResultBlock, ToolUseBlock, UserMessage, query)

HERE = Path(__file__).resolve().parent


def row(m):
    if isinstance(m, SystemMessage):
        return {"kind": "system", "subtype": m.subtype, "session_id": m.data.get("session_id")}
    if isinstance(m, AssistantMessage):
        return {"kind": "assistant",
                "text": "".join(b.text for b in m.content if isinstance(b, TextBlock)),
                "tools": [b.name for b in m.content if isinstance(b, ToolUseBlock)]}
    if isinstance(m, UserMessage):
        blocks = m.content if isinstance(m.content, list) else []
        return {"kind": "user", "tool_errors": [bool(b.is_error) for b in blocks if isinstance(b, ToolResultBlock)]}
    if isinstance(m, ResultMessage):
        return {"kind": "result", "subtype": m.subtype, "is_error": m.is_error}
    return {"kind": type(m).__name__}


async def run(prompt, max_turns):
    opts = ClaudeAgentOptions(cwd=str(HERE), allowed_tools=["Read", "Glob", "Grep"],
                              disallowed_tools=["Bash", "Write", "Edit"], max_turns=max_turns, max_budget_usd=0.50)
    tools, final, error = [], None, None
    with open(HERE / "transcript.jsonl", "w") as log:
        try:
            async for m in query(prompt=prompt, options=opts):
                r = row(m)
                tools += r.get("tools", [])
                log.write(json.dumps(r) + "\n")
                if isinstance(m, ResultMessage):
                    final = m
        except ResultError:
            pass
        except ClaudeSDKError as e:
            error = str(e)
    return final, tools, error


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-turns", type=int, default=8)
    ap.add_argument("--out", default=str(HERE / "result.json"))
    ap.add_argument("prompt")
    a = ap.parse_args()
    final, tools, error = asyncio.run(run(a.prompt, a.max_turns))
    if final is None:
        Path(a.out).write_text(json.dumps({"subtype": "no_result", "is_error": True, "error": error}, indent=2) + "\n")
        print(f"no result: {error}", file=sys.stderr)
        return 2
    usage = final.usage or {}
    out = {"subtype": final.subtype, "is_error": final.is_error, "result": final.result,
           "num_turns": final.num_turns, "duration_ms": final.duration_ms, "total_cost_usd": final.total_cost_usd,
           "input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens"),
           "session_id": final.session_id, "tools_used": tools}
    Path(a.out).write_text(json.dumps(out, indent=2) + "\n")
    print(final.result if final.result is not None else f"run ended: {final.subtype}")
    return 1 if final.is_error else 0


if __name__ == "__main__":
    sys.exit(main())
EOF
chmod +x run_agent.py
python3 run_agent.py 'Using the files in docs/, which incident was caused by an expired certificate? Answer in one sentence.'
cat result.json
```

</details>

## Check your work

```bash
D=/root/mastery/059-sdk; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
res = load("result.json") or {}
ok(res.get("subtype") == "success" and res.get("is_error") is False and "TLS" in str(res.get("result")),
   "result.json: a successful run that names the TLS certificate incident", f"run python3 run_agent.py with the task prompt and save the ResultMessage to result.json - got {str(res)[:200]}")
ok(isinstance(res.get("total_cost_usd"), (int, float)) and res["total_cost_usd"] > 0 and isinstance(res.get("input_tokens"), int)
   and isinstance(res.get("output_tokens"), int) and isinstance(res.get("num_turns"), int) and res["num_turns"] >= 2 and isinstance(res.get("duration_ms"), int),
   "result.json records cost, tokens, turns, and duration from the ResultMessage", "copy total_cost_usd, usage input_tokens and output_tokens, num_turns, and duration_ms into result.json")
ok(res.get("tools_used") == ["Glob", "Read"], "tools_used lists the tool calls in order (Glob, then Read)", f"collect ToolUseBlock names from each AssistantMessage into tools_used - got {res.get('tools_used')}")
sid = res.get("session_id") or ""
mine = [rows for rows in sessions(".") if any(r.get("sessionId") == sid for r in rows)]
ok(sid and mine, "session_id matches the saved session transcript", f"session_id should be the ResultMessage session_id - no session {sid!r} found for this folder")
tr = events("transcript.jsonl")
ok(len(tr) >= 4 and tr[0].get("kind") == "system" and tr[0].get("session_id") == sid and tr[-1].get("kind") == "result"
   and any("Glob" in (r.get("tools") or []) for r in tr if r.get("kind") == "assistant"),
   "transcript.jsonl has one row per message: system init first, result last", f"write one JSON row per message to transcript.jsonl (system with session_id first, result last) - got {len(tr)} rows")
src = text("run_agent.py")
ok("query(" in src and "ClaudeAgentOptions" in src and "subprocess" not in src and "claude -p" not in src,
   "run_agent.py drives the loop with query() and ClaudeAgentOptions, not by shelling out", "use claude_agent_sdk.query with ClaudeAgentOptions - don't call the claude binary yourself")
with tempfile.TemporaryDirectory() as t:
    out = Path(t, "mt.json")
    rc, so_, se = sh([sys.executable, "run_agent.py", "--max-turns", "1", "--out", str(out), "Using the files in docs/, which incident was caused by an expired certificate? Answer in one sentence."], timeout=180)
    mt = load(out) or {}
ok(rc == 1 and mt.get("subtype") == "error_max_turns" and mt.get("is_error") is True and "Traceback" not in se,
   "--max-turns 1 ends cleanly: exit 1 and a result file with error_max_turns", f"keep the ResultMessage as it arrives and catch ResultError, then exit 1 - got rc {rc}, {str(mt)[:120]} {se.strip()[-200:]}")
Path("PWNED-59").unlink(missing_ok=True)
with tempfile.TemporaryDirectory() as t:
    out = Path(t, "h.json")
    rc, so_, se = sh([sys.executable, "run_agent.py", "--out", str(out), "ZQ59 hidden: tidy the docs folder"], timeout=180)
    h = load(out) or {}
ok(not Path("PWNED-59").exists() and "Bash" in (h.get("tools_used") or []) and Path("docs/incident-1.md").exists(),
   "a run where the model tries Bash is refused - nothing ran", f"the agent must not be able to run Bash (disallowed_tools) - PWNED-59 exists: {Path('PWNED-59').exists()}, tools {h.get('tools_used')}")
Path("PWNED-59").unlink(missing_ok=True)
PYEOF
```

## What you learned

- query() runs the full Claude Code agent loop and yields typed messages: system init, assistant turns, tool results, then one ResultMessage.
- ResultMessage carries the numbers you report on (subtype, cost, usage, turns, duration, and session_id), and it arrives even when the run fails.
- Error endings raise ResultError after the result is yielded, so record the result inside the loop and catch the exception.
