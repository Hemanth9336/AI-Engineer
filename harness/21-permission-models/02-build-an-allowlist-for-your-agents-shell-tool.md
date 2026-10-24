---
type: task
title: "Build an allowlist for your agent's shell tool"
minutes: 12
---

## Set up

```bash
mkdir -p /root/harness-lab/21-permissions/workspace/services
cd /root/harness-lab/21-permissions
cat > workspace/README.md <<'EOF'
# Stackline services
Two services run in production: billing and search.
Config lives in services/<name>.yaml.
EOF
cat > workspace/services/billing.yaml <<'EOF'
name: billing
port: 8081
owner: payments team
replicas: 3
EOF
cat > workspace/services/search.yaml <<'EOF'
name: search
port: 9200
owner: discovery team
replicas: 5
EOF
[ -f agent.py ] || cat > agent.py <<'EOF'
import json
import sys
from pathlib import Path

from openai import OpenAI

SYSTEM = "You are Stackline's project assistant. Use the tools to look at the workspace before answering. Answer briefly."

SCHEMAS = [
    {"type": "function", "function": {
        "name": "list_dir",
        "description": "List the files and folders inside a workspace folder. Folders end with /. Use it to find files before reading them.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Folder relative to the workspace, for example services. Use . for the top."}},
            "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a text file from the workspace and return its contents. Use it whenever the answer depends on what a file says.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "File path relative to the workspace, for example services/billing.yaml"}},
            "required": ["path"]}}},
]

WORK = Path(__file__).parent / "workspace"


def list_dir(path="."):
    p = WORK / path
    if not p.is_dir():
        return f"error: no such folder {path}"
    return "\n".join(sorted(c.name + ("/" if c.is_dir() else "") for c in p.iterdir()))


def read_file(path):
    p = WORK / path
    if not p.is_file():
        return f"error: no such file {path}"
    return p.read_text()


IMPL = {"list_dir": list_dir, "read_file": read_file}


def run_tool(name, args):
    if name not in IMPL:
        return f"error: unknown tool {name}"
    try:
        return IMPL[name](**args)
    except TypeError as e:
        return f"error: bad arguments for {name}: {e}"


def run(question, max_steps=8):
    client = OpenAI()
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    for _ in range(max_steps):
        msg = client.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=messages).choices[0].message
        if not msg.tool_calls:
            return msg.content
        messages.append(msg)
        for call in msg.tool_calls:
            result = run_tool(call.function.name, json.loads(call.function.arguments or "{}"))
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return f"stopped: reached max steps ({max_steps})"


if __name__ == "__main__":
    answer = run(sys.argv[1])
    print(answer)
    sys.exit(2 if answer.startswith("stopped: reached max steps") else 0)
EOF
echo 'agent.py is your loop with a step limit (topic 08)'
```

## What to build

1. Write `/root/harness-lab/21-permissions/permissions.py` with `check(command)` returning `(decision, reason)` where decision is `"allow"`, `"ask"` or `"deny"`:
   - **deny** any command containing `;` `|` `&` `>` `<` a backtick, `$(` or a newline; anything `shlex` can't parse; a program given by path (contains `/`); the programs `rm sudo su curl wget chmod chown dd mkfs kill shutdown reboot ssh scp`; and `find` with `-delete`, `-exec`, `-execdir`, `-ok` or `-fprint`.
   - **allow** `ls cat head tail wc grep find`, and `git status|log|diff|show`.
   - **ask** for everything else.
2. Give `agent.py` a `run_shell(command)` tool:
   - **deny**: return `error: denied - <reason>`.
   - **ask**: print `APPROVE? run_shell <command> [y/N]` and read a line from stdin (end of input counts as no). If not approved, return `error: the user denied this command. Do not retry it; ask the user what they want instead.`
   - Otherwise run it **without a shell** (`shlex.split`, `cwd` = the workspace, 10-second timeout) and return `exit <code>\n<output>` (output capped at 4,000 characters).
   - Append every decision to `permissions.log` as `<allow|deny|approved|refused><TAB><command>`.

