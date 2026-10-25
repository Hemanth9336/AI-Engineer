---
type: task
title: "Add a custom tool and a permission gate"
minutes: 17
---

## Set up

Set up creates `/root/mastery/060-jobs` with `jobs.json`: four jobs, one of them (`J-102`) belonging to another customer, `globex`.

```bash
rm -rf /root/mastery/060-jobs && mkdir -p /root/mastery/060-jobs && cd /root/mastery/060-jobs
cat > jobs.json <<'EOF'
[
  {
    "id": "J-101",
    "customer": "acme",
    "status": "running"
  },
  {
    "id": "J-102",
    "customer": "globex",
    "status": "running"
  },
  {
    "id": "J-103",
    "customer": "acme",
    "status": "queued"
  },
  {
    "id": "J-104",
    "customer": "acme",
    "status": "running"
  }
]
EOF
python3 -c "import claude_agent_sdk"
```

## What to build

1. Write `jobs_agent.py --customer NAME [--resume SESSION] PROMPT`.
   - **Tools.** Use an in-process MCP server named `jobs` with two `@tool`s:
     - `list_jobs` returns only that customer's jobs.
     - `cancel_job(job_id)` sets `status` to `cancelled` in `jobs.json`, and returns `is_error` for a job that isn't theirs.
   - **Gate.** Write `make_gate(customer)`, returning an async `can_use_tool` callback:
     - Allow `list_jobs`.
     - Allow `cancel_job` only for an existing job owned by `customer`.
     - Deny everything else, Bash and Read included, with a message saying what *is* allowed.
     - Append every decision to `decisions.jsonl` (`tool`, `input`, `decision`, `reason`).
     - Keep every tool out of `allowed_tools`, or the callback is skipped.
   - **Audit hook.** Add a PreToolUse hook (`matcher=None`) that appends `tool` and `session_id` to `audit.jsonl` for every call.
   - **Session.** Pass `--resume` through as `resume=`. Write `session.txt` (the session id) and `last_result.json` (`session_id`, `subtype`, `result`).
2. Run as `acme`:
   > Cancel jobs J-102 and J-103 for me, then show me what is left.
3. Resume that session and ask:
   > Which of my jobs are still running?

The checker calls your `make_gate` directly with calls you never saw, and re-runs the agent as `--customer globex` in a fresh copy.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `can_use_tool` needs streaming input: pass `prompt` as an async generator that yields one `{"type": "user", "message": {...}}` dict.
- A tool name in `allowed_tools` is approved before your callback runs, and the SDK warns with CanUseToolShadowedWarning.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/060-jobs
cat > jobs_agent.py <<'EOF'
#!/usr/bin/env python3
"""jobs_agent.py --customer NAME [--resume SESSION] PROMPT - an agent that manages one customer's jobs and nothing else."""
import argparse
import asyncio
import json
import sys
from pathlib import Path

from claude_agent_sdk import (ClaudeAgentOptions, HookMatcher, PermissionResultAllow, PermissionResultDeny, ResultMessage,
                              create_sdk_mcp_server, query, tool)

HERE = Path(__file__).resolve().parent
JOBS = HERE / "jobs.json"


def jobs():
    return json.loads(JOBS.read_text())


def log(name, row):
    with open(HERE / name, "a") as f:
        f.write(json.dumps(row) + "\n")


def make_tools(customer):
    @tool("list_jobs", "List this customer's jobs with their id and status.", {})
    async def list_jobs(args):
        mine = [j for j in jobs() if j["customer"] == customer]
        return {"content": [{"type": "text", "text": json.dumps(mine)}]}

    @tool("cancel_job", "Cancel one of this customer's jobs by id (for example J-101).", {"job_id": str})
    async def cancel_job(args):
        data = jobs()
        job = next((j for j in data if j["id"] == args.get("job_id") and j["customer"] == customer), None)
        if job is None:
            return {"content": [{"type": "text", "text": f"No job {args.get('job_id')} for {customer}"}], "is_error": True}
        job["status"] = "cancelled"
        JOBS.write_text(json.dumps(data, indent=2) + "\n")
        return {"content": [{"type": "text", "text": f"{job['id']} cancelled"}]}

    return [list_jobs, cancel_job]


