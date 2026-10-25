---
type: challenge
title: "Foundations challenge: stand up a project end to end"
minutes: 36
---

## Set up

Set up creates `/root/mastery/020-invoicer`, a git repo with an invoice module whose test fails, and an untracked `.env` holding a (fake) payments key.

```bash
rm -rf /root/mastery/020-invoicer && mkdir -p /root/mastery/020-invoicer && cd /root/mastery/020-invoicer
git init -q && git symbolic-ref HEAD refs/heads/main && git config user.email dev@example.com && git config user.name 'Dev Lab'
cat > invoice.py <<'EOF'
def total_cents(lines, tax_rate):
    subtotal = sum(l["unit_cents"] * l["qty"] for l in lines)
    tax = round(lines[0]["unit_cents"] * tax_rate)
    return subtotal + tax
EOF
cat > test_invoice.py <<'EOF'
import unittest

from invoice import total_cents


class InvoiceTest(unittest.TestCase):
    def test_tax_on_subtotal(self):
        lines = [{"unit_cents": 1000, "qty": 2}, {"unit_cents": 500, "qty": 1}]
        self.assertEqual(total_cents(lines, 0.1), 2750)
EOF
git add -A && git commit -q -m 'feat: invoice totals'
cat > .env <<'EOF'
STRIPE_KEY=sk_test_fake_020_invoicer
EOF
```

## What to build

Take `/root/mastery/020-invoicer` from "fresh clone" to "fixed, guarded, and committed" using only Claude Code. No hints this time.

**Done means:**

- `CLAUDE.md` names the test command and requires Conventional Commits.
- Project settings deny reading `.env` and allow the test command; the folder is trusted.
- A project `/check` command (or skill) runs the tests and replies exactly `CHECK: PASS` or `CHECK: FAIL - <test>`.
- A headless agent run fixed the bug, and a headless `/check` run reported `CHECK: PASS`.
- The fix and your project setup are committed with a `fix:` Conventional Commits subject; `.gitignore` keeps out `.env` and Python caches, `.env` was never committed, and the tree is clean.
- Keep the envelopes of the fix run, the `/check` run, and the commit run in `<git dir>/runs/` as `fix.json`, `check.json`, and `commit.json`.

When everything is in place, press **Submit**.

<details><summary>Solution</summary>

```bash
cd /root/mastery/020-invoicer
git status --short
printf '.env\n__pycache__/\n' > .gitignore
cat > CLAUDE.md <<'EOF'
# invoicer

## Commands
- Tests: `python3 -m unittest`

## Conventions
- Money is integer cents.
- Commit messages use Conventional Commits: type(scope): imperative subject, 72 characters or fewer.
EOF
mkdir -p .claude/commands
cat > .claude/settings.json <<'EOF'
{
  "permissions": {
    "allow": ["Bash(python3 -m unittest *)", "Bash(git add *)", "Bash(git commit *)"],
    "ask": ["Bash(git push *)"],
    "deny": ["Read(./.env)", "Bash(git add -A *)", "Bash(git commit -a *)"]
  }
}
EOF
cat > .claude/commands/check.md <<'EOF'
---
description: Run the test suite and report one status line
---

Run `python3 -m unittest`. Reply with exactly one line: `CHECK: PASS` if every test passed, otherwise `CHECK: FAIL - <first failing test>`.
EOF
[ -f ~/.claude.json ] || echo '{}' > ~/.claude.json
tmp=$(mktemp) && jq --arg p "$(pwd -P)" '.projects[$p].hasTrustDialogAccepted = true' ~/.claude.json > "$tmp" && mv "$tmp" ~/.claude.json
mkdir -p "$(git rev-parse --git-dir)/runs" && R="$(git rev-parse --git-dir)/runs"
claude -p "The invoice test fails. Find the bug in invoice.py and fix it, then run the tests." --permission-mode acceptEdits --output-format json > "$R/fix.json"
claude -p "/check" --output-format json > "$R/check.json"
claude -p "Stage invoice.py, CLAUDE.md, .claude/, and .gitignore by name with git add, then commit them with a Conventional Commits message for the bug fix. Do not stage anything else." --output-format json > "$R/commit.json"
git log --oneline -2 && git status --short
```

</details>

## Check your work

```bash
D=/root/mastery/020-invoicer; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
run = lambda n: load(os.path.join(gd, "runs", n + ".json")) or {}
c = text("CLAUDE.md")
ok("python3 -m unittest" in c and re.search(r"conventional commits", c, re.I), "CLAUDE.md names the test command and the commit convention",
   "CLAUDE.md should name the test command and require Conventional Commits")
s = load(".claude/settings.json") or {}
p = s.get("permissions") or {}
ok(any(re.fullmatch(r"Read\((\./)?\.env\)", d) for d in p.get("deny") or []) and "Bash(python3 -m unittest *)" in (p.get("allow") or []),
   "project settings deny reading .env and allow the tests", "project settings must deny Read(./.env) and allow Bash(python3 -m unittest *)")
cmd = text(".claude/commands/check.md") or text(".claude/skills/check/SKILL.md")
ok("CHECK: PASS" in cmd, "a /check command or skill reports CHECK: PASS or FAIL", "create a /check command (or skill) that replies CHECK: PASS or CHECK: FAIL - ...")
probe = sh("python3 -c 'from invoice import total_cents as t; print(t([{\"unit_cents\": 333, \"qty\": 3}], 0.2))'")[1].strip()
ok(sh("python3 -m unittest -q")[0] == 0 and probe == "1199", "the bug is fixed - tax is on the subtotal", f"tax must apply to the whole subtotal - total_cents for 3 x 333 at 20% gave {probe}")
fx = run("fix")
ok(fx.get("subtype") == "success" and not fx.get("permission_denials"), "the fix was made by a headless agent run", "keep the fix run's envelope as <git dir>/runs/fix.json")
ck = run("check")
f, rows = transcript(ck.get("session_id") or "none")
ok("<command-name>/check</command-name>" in json.dumps(rows) and (ck.get("result") or "").strip() == "CHECK: PASS" and not ck.get("permission_denials"),
   "/check ran headless with the trusted allow rule and passed", f"run /check headless and keep <git dir>/runs/check.json - got {ck.get('result')!r}, denials {ck.get('permission_denials')}")
subj = sh("git log -1 --format=%s")[1].strip()
files = set(sh("git show --name-only --format= HEAD")[1].split())
tracked = set(sh("git ls-files")[1].split())
ok(re.fullmatch(r"fix(\([a-z0-9-]+\))?: [a-z].{0,70}", subj) and "invoice.py" in files and ".env" not in tracked and ".env" in text(".gitignore").split(),
   f"the fix is committed as {subj!r}, and .env is ignored and untracked", f"commit the fix with a fix: message, keep .env out of git via .gitignore - subject {subj!r}")
ok(not sh("git status --porcelain")[1].strip(), "the working tree is clean", "commit CLAUDE.md, .claude/, and .gitignore too - git status should be empty")
PYEOF
```

## What you learned

- A new repo gets rules, guardrails, a reusable check, and a checkpointed, verified agent run - in that order.
- Trust, allow rules, and deny rules decide what a headless run can actually do.
- The proof is in artifacts: tests, envelopes, git history, and a clean tree.
