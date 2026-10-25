---
type: task
title: "Commit a change with an agent-written message"
minutes: 23
---

## Set up

Set up creates a git repo at `/root/mastery/019-commit` with a VAT bug fix and its test **staged**, plus an untracked `scratch.txt` that must not be committed.

```bash
rm -rf /root/mastery/019-commit && mkdir -p /root/mastery/019-commit && cd /root/mastery/019-commit
git init -q && git symbolic-ref HEAD refs/heads/main && git config user.email dev@example.com && git config user.name 'Dev Lab'
cat > pricing.py <<'EOF'
def vat(cents, rate=0.2):
    return int(cents * rate)
EOF
git add -A && git commit -q -m 'feat: add vat helper'
cat > pricing.py <<'EOF'
def vat(cents, rate=0.2):
    return round(cents * rate)
EOF
cat > test_pricing.py <<'EOF'
import unittest

from pricing import vat


class VatTest(unittest.TestCase):
    def test_rounds_to_nearest_cent(self):
        self.assertEqual(vat(999), 200)
EOF
git add pricing.py test_pricing.py
cat > scratch.txt <<'EOF'
TODO: ask finance about reverse charge
EOF
```

## What to build

You decided what goes in the commit by staging it. Let the agent write the message and commit exactly that.

1. Check `git status --short`: two staged files, one untracked note.
2. Run this headless, pre-approving only `git diff` and `git commit` (save the envelope outside the repo for now):
   > Read the staged diff with git diff --cached. Commit only the staged changes with a Conventional Commits message: type and scope from the diff, an imperative subject of 72 characters or fewer, and a body explaining why. Do not stage anything else.
3. Read the result with `git log -1 --format=%B`. Is the type right for a bug fix?
4. Keep the envelope inside the git directory, where it can never be committed: `<git dir>/runs/commit.json` - normally `.git/runs/commit.json`; `git rev-parse --git-dir` prints the git directory.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `--allowedTools "Bash(git diff *)" "Bash(git commit *)"` - read-only git needs no rule, but listing it is harmless.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/019-commit
git status --short
claude -p "Read the staged diff with git diff --cached. Commit only the staged changes with a Conventional Commits message: type and scope from the diff, an imperative subject of 72 characters or fewer, and a body explaining why. Do not stage anything else." --allowedTools "Bash(git diff *)" "Bash(git commit *)" --output-format json > /tmp/commit-019.json
git log -1 --format=%B
R="$(git rev-parse --git-dir)/runs" && mkdir -p "$R" && mv /tmp/commit-019.json "$R/commit.json"
```

</details>

## Check your work

```bash
D=/root/mastery/019-commit; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
def transcript(sid):
    for f in glob.glob(os.path.expanduser(f"~/.claude/projects/*/{sid}.jsonl")):
        rows = []
        for line in open(f, errors="replace"):
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
        return f, rows
    return None, []

gd = sh("git rev-parse --git-dir")[1].strip()
env = load(os.path.join(gd, "runs/commit.json")) or {}
f, rows = transcript(env.get("session_id") or "none")
cmds = [u["input"].get("command", "") for u in uses(rows) if u.get("name") == "Bash"]
ok(any("git diff --cached" in c or "git diff --staged" in c for c in cmds) and any(c.lstrip().startswith("git commit") for c in cmds),
   "the agent read the staged diff and made the commit itself",
   "save the commit run's envelope as <git dir>/runs/commit.json - its transcript should show git diff --cached and git commit")
ok(not any(re.search(r"git add (-A|\.|--all)|git commit -a", c) for c in cmds), "the agent did not stage anything extra", "the agent ran git add -A or commit -a - commit only what was staged")
msg = sh("git log -1 --format=%B")[1].strip()
subj, _, body = msg.partition("\n")
ok(re.fullmatch(r"fix(\([a-z0-9-]+\))?: [a-z].{0,70}[^.]", subj) and len(subj) <= 72,
   f"the subject is a Conventional Commits fix: {subj!r}", f"the subject should look like 'fix(scope): imperative summary' within 72 chars - got {subj!r}")
ok(body.strip() and not body.startswith(" "), "the message has a body explaining why", "add a body after a blank line explaining why")
files = set(sh("git show --name-only --format= HEAD")[1].split())
st = sh("git status --porcelain")[1]
ok(files == {"pricing.py", "test_pricing.py"} and "?? scratch.txt" in st and sh("git rev-list --count HEAD")[1].strip() == "2",
   "the commit holds exactly the staged fix and test; scratch.txt stays untracked",
   f"HEAD should contain only pricing.py and test_pricing.py - got {sorted(files)}; status {st!r}")
PYEOF
```

## What you learned

- Read-only git runs without prompts; commits and pushes need explicit rules.
- Stage the changes yourself; let the agent describe and commit only what is staged.
- Conventional Commits: type(scope): imperative subject of 72 characters or fewer, then a body for why.