def make_gate(customer):
    async def gate(tool_name, tool_input, context):
        if tool_name == "mcp__jobs__list_jobs":
            decision, reason = "allow", "read-only"
        elif tool_name == "mcp__jobs__cancel_job":
            job = next((j for j in jobs() if j["id"] == tool_input.get("job_id")), None)
            if job is None:
                decision, reason = "deny", f"there is no job {tool_input.get('job_id')}"
            elif job["customer"] != customer:
                decision, reason = "deny", f"{job['id']} belongs to another customer; you can only cancel {customer}'s jobs"
            else:
                decision, reason = "allow", f"{job['id']} belongs to {customer}"
        else:
            decision, reason = "deny", f"{tool_name} is not available; use list_jobs and cancel_job"
        log("decisions.jsonl", {"tool": tool_name, "input": tool_input, "decision": decision, "reason": reason})
        if decision == "allow":
            return PermissionResultAllow(updated_input=tool_input)
        return PermissionResultDeny(message=reason)
    return gate


async def audit(input_data, tool_use_id, context):
    log("audit.jsonl", {"tool": input_data.get("tool_name"), "session_id": input_data.get("session_id")})
    return {}


async def run(customer, prompt, resume):
    server = create_sdk_mcp_server(name="jobs", version="1.0.0", tools=make_tools(customer))
    opts = ClaudeAgentOptions(cwd=str(HERE), mcp_servers={"jobs": server}, can_use_tool=make_gate(customer),
                              hooks={"PreToolUse": [HookMatcher(matcher=None, hooks=[audit])]},
                              max_turns=10, max_budget_usd=0.50, resume=resume)

    async def messages():
        yield {"type": "user", "message": {"role": "user", "content": prompt}}

    final = None
    async for m in query(prompt=messages(), options=opts):
        if isinstance(m, ResultMessage):
            final = m
    return final


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--customer", required=True)
    ap.add_argument("--resume")
    ap.add_argument("prompt")
    a = ap.parse_args()
    final = asyncio.run(run(a.customer, a.prompt, a.resume))
    (HERE / "session.txt").write_text(final.session_id + "\n")
    (HERE / "last_result.json").write_text(json.dumps(
        {"session_id": final.session_id, "subtype": final.subtype, "result": final.result}, indent=2) + "\n")
    print(final.result)
    return 1 if final.is_error else 0


if __name__ == "__main__":
    sys.exit(main())
EOF
chmod +x jobs_agent.py
python3 jobs_agent.py --customer acme 'Cancel jobs J-102 and J-103 for me, then show me what is left.'
python3 jobs_agent.py --customer acme --resume "$(cat session.txt)" 'Which of my jobs are still running?'
cat decisions.jsonl
```

</details>

## Check your work

```bash
D=/root/mastery/060-jobs; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
ORIG = '[{"id": "J-101", "customer": "acme", "status": "running"}, {"id": "J-102", "customer": "globex", "status": "running"}, {"id": "J-103", "customer": "acme", "status": "queued"}, {"id": "J-104", "customer": "acme", "status": "running"}]'

import asyncio, importlib.util, shutil
st = {j["id"]: j["status"] for j in (load("jobs.json") or [])}
ok(st.get("J-103") == "cancelled" and st.get("J-102") == "running" and st.get("J-101") == "running",
   "acme's J-103 is cancelled; globex's J-102 is untouched", f"the run as --customer acme should cancel J-103 only - jobs.json statuses {st}")
dec = events("decisions.jsonl")
def find(tool, job=None):
    return [d for d in dec if d.get("tool") == tool and (job is None or (d.get("input") or {}).get("job_id") == job)]
ok(find("mcp__jobs__cancel_job", "J-102") and all(d.get("decision") == "deny" for d in find("mcp__jobs__cancel_job", "J-102"))
   and any(d.get("decision") == "allow" for d in find("mcp__jobs__cancel_job", "J-103")),
   "decisions.jsonl: the gate denied J-102 (another customer) and allowed J-103", f"log every can_use_tool decision to decisions.jsonl - cancel decisions {find('mcp__jobs__cancel_job')}")
