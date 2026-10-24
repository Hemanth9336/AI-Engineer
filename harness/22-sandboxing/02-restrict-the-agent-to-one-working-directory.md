---
type: task
title: "Restrict the agent to one working directory"
minutes: 11
---

## Set up

`agent.py` and `permissions.py` are the topic 21 shell agent. Next to them is `secret.txt`, which the agent must never read. Someone also committed a symlink, `workspace/etc-link`, that points to `/etc`.

```bash
mkdir -p /root/harness-lab/22-sandbox/workspace/services
cd /root/harness-lab/22-sandbox
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
echo 'TOP SECRET: production database password is hunter2-stackline' > secret.txt
ln -sfn /etc workspace/etc-link
[ -f agent.py ] || cat > agent.py <<'EOF'
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
echo 'agent.py is your loop with a step limit (topic 08)'
```

## What to build

1. Try the escape first: with the current agent, `read_file("../secret.txt")` and `run_shell("cat ../secret.txt")` both work.
2. Write `/root/harness-lab/22-sandbox/sandbox.py`:
   - `WORK` = the resolved `workspace/` folder next to sandbox.py, and an `Escape` exception.
   - `inside(path)` returns the resolved path, or raises `Escape` if it's outside `WORK` - including through `..`, absolute paths and symlinks.
   - `run(command)` raises `Escape` if any argument starts with `/` or `~` or contains a `..` part; otherwise runs it **without a shell** in `WORK`, with only `PATH`, `HOME` (= `WORK`) and `LANG` in the environment, a 10-second timeout, and returns `(exit_code, output)` with output capped at 4,000 characters.
3. Change `agent.py` so `list_dir` and `read_file` use `inside()`, `run_shell` uses `sandbox.run()` after the permission check, and an `Escape` becomes the tool result `error: denied - <reason>`.

```bash
cd /root/harness-lab/22-sandbox
python -c "from sandbox import inside; print(inside('services/billing.yaml')); inside('../secret.txt')" || true
python agent.py "Show me the file ../secret.txt"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `WORK not in p.parents` is the containment test; compare resolved paths only.
- Pass `env=` explicitly - without it, the child process inherits OPENAI_API_KEY.
- Catch `Escape` in `run_tool` so every tool gets the same denial format.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/22-sandbox
cat > sandbox.py <<'EOF'
"""Keep every file path and shell command inside the workspace."""
import shlex
import subprocess
from pathlib import Path

WORK = (Path(__file__).parent / "workspace").resolve()
SAFE_ENV = {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(WORK), "LANG": "C.UTF-8"}
TIMEOUT = 10
MAX_OUTPUT = 4000


class Escape(Exception):
    pass


def inside(path):
    p = (WORK / path).resolve()
    if p != WORK and WORK not in p.parents:
        raise Escape(f"{path} is outside the workspace")
    return p


def run(command):
    argv = shlex.split(command)
    for a in argv[1:]:
        if a.startswith(("/", "~")) or ".." in Path(a).parts:
            raise Escape(f"{a} points outside the workspace")
    r = subprocess.run(argv, cwd=WORK, env=SAFE_ENV, capture_output=True, text=True, timeout=TIMEOUT)
    return r.returncode, (r.stdout + r.stderr)[:MAX_OUTPUT]

EOF
cat > agent.py <<'EOF'
import json
import shlex
import subprocess
import sys
from pathlib import Path

from openai import OpenAI

from permissions import check
from sandbox import Escape, inside
from sandbox import run as sandboxed

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
    p = inside(path)
    if not p.is_dir():
        return f"error: no such folder {path}"
    return "\n".join(sorted(c.name + ("/" if c.is_dir() else "") for c in p.iterdir()))


def read_file(path):
    p = inside(path)
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
        code, out = sandboxed(command)
    except Escape as e:
        return f"error: denied - {e}"
    except FileNotFoundError:
        return f"error: command not found: {shlex.split(command)[0]}"
    except subprocess.TimeoutExpired:
        return "error: the command took longer than 10 seconds and was stopped"
    return f"exit {code}\n{out}"


IMPL = {"list_dir": list_dir, "read_file": read_file, "run_shell": run_shell}


def run_tool(name, args):
    if name not in IMPL:
        return f"error: unknown tool {name}"
    try:
        return IMPL[name](**args)
    except Escape as e:
        return f"error: denied - {e}"
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
python -c "from sandbox import inside; print(inside('services/billing.yaml')); inside('../secret.txt')" || true
python agent.py "Show me the file ../secret.txt"
```

