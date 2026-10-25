---
type: task
title: "Run your first agent task"
minutes: 23
---

## Task: run your first agent task

Prove the whole stack works by leaving three artifacts in a new folder.

## Files to create

- `/root/first-contact/hello.py` - a small Python script you write yourself, containing at least one print statement.
- `/root/first-contact/version.txt` - the output of the command that prints the installed Claude Code version.
- `/root/first-contact/report.txt` - the agent's reply to a headless prompt. Ask Claude to read `hello.py` and report what it does, and tell it to begin the reply with the exact line `REPO REPORT`. Redirect the reply into the file.

Any model works for the report. If it feels slow, ask for the fast one with `--model` and the alias `haiku`.

When all three files exist, press **Submit**.

<details><summary>Solution</summary>

```bash
mkdir -p /root/first-contact && cd /root/first-contact
cat > hello.py <<'EOF'
def greet(name):
    return f"Hello, {name}!"


print(greet("agent"))
EOF
claude --version > version.txt
claude -p "Read hello.py and report what it does. Begin the reply with the exact line REPO REPORT." --model haiku > report.txt
cat report.txt
```

</details>

## Check your work

```bash
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
D = "/root/first-contact"
os.chdir(D) if os.path.isdir(D) else None
src = text(D + "/hello.py")
ok("print(" in src and sh("python3 hello.py", cwd=D)[0] == 0 if src else False,
   "hello.py exists, has a print statement, and runs", f"write {D}/hello.py with at least one print statement (python3 hello.py must run)")
rc, ver, _ = sh("claude --version")
got = text(D + "/version.txt").strip()
ok(bool(got) and got == ver.strip(), f"version.txt holds the installed version ({ver.strip()})", "save the output of claude --version to version.txt")
rep = text(D + "/report.txt")
first = rep.strip().splitlines()[0].strip() if rep.strip() else ""
ok(first == "REPO REPORT" and len(rep.strip().splitlines()) > 1, "report.txt begins with the line REPO REPORT and says more",
   "report.txt must start with the exact line REPO REPORT, followed by the agent's description")
hits = []
for rows in sessions(D):
    if not any("hello.py" in p for p in prompts(rows)):
        continue
    read = any((u.get("name") == "Read" and str(u["input"].get("file_path", "")).endswith("hello.py")) or
               (u.get("name") == "Bash" and "hello.py" in u["input"].get("command", "")) for u in uses(rows))
    last = [b.get("text", "") for r in rows if r.get("type") == "assistant" for b in content(r) if b.get("type") == "text"]
    hits.append(read and bool(last) and last[-1].strip() == rep.strip())
ok(any(hits), "report.txt is the reply of a run in this folder that read hello.py",
   "run claude -p from inside the folder, ask it to read hello.py, and redirect the reply into report.txt")
PYEOF
```

## What you learned

- An agent run leaves real artifacts: the conversation ends, the files stay.
- `claude -p` prints the reply on stdout, so ordinary redirection captures it.
- Every run, headless or interactive, is saved as a session the checker (and you) can inspect later.

> **This lab VM:** Claude Code is installed and wired to the lab model gateway, so `claude` works with no sign-in. Setting up your own machine? Follow step 8 of `setup/README.md` once.
