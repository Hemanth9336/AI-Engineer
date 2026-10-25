---
type: task
title: "Add a hook that blocks a command pattern"
minutes: 9
---

## Set up

`/root/harness-lab/36-hooks` has `deploy.sh` (records each deploy in `deploy.log`) and `run-tests.sh`. Claude Code may run `./deploy.sh` - but production deploys must go through the release pipeline.

```bash
mkdir -p /root/harness-lab/36-hooks/.claude/hooks
cd /root/harness-lab/36-hooks
cat > deploy.sh <<'EOF'
#!/usr/bin/env bash
env=""
while [ $# -gt 0 ]; do
  case "$1" in
    --env) env="$2"; shift 2 ;;
    --env=*) env="${1#--env=}"; shift ;;
    *) shift ;;
  esac
done
echo "deploy $env" >> "$(dirname "$0")/deploy.log"
echo "deployed ledger-api to $env"
EOF
cat > run-tests.sh <<'EOF'
#!/usr/bin/env bash
echo "run-tests $*" >> "$(dirname "$0")/tests.log"
echo "14 passed, 0 failed"
EOF
chmod +x deploy.sh run-tests.sh
touch deploy.log tests.log
claude --version
```

## What to build

1. Write `/root/harness-lab/36-hooks/.claude/hooks/block_prod.py`, a `PreToolUse` hook:
   - Read the event JSON from stdin. Only `Bash` calls are checked.
   - Block any command that runs `deploy.sh` with `--env prod` or `--env production`, written with a space or `=`, anywhere in the command.
   - On a block: append `blocked<TAB><command>` to `$CLAUDE_PROJECT_DIR/.claude/hooks.log`, print a reason starting with `Blocked by project policy` to **stderr**, and exit **2**.
   - Otherwise exit 0.
2. Register it in `/root/harness-lab/36-hooks/.claude/settings.json` for the `Bash` matcher, using `$CLAUDE_PROJECT_DIR` in the command.
3. Test the hook by hand, then through Claude Code:

```bash
cd /root/harness-lab/36-hooks
echo '{"tool_name": "Bash", "tool_input": {"command": "./deploy.sh --env=prod"}}' | CLAUDE_PROJECT_DIR=$PWD python .claude/hooks/block_prod.py; echo "exit $?"
cd /root/harness-lab/36-hooks
claude -p "Ship ledger-api to production with deploy.sh" --allowedTools "Bash(./deploy.sh:*)" --max-turns 4
claude -p "Ship ledger-api to staging with deploy.sh" --allowedTools "Bash(./deploy.sh:*)" --max-turns 4
cat deploy.log .claude/hooks.log
```

The production run should end with the model explaining it was blocked, and `deploy.log` should only show staging.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `re.compile(r'\bdeploy\.sh\b.*--env(=|\s+)(prod|production)\b')` covers the variants.
- `sys.exit(2)` after printing the reason to `sys.stderr`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/36-hooks
cat > .claude/hooks/block_prod.py <<'EOF'
"""PreToolUse hook: block Bash commands that deploy to production. Exit code 2 blocks the call; stderr goes to the model."""
import json
import os
import re
import sys
from pathlib import Path

PROD = re.compile(r"\bdeploy\.sh\b.*--env(=|\s+)(prod|production)\b")

event = json.load(sys.stdin)
command = (event.get("tool_input") or {}).get("command", "") if event.get("tool_name") == "Bash" else ""
if PROD.search(command):
    log = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")) / ".claude" / "hooks.log"
    with open(log, "a") as f:
        f.write(f"blocked\t{command}\n")
    print("Blocked by project policy: production deploys go through the release pipeline, not the agent. "
          "Deploy to staging instead.", file=sys.stderr)
    sys.exit(2)
sys.exit(0)

EOF
cat > .claude/settings.json <<'EOF'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/block_prod.py\""
          }
        ]
      }
    ]
  }
}
EOF
echo '{"tool_name": "Bash", "tool_input": {"command": "./deploy.sh --env=prod"}}' | CLAUDE_PROJECT_DIR=$PWD python .claude/hooks/block_prod.py || echo "exit $?"
cd /root/harness-lab/36-hooks
claude -p "Ship ledger-api to production with deploy.sh" --allowedTools "Bash(./deploy.sh:*)" --max-turns 4
claude -p "Ship ledger-api to staging with deploy.sh" --allowedTools "Bash(./deploy.sh:*)" --max-turns 4
cat deploy.log .claude/hooks.log
```

</details>

## Check your work

```bash
D=/root/harness-lab/36-hooks; cd $D 2>/dev/null || echo "❌ create $D"
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

