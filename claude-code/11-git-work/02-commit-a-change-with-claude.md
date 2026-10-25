---
type: task
title: "Commit a change with Claude"
minutes: 12
---

## Set up

Set up creates a git repo in `/root/cc-lab/11-git` with one commit and an uncommitted change: a new `farewell()` function and a README line.

```bash
mkdir -p /root/cc-lab/11-git && cd /root/cc-lab/11-git
if [ ! -d .git ]; then
git init -q && git symbolic-ref HEAD refs/heads/main
git config user.name "Lab Learner"
git config user.email "learner@example.com"
cat > greet.py <<'EOF'
def hello(name):
    return f"Hello, {name}!"
EOF
cat > README.md <<'EOF'
# greet

Functions:
- hello(name) says hello
EOF
git add . && git commit -qm "initial: greet module"
cat > greet.py <<'EOF'
def hello(name):
    return f"Hello, {name}!"


def farewell(name):
    return f"Goodbye, {name}!"
EOF
echo "- farewell(name) says goodbye" >> README.md
fi
git status --short
claude --version
```

## What to build

Let Claude read the diff, stage it and commit it with a Conventional Commits message - with permission for exactly those git commands and nothing else (no push):

```bash
cd /root/cc-lab/11-git
claude -p "Look at the uncommitted changes, then stage them and commit with a Conventional Commits message (type: short summary, under 72 characters) that describes what changed. Do not push." \
  --allowedTools "Bash(git status:*)" "Bash(git diff:*)" "Bash(git add:*)" "Bash(git commit:*)" --max-turns 10
git log --oneline -3
git show --stat HEAD
```

Check the result: one new commit, `type: summary` under 72 characters, both changed files in it, a clean working tree.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Conventional Commits types: feat, fix, docs, refactor, test, chore.
- If the message isn't right, `git commit --amend` lets you (or Claude) fix it before anything is pushed.

</details>

<details><summary>Solution</summary>

```bash
cd /root/cc-lab/11-git
claude -p "Look at the uncommitted changes, then stage them and commit with a Conventional Commits message (type: short summary, under 72 characters) that describes what changed. Do not push." \
  --allowedTools "Bash(git status:*)" "Bash(git diff:*)" "Bash(git add:*)" "Bash(git commit:*)" --max-turns 10
git log --oneline -3
git show --stat HEAD
```

</details>

## Check your work

```bash
D=/root/cc-lab/11-git; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
rc, st, _ = sh("git status --porcelain")
ok(rc == 0 and not st.strip(), "the working tree is clean - the change was committed", f"uncommitted changes remain: {st.strip()[:200]}")
rc, n, _ = sh("git rev-list --count HEAD")
ok(rc == 0 and n.strip().isdigit() and int(n) >= 2, "there's a new commit on top of the initial one", "no new commit yet")
rc, subj, _ = sh("git log -1 --format=%s")
subj = subj.strip()
ok(re.match(r"^(feat|fix|docs|refactor|test|chore|style|perf)(\([\w-]+\))?!?: \S.{2,}$", subj) and len(subj) <= 72, f"the commit message is Conventional Commits: {subj!r}", f"the commit subject should look like 'feat: add farewell greeting' (under 72 chars) - got {subj!r}")
rc, files, _ = sh("git show --name-only --format= HEAD")
ok({"greet.py", "README.md"} <= set(files.split()), "the commit contains both greet.py and README.md", f"the commit should contain greet.py and README.md - got {files.split()}")
rc, email, _ = sh("git log -1 --format=%ae")
ok(email.strip() == "learner@example.com", "the commit uses the repo's configured author", f"the commit author should be learner@example.com - got {email.strip()}")
def read_then_commit(rows):
    cmds = [u["input"].get("command", "") for u in uses(rows) if u.get("name") == "Bash"]
    d = next((i for i, c in enumerate(cmds) if c.startswith("git diff") or c.startswith("git status")), None)
    return d is not None and any(c.startswith("git commit") for c in cmds[d + 1:])
ok([r for r in sessions(os.getcwd()) if read_then_commit(r)], "Claude looked at the changes before committing them", "no session here where Claude ran git diff/status and then git commit")
PYEOF
```

## What you learned

- Claude writes commit messages from the real diff; Conventional Commits is `type: summary`.
- Grant exactly the git commands a job needs - leave push out unless it's the job.
- Review the staged files and the diff before anything lands.