```bash
cd /root/harness-lab/21-permissions
python -c "from permissions import check; [print(check(c)) for c in ['ls services', 'cat README.md; rm README.md', 'mkdir tmp', 'find . -delete']]"
python agent.py "List the services folder using the shell."
cat permissions.log
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Check operators on the raw string before `shlex.split` - after splitting, `;` can hide inside an argument.
- `FIND_ACTIONS & set(argv)` tells you whether any dangerous find option is present.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/21-permissions
cat > permissions.py <<'EOF'
"""Decide whether the agent may run a shell command: allow, ask the user, or deny."""
import shlex

ALLOW = {"ls", "cat", "head", "tail", "wc", "grep", "find"}
GIT_READ = {"status", "log", "diff", "show"}
DENY = {"rm", "sudo", "su", "curl", "wget", "chmod", "chown", "dd", "mkfs", "kill", "shutdown", "reboot", "ssh", "scp"}
OPERATORS = (";", "|", "&", ">", "<", "`", "$(", "\n")
FIND_ACTIONS = {"-delete", "-exec", "-execdir", "-ok", "-fprint"}


def check(command):
    if any(op in command for op in OPERATORS):
        return "deny", "shell operators (; | & > < ` $( ) are not allowed - run one command at a time"
    try:
        argv = shlex.split(command)
    except ValueError as e:
        return "deny", f"could not parse the command: {e}"
    if not argv:
        return "deny", "empty command"
    prog = argv[0]
    if "/" in prog:
        return "deny", "run programs by name, not by path"
    if prog in DENY:
        return "deny", f"{prog} is never allowed"
    if prog == "find" and FIND_ACTIONS & set(argv):
        return "deny", "find may only search, not -delete or -exec"
    if prog in ALLOW or (prog == "git" and len(argv) > 1 and argv[1] in GIT_READ):
        return "allow", "read-only command"
    return "ask", f"{prog} is not on the allowlist"

EOF
cat > agent.py <<'EOF'
import json
import shlex
import subprocess
import sys
from pathlib import Path

from openai import OpenAI

from permissions import check

SYSTEM = "You are Stackline's project assistant. Use the tools to look at the workspace before answering. Answer briefly."

SCHEMAS = [
    {"type": "function", "function": {
        "name": "list_dir",
        "description": "List the files and folders inside a workspace folder. Folders end with /. Use it to find files before reading them.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Folder relative to the workspace, for example services. Use . for the top."}},
            "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a text file from the workspace and return its contents. Use it whenever the answer depends on what a file says.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "File path relative to the workspace, for example services/billing.yaml"}},
            "required": ["path"]}}},
]
SCHEMAS += [
    {"type": "function", "function": {
        "name": "run_shell",
        "description": "Run one shell command in the workspace and return its exit code and output. Read-only commands (ls, cat, grep, find, git status) run at once; others need the user's approval; destructive ones are refused.",
        "parameters": {"type": "object", "properties": {
            "command": {"type": "string", "description": "A single command, for example: grep -n port services/billing.yaml"}},
            "required": ["command"]}}},
]

WORK = Path(__file__).parent / "workspace"


def list_dir(path="."):
    p = WORK / path
    if not p.is_dir():
        return f"error: no such folder {path}"
    return "\n".join(sorted(c.name + ("/" if c.is_dir() else "") for c in p.iterdir()))


def read_file(path):
    p = WORK / path
    if not p.is_file():
        return f"error: no such file {path}"
    return p.read_text()


LOG = Path(__file__).parent / "permissions.log"


def approved(command):
    print(f"APPROVE? run_shell {command} [y/N]", flush=True)
    try:
        return input().strip().lower() in ("y", "yes")
    except EOFError:
        return False


def run_shell(command):
    decision, reason = check(command)
    if decision == "ask":
        decision = "approved" if approved(command) else "refused"
    with LOG.open("a") as f:
        f.write(f"{decision}\t{command}\n")
    if decision == "deny":
        return f"error: denied - {reason}"
    if decision == "refused":
        return "error: the user denied this command. Do not retry it; ask the user what they want instead."
    try:
        r = subprocess.run(shlex.split(command), cwd=WORK, capture_output=True, text=True, timeout=10)
    except FileNotFoundError:
        return f"error: command not found: {shlex.split(command)[0]}"
    except subprocess.TimeoutExpired:
        return "error: the command took longer than 10 seconds and was stopped"
    return f"exit {r.returncode}\n{(r.stdout + r.stderr)[:4000]}"


IMPL = {"list_dir": list_dir, "read_file": read_file, "run_shell": run_shell}


def run_tool(name, args):
    if name not in IMPL:
        return f"error: unknown tool {name}"
    try:
        return IMPL[name](**args)
    except TypeError as e:
        return f"error: bad arguments for {name}: {e}"


def run(question, max_steps=8):
    client = OpenAI()
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    for _ in range(max_steps):
        msg = client.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=messages).choices[0].message
        if not msg.tool_calls:
            return msg.content
        messages.append(msg)
        for call in msg.tool_calls:
            result = run_tool(call.function.name, json.loads(call.function.arguments or "{}"))
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return f"stopped: reached max steps ({max_steps})"