ok(find("mcp__jobs__list_jobs") and find("Bash") and all(d.get("decision") == "deny" for d in find("Bash")) and not Path("PWNED-60").exists(),
   "every call went through the gate: list_jobs logged, Bash denied and never ran", "keep every tool out of allowed_tools so can_use_tool sees list_jobs too, and deny anything that isn't a jobs tool")
aud = events("audit.jsonl")
ok(len(aud) >= 5 and {"mcp__jobs__list_jobs", "mcp__jobs__cancel_job", "Bash"} <= {a.get("tool") for a in aud} and all(a.get("session_id") for a in aud),
   "audit.jsonl: the PreToolUse hook logged every call, denied ones included, with its session id", f"add a PreToolUse hook (matcher None) that appends tool and session_id to audit.jsonl - {len(aud)} rows")
sid = text("session.txt").strip()
lr = load("last_result.json") or {}
mine = [rows for rows in sessions(".") if any(r.get("sessionId") == sid for r in rows)]
ps = " ".join(p for rows in mine for p in prompts(rows))
ok(sid and lr.get("session_id") == sid and "J-102 and J-103" in ps and "still running" in ps,
   "the second run resumed the same session: one id, both prompts in its transcript", f"pass --resume $(cat session.txt) as ClaudeAgentOptions(resume=...) - last_result {lr.get('session_id')} vs session.txt {sid}")
ok("J-101" in str(lr.get("result")) and "J-104" in str(lr.get("result")), "the resumed run answered with acme's running jobs", f"last_result.json should hold the second answer - got {str(lr.get('result'))[:150]}")
with tempfile.TemporaryDirectory() as t:
    shutil.copy("jobs_agent.py", t)
    Path(t, "jobs.json").write_text(ORIG)
    spec = importlib.util.spec_from_file_location("jobs_agent_chk", Path(t, "jobs_agent.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    g = m.make_gate("acme")
    def decide(name, inp):
        return type(asyncio.run(g(name, inp, None))).__name__
    got = {"J-104": decide("mcp__jobs__cancel_job", {"job_id": "J-104"}), "J-102": decide("mcp__jobs__cancel_job", {"job_id": "J-102"}),
           "J-999": decide("mcp__jobs__cancel_job", {"job_id": "J-999"}), "Read": decide("Read", {"file_path": "/etc/passwd"}),
           "Write": decide("Write", {"file_path": "jobs.json", "content": "[]"})}
    ok(got == {"J-104": "PermissionResultAllow", "J-102": "PermissionResultDeny", "J-999": "PermissionResultDeny", "Read": "PermissionResultDeny", "Write": "PermissionResultDeny"},
       "make_gate('acme') decides hidden calls correctly: J-104 yes; J-102, J-999, Read, and Write no", f"make_gate(customer) should return an async gate - got {got}")
    rc, so_, se = sh([sys.executable, "jobs_agent.py", "--customer", "globex", "Cancel jobs J-102 and J-103 for me, then show me what is left."], cwd=t, timeout=180)
    st2 = {j["id"]: j["status"] for j in json.loads(Path(t, "jobs.json").read_text())}
    ok(st2.get("J-102") == "cancelled" and st2.get("J-103") == "queued" and not Path(t, "PWNED-60").exists(),
       "run as --customer globex, the same prompt cancels J-102 and leaves acme's J-103 alone", f"the customer must come from --customer, not be hard-coded - statuses {st2}, rc {rc} {se.strip()[-200:]}")
Path("PWNED-60").unlink(missing_ok=True)
PYEOF
```

## What you learned

- @tool plus create_sdk_mcp_server gives the agent narrow, typed capabilities that run in your process, named mcp__<server>__<tool>.
- can_use_tool decides each call that needs approval, but only calls that allow rules haven't already approved; PreToolUse hooks see every call.
- resume keeps one session id across processes, and fork_session branches into a new one.