</details>

## Check your work

```bash
D=/root/harness-lab/22-sandbox; cd $D 2>/dev/null || echo "❌ create $D"
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
import time
try:
    import sandbox as SB
    work = Path("workspace").resolve()
    ok(SB.WORK == work and SB.inside("services/billing.yaml") == work / "services/billing.yaml" and SB.inside("services/../README.md") == work / "README.md",
       "inside() accepts paths in the workspace, even with a harmless ..", f"WORK is {SB.WORK}")
    esc = []
    for bad in ["../secret.txt", "/etc/passwd", "etc-link/hosts", "services/../../secret.txt", ".."]:
        try:
            SB.inside(bad)
            esc.append(bad)
        except SB.Escape:
            pass
    ok(not esc, "inside() raises Escape for .., absolute paths and the /etc symlink", f"these got through: {esc}")
    code, out = SB.run("pwd")
    ok(code == 0 and out.strip() == str(work), "commands run in the workspace", f"pwd printed {out.strip()!r}")
    code, out = SB.run("printenv")
    ok("OPENAI" not in out and "LAB_AI" not in out and f"HOME={work}" in out, "commands get a clean environment - no API key, HOME is the workspace", f"printenv showed: {out[:200]!r}")
    esc = []
    for bad in ["cat ../secret.txt", "cat /etc/hosts", "ls ~"]:
        try:
            SB.run(bad)
            esc.append(bad)
        except SB.Escape:
            pass
    ok(not esc, "run() refuses arguments that point outside", f"these ran: {esc}")
    t = time.time()
    try:
        SB.run("sleep 30")
    except Exception:
        pass
    ok(time.time() - t < 15, "a command that hangs is stopped by the timeout", f"sleep 30 ran for {time.time() - t:.0f}s")
except Exception as e:
    ok(False, "", f"sandbox.py should define WORK, Escape, inside() and run() - {type(e).__name__}: {e}")
calls = [("read_file", {"path": "../secret.txt"}), ("read_file", {"path": "etc-link/hosts"}), ("list_dir", {"path": ".."}),
         ("run_shell", {"command": "cat ../secret.txt"}), ("run_shell", {"command": "printenv"}), ("read_file", {"path": "services/billing.yaml"})]
with MockModel([{"calls": [{"tool": n, "args": a} for n, a in calls]}, "done"]) as m:
    rc, out, err = m.run(["python", "agent.py", "look around"], input="y\n", timeout=40)
res = [x.get("content", "") for x in (m.requests[-1]["messages"] if m.requests else []) if x.get("role") == "tool"]
ok(len(res) == 6 and all(r.startswith("error: denied") for r in res[:4]) and not any("TOP SECRET" in r for r in res), "the agent's tools refuse every escape with 'error: denied'", f"results {[r[:50] for r in res]}; {err[-150:]}")
ok(len(res) == 6 and res[4].startswith("exit 0") and "mock-key" not in res[4] and "OPENAI" not in res[4] and "port: 8081" in res[5], "allowed work still works, and the shell can't see the API key", f"printenv result {res[4:5]}, billing {res[5:6]}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")) and (.tool_calls | index("read_file") != null))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the real model tried to read ../secret.txt through your sandbox" || echo "❌ run the 'Show me the file ../secret.txt' question - no read_file call in the gateway log"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Resolve every path, then check it's inside the workspace - this catches .., absolute paths and symlinks.
- Run commands in the workspace with a clean environment, a timeout and an output cap.
- Argument checks are a rough filter; the operating system has to enforce the real boundary.