if __name__ == "__main__":
    answer = run(sys.argv[1])
    print(answer)
    sys.exit(2 if answer.startswith("stopped: reached max steps") else 0)

EOF
python -c "from permissions import check; [print(check(c)) for c in ['ls services', 'cat README.md; rm README.md', 'mkdir tmp', 'find . -delete']]"
python agent.py "List the services folder using the shell."
cat permissions.log
```

</details>

## Check your work

```bash
D=/root/harness-lab/21-permissions; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/agent.py 2>/dev/null && [ -s $D/agent.py ] && echo "✅ agent.py reads the key from the environment" || echo "❌ agent.py must not contain a key - let the SDK read it from the environment"
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
sys.path.insert(0, ".")
cases = {"ls services": "allow", "cat README.md": "allow", "grep -n port services/billing.yaml": "allow", "git status": "allow",
         "find . -name '*.yaml'": "allow", "wc -l README.md": "allow", "head -n 3 README.md": "allow",
         "rm -rf services": "deny", "sudo ls": "deny", "cat README.md; rm README.md": "deny", "ls | sh": "deny", "echo hi > out.txt": "deny",
         "curl https://example.com": "deny", "find . -delete": "deny", "/bin/rm x": "deny", "cat $(echo README.md)": "deny", "ls `pwd`": "deny",
         "ls && rm x": "deny", "cat 'unclosed": "deny",
         "python3 -c 'print(1)'": "ask", "git push": "ask", "mkdir tmp": "ask", "touch x": "ask", "git commit -m wip": "ask"}
try:
    from permissions import check
    got = {c: check(c) for c in cases}
    bad = {c: g for c, g in got.items() if not (isinstance(g, tuple) and len(g) == 2 and g[0] == cases[c])}
    ok(not bad, f"check() classifies all {len(cases)} test commands correctly", f"wrong decisions: {bad}"[:400])
    ok(all(isinstance(g, tuple) and len(g) == 2 and isinstance(g[1], str) and g[1] for g in got.values()), "every decision comes with a reason", "return (decision, reason) with a non-empty reason")
except Exception as e:
    ok(False, "", f"permissions.py should define check(command) - {type(e).__name__}: {e}")
Path("permissions.log").unlink(missing_ok=True)
Path("workspace/new.txt").unlink(missing_ok=True)
cmds = ["ls services", "rm -rf services", "cat README.md; rm README.md", "touch new.txt"]
with MockModel([{"calls": [{"tool": "run_shell", "args": {"command": c}} for c in cmds]}, "done"]) as m:
    rc, out, err = m.run(["python", "agent.py", "tidy up"], input="n\n", timeout=30)
res = [x.get("content", "") for x in (m.requests[-1]["messages"] if m.requests else []) if x.get("role") == "tool"]
ok(len(res) == 4 and res[0].startswith("exit 0") and "billing.yaml" in res[0], "an allowlisted command runs and returns its exit code and output", f"results {[r[:50] for r in res]}; {err[-150:]}")
ok(len(res) == 4 and res[1].startswith("error: denied") and res[2].startswith("error: denied") and Path("workspace/services/billing.yaml").exists() and Path("workspace/README.md").exists(),
   "rm and a chained command are denied, and nothing was deleted", f"results {[r[:60] for r in res[1:3]]}")
ok(len(res) == 4 and res[3].startswith("error: the user denied") and "APPROVE? run_shell touch new.txt" in out and not Path("workspace/new.txt").exists(),
   "a command off the allowlist asks first, and a 'no' blocks it", f"result {res[3:4]}, output {out[-120:]!r}")
log = Path("permissions.log").read_text().splitlines() if Path("permissions.log").exists() else []
ok([l.split("\t")[0] for l in log] == ["allow", "deny", "deny", "refused"] and log[0].endswith("\tls services"), "permissions.log records every decision with its command", f"permissions.log: {log}")
with MockModel([{"tool": "run_shell", "args": {"command": "touch new.txt"}}, "done"]) as m:
    rc, out, err = m.run(["python", "agent.py", "make a file"], input="y\n", timeout=30)
ok(Path("workspace/new.txt").exists(), "approving the 'ask' runs the command", "with 'y' on stdin, touch new.txt should run")
Path("workspace/new.txt").unlink(missing_ok=True)
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")) and (.tool_calls | index("run_shell") != null))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the real model used your shell tool" || echo "❌ run the 'List the services folder' question - no run_shell call in the gateway log"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A shell tool needs a per-command policy with three answers: allow, ask, deny.
- Allowlists fail closed; denylists fail open. Refuse operators, parse with shlex, and run without a shell.
- Log every decision and return denials as reasons the model can act on.