hook = Path(".claude/hooks/block_prod.py")
def call(tool, inp):
    d = tempfile.mkdtemp()
    Path(d, ".claude").mkdir()
    r = subprocess.run([sys.executable, str(hook)], input=json.dumps({"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": inp}), capture_output=True, text=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=d), timeout=20)
    log = Path(d, ".claude/hooks.log")
    return r.returncode, r.stderr, log.read_text() if log.exists() else ""
if not hook.exists():
    print("❌ write .claude/hooks/block_prod.py")
else:
    blocked = ["./deploy.sh --env prod", "./deploy.sh --env=prod", "bash deploy.sh   --env   production", "cd /x && ./deploy.sh --verbose --env prod"]
    allowed = ["./deploy.sh --env staging", "echo prod", "./deploy.sh --env prodlike-sandbox", "./run-tests.sh --fast"]
    res = {c: call("Bash", {"command": c}) for c in blocked + allowed}
    bad = [c for c in blocked if res[c][0] != 2] + [c for c in allowed if res[c][0] != 0]
    ok(not bad, "the hook exits 2 for every prod/production deploy variant and 0 for everything else", f"wrong exit code for: {bad}")
    ok(all(res[c][1].strip().startswith("Blocked by project policy") for c in blocked), "blocked calls explain why on stderr", f"stderr should start with 'Blocked by project policy' - got {res[blocked[0]][1][:120]!r}")
    ok(all(res[c][2] == f"blocked\t{c}\n" for c in blocked) and not any(res[c][2] for c in allowed), "each block is logged to $CLAUDE_PROJECT_DIR/.claude/hooks.log", f"hooks.log for {blocked[1]!r}: {res[blocked[1]][2]!r}")
    w = call("Write", {"file_path": "notes.md", "content": "./deploy.sh --env prod"})
    ok(w[0] == 0, "non-Bash tools pass through", f"a Write call returned exit {w[0]}")
hooks = ((load(".claude/settings.json") or {}).get("hooks") or {}).get("PreToolUse") or []
ok(any("Bash" in (h.get("matcher") or "") and any("block_prod.py" in x.get("command", "") and "CLAUDE_PROJECT_DIR" in x.get("command", "") for x in h.get("hooks", [])) for h in hooks), ".claude/settings.json registers block_prod.py as a PreToolUse hook for Bash", f"PreToolUse hooks in .claude/settings.json: {hooks}")
deploys = lambda: Path("deploy.log").read_text().splitlines() if Path("deploy.log").exists() else []
ok(deploys() and "deploy prod" not in deploys() and "deploy staging" in deploys(), "deploy.log shows the staging deploy and no prod deploy", f"deploy.log: {deploys()}")
n_prod, n_stage = deploys().count("deploy prod"), deploys().count("deploy staging")
rc, ev, err = claude("Ship ledger-api to production with deploy.sh", "--allowedTools", "Bash(./deploy.sh:*)")
tr = [b.get("content") for e in ev if e.get("type") == "user" for b in blocks(e) if b.get("type") == "tool_result"]
ok(deploys().count("deploy prod") == n_prod and any("Blocked by project policy" in str(t) for t in tr), "a fresh claude -p prod deploy is blocked by your hook, and the model sees the reason", f"prod deploys {n_prod}->{deploys().count('deploy prod')}; tool results {[str(t)[:120] for t in tr]}")
rc, ev, err = claude("Ship ledger-api to staging with deploy.sh", "--allowedTools", "Bash(./deploy.sh:*)")
ok(deploys().count("deploy staging") == n_stage + 1, "a staging deploy through claude -p still runs", f"staging deploys {n_stage}->{deploys().count('deploy staging')} {err[-200:]}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- PreToolUse hooks get the tool call as JSON on stdin; exit 2 blocks it and stderr tells the model why.
- Hooks enforce; instructions request. Anything that must never happen belongs in a hook or a deny rule.
- Test pattern variants directly, without the model - spaces, `=`, synonyms, chained commands.
