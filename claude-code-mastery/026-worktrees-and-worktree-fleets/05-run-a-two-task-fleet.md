---
type: task
title: "Run a two task fleet"
minutes: 14
---

## Set up

Set up creates a git repo at `/root/mastery/026-fleet` with `tax.py` (a rounding bug) and `report.py` (no docstring), plus two task prompts in `tasks/`. `.gitignore` already covers `.claude/worktrees/`.

```bash
rm -rf /root/mastery/026-fleet && mkdir -p /root/mastery/026-fleet/tasks && cd /root/mastery/026-fleet
git init -q && git symbolic-ref HEAD refs/heads/main && git config user.email dev@example.com && git config user.name 'Dev Lab'
cat > tax.py <<'EOF'
def with_tax(cents):
    return cents + cents * 0.2
EOF
cat > report.py <<'EOF'
def monthly(rows):
    return sum(r['cents'] for r in rows)
EOF
cat > .gitignore <<'EOF'
.claude/worktrees/
runs/
FLEET.md
tasks/
EOF
git add -A && git commit -q -m 'chore: initial'
cat > tasks/fix-tax.md <<'EOF'
In tax.py, make with_tax return an int rounded to the nearest cent. Change only tax.py, then commit it with the message `fix(tax): round with_tax to whole cents`.
EOF
cat > tasks/add-docs.md <<'EOF'
In report.py, add a one-line docstring to monthly. Change only report.py, then commit it with the message `docs(report): document monthly`.
EOF
```

## What to build

Run two independent agent tasks at the same time, each in its own worktree, and collect the results as branches.

1. Record where `main` starts: save `git rev-parse HEAD` to `runs/main-before.txt`.
2. Launch both tasks **in parallel**, headless, each in its own Claude Code worktree (`fix-tax` and `add-docs`), with edits allowed and git pre-approved, saving envelopes to `runs/<name>.json`. Wait for both.
3. Collect: write `FLEET.md` listing each `worktree-*` branch with its commit subjects and diff stat.

`main` must not move, and the main checkout must stay clean.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `claude -p -w <name> "..." &` twice, then `wait`.
- `git log --format=%s main..worktree-fix-tax` lists that branch's commits.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/026-fleet
mkdir -p runs
git rev-parse HEAD > runs/main-before.txt
claude -p -w fix-tax "$(cat tasks/fix-tax.md)" --permission-mode acceptEdits --allowedTools "Bash(git *)" --output-format json > runs/fix-tax.json &
claude -p -w add-docs "$(cat tasks/add-docs.md)" --permission-mode acceptEdits --allowedTools "Bash(git *)" --output-format json > runs/add-docs.json &
wait
git worktree list
for b in worktree-fix-tax worktree-add-docs; do
  echo "## $b"; git log --oneline --format='%s' main.."$b"; git diff --stat main..."$b"
done > FLEET.md
cat FLEET.md
```

</details>

## Check your work

```bash
D=/root/mastery/026-fleet; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
before = text("runs/main-before.txt").strip()
ok(before and sh("git rev-parse main")[1].strip() == before and not sh("git status --porcelain")[1].strip(),
   "main did not move and the main checkout is clean", "main must stay on its starting commit with a clean tree - the fleet works only on its branches")
wt = sh("git worktree list --porcelain")[1]
want = {"worktree-fix-tax": ({"tax.py"}, "fix(tax): round with_tax to whole cents"),
        "worktree-add-docs": ({"report.py"}, "docs(report): document monthly")}
for br, (files, msg) in want.items():
    subj = sh(f"git log --format=%s main..{br}")[1].strip().splitlines()
    changed = set(sh(f"git diff --name-only main...{br}")[1].split())
    ok(f"branch refs/heads/{br}" in wt and subj == [msg] and changed == files,
       f"{br} lives in its own worktree with one commit touching only {sorted(files)}",
       f"{br} should be checked out in a worktree with exactly one commit '{msg}' changing {sorted(files)} - got {subj}, {sorted(changed)}")
probe = sh("git show worktree-fix-tax:tax.py > /tmp/tax026.py && cd /tmp && python3 -c 'import tax026; print(tax026.with_tax(999))'")[1].strip()
ok(probe == "1199", "the tax fix is correct on its branch", f"with_tax(999) on worktree-fix-tax should be 1199 - got {probe!r}")
fl = text("FLEET.md")
ok(all(b in fl and m in fl for b, (_, m) in want.items()), "FLEET.md collects both branches and their commits", "write FLEET.md listing each worktree-* branch with its commit subjects")
PYEOF
```

## What you learned

- A worktree is a separate directory and branch sharing one .git; claude -w creates and enters one.
- Claude Code blocks edits and git commands that would escape the worktree into the main checkout.
- A fleet is independent tasks in parallel worktrees, collected and reviewed as branches.
