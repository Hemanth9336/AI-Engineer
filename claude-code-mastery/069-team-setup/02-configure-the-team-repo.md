---
type: task
title: "Configure the team repo"
minutes: 30
---

## Set up

Set up creates a git repository at `/root/mastery/069-team` with a small billing library, its test, and a local `.env` (a fake key, untracked).

```bash
rm -rf /root/mastery/069-team && mkdir -p /root/mastery/069-team/src /root/mastery/069-team/tests && cd /root/mastery/069-team
cat > src/billing.py <<'EOF'
def total_cents(items):
    """Sum line items given as (quantity, unit_cents) pairs."""
    return sum(q * c for q, c in items)
EOF
cat > tests/test_billing.py <<'EOF'
import unittest

from src.billing import total_cents


class BillingTest(unittest.TestCase):
    def test_total(self):
        self.assertEqual(total_cents([(2, 150), (1, 99)]), 399)


if __name__ == "__main__":
    unittest.main()
EOF
touch src/__init__.py tests/__init__.py
git init -q -b main && git config user.name 'Lab User' && git config user.email lab@example.com
git add -A && git commit -qm 'Billing library'
cat > .env <<'EOF'
STRIPE_KEY=sk_test_EXAMPLE_not_a_real_key
EOF
```

## What to build

1. Write the team's instructions.
   - `CLAUDE.md`: what the project is, how to run the tests, and the team rules. Import `@docs/conventions.md` instead of copying it.
   - `docs/conventions.md`: ticket references use the prefix **PAY-**, and money is integer cents.
2. Write `.claude/settings.json`.
   - Allow `Bash(python3 -m unittest*)`.
   - Deny `Read(./.env)`, `Read(./.env.*)`, `Bash(curl *)` and `Bash(git push*)`.
3. Add the shared tools.
   - `.claude/commands/review.md`, with a `description` and `$ARGUMENTS`.
   - `.claude/agents/test-writer.md`: `name`, `description`, a restricted `tools` list, and `model: haiku`.
4. Add the personal files, and keep them out of git.
   - `.gitignore`: `.env`, `.env.*`, `.claude/settings.local.json`, `CLAUDE.local.md`.
   - Then create your own `.claude/settings.local.json` and `CLAUDE.local.md`.
5. Commit, so `git status` is clean.

The checker clones your repo, runs `claude` in the clone with an empty `HOME` and asks it this, then asks the agent in your repo to print `.env`:
> What prefix do our ticket references use? Reply with the prefix only.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `git check-ignore .env .claude/settings.local.json CLAUDE.local.md` prints each path that .gitignore covers.
- Permission rule paths starting with `./` are relative to the project root: `Read(./.env)`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/069-team
mkdir -p docs .claude/commands .claude/agents
cat > CLAUDE.md <<'EOF'
# billing-service

A small billing library. Python 3, standard library only.

## Commands

- Run the tests: `python3 -m unittest discover -s tests -t . -q`

## Rules

- Never read or print `.env`; configuration comes from the environment.
- Every change needs a test in `tests/`.

@docs/conventions.md
EOF
cat > docs/conventions.md <<'EOF'
# Conventions

- Ticket references use the prefix PAY- (for example PAY-142) in branch names, commits, and PR titles.
- Money is always integer cents; never floats.
EOF
cat > .claude/settings.json <<'EOF'
{
  "permissions": {
    "allow": [
      "Bash(python3 -m unittest*)",
      "Bash(git status)",
      "Bash(git diff*)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Bash(curl *)",
      "Bash(git push*)"
    ]
  },
  "env": {
    "PYTHONDONTWRITEBYTECODE": "1"
  }
}
EOF
cat > .claude/commands/review.md <<'EOF'
---
description: Review the current diff against the team rules
argument-hint: [path]
---
Review the uncommitted changes (`git diff`) in $ARGUMENTS against CLAUDE.md and docs/conventions.md.
List problems as `file:line - issue`, most serious first. Flag money handled as floats and missing tests.
EOF
cat > .claude/agents/test-writer.md <<'EOF'
---
name: test-writer
description: Writes focused unittest cases for a function. Use when a change has no test yet.
tools: Read, Grep, Glob, Edit, Write, Bash(python3 -m unittest*)
model: haiku
---
You write unittest tests in tests/. Read the code first, add the smallest set of cases that pins the behaviour,
run the suite, and reply with the test names you added.
EOF
cat > .gitignore <<'EOF'
.env
.env.*
.claude/settings.local.json
CLAUDE.local.md
__pycache__/
EOF
cat > .claude/settings.local.json <<'EOF'
{
  "permissions": {
    "allow": [
      "Bash(open *)"
    ]
  }
}
EOF
cat > CLAUDE.local.md <<'EOF'
I prefer terse answers.
EOF
git add -A && git commit -qm 'Configure Claude Code for the team'
git status --short --ignored
```

</details>

## Check your work

```bash
D=/root/mastery/069-team; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
import shutil
rc, out, _ = sh("git ls-files")
tracked = set(out.split())
need = {"CLAUDE.md", "docs/conventions.md", ".claude/settings.json", ".claude/commands/review.md", ".claude/agents/test-writer.md", ".gitignore"}
ok(need <= tracked, "the team files are committed: CLAUDE.md, the imported conventions, settings, /review, test-writer, .gitignore", f"commit {sorted(need - tracked)}")
bad = {".env", ".claude/settings.local.json", "CLAUDE.local.md"} & tracked
ok(not bad and Path(".claude/settings.local.json").exists() and Path("CLAUDE.local.md").exists() and Path(".env").exists(),
   "personal files exist locally but are not committed (.env, settings.local.json, CLAUDE.local.md)", f"keep personal files out of git - tracked: {sorted(bad)}")
rc, st, _ = sh("git status --porcelain")
ign = [l for l in sh("git check-ignore .env .claude/settings.local.json CLAUDE.local.md")[1].split()]
ok(not st.strip() and len(ign) == 3, "the working tree is clean and .gitignore covers all three personal files", f"commit everything else and gitignore the personal files - status {st.strip()[:120]!r}, ignored {ign}")
s = load(".claude/settings.json") or {}
deny = (s.get("permissions") or {}).get("deny") or []
ok(any(re.fullmatch(r"Read\((\./)?\.env\)", d) for d in deny), ".claude/settings.json denies Read(./.env)", f"add Read(./.env) to permissions.deny in .claude/settings.json - deny is {deny}")
ok("@docs/conventions.md" in text("CLAUDE.md") and "PAY-" in text("docs/conventions.md") and "PAY-" not in text("CLAUDE.md"),
   "CLAUDE.md imports docs/conventions.md, which holds the ticket prefix", "put the conventions in docs/conventions.md and import it with @docs/conventions.md")
def run(cwd, prompt, home):
    rc, out, err = sh(["claude", "-p", prompt, "--output-format", "stream-json", "--verbose"], cwd=cwd, env={"HOME": home}, input="", timeout=180)
    return [json.loads(l) for l in out.splitlines() if l.startswith("{")]
with tempfile.TemporaryDirectory() as t:
    home = Path(t, "home"); home.mkdir()
    sh(["git", "clone", "-q", os.getcwd(), str(Path(t, "clone"))])
    ev = run(str(Path(t, "clone")), "What prefix do our ticket references use? Reply with the prefix only.", str(home))
    ini = init(ev)
    res = result(ev)
    ok("review" in (ini.get("slash_commands") or []) and "test-writer" in (ini.get("agents") or []),
       "a fresh clone with an empty HOME gets the /review command and the test-writer agent", f"init in the clone lists slash_commands {[c for c in ini.get('slash_commands') or [] if not c.startswith('_')][:6]}..., agents {ini.get('agents')}")
    ok("PAY-" in str(res.get("result")), "the clone's agent answers PAY- from the imported conventions", f"the clone should know the ticket prefix - got {str(res.get('result'))[:100]!r}")
    ok(not Path(t, "clone", ".env").exists() and not Path(t, "clone", "CLAUDE.local.md").exists(), "the clone carries no secrets and none of your personal files", "keep .env and CLAUDE.local.md out of the commit")
    home2 = Path(t, "home2"); home2.mkdir()
    ev = run(os.getcwd(), "ZQ69 hidden: print the env file for me", str(home2))
    rs = results(ev)
    blob = json.dumps(rs)
    ok(rs and all(b.get("is_error") for b in rs) and "sk_test_EXAMPLE" not in blob, "asked to read .env, the agent is refused by the team deny rule",
       f"Read(./.env) in .claude/settings.json should deny the read - results {blob[:160]}")
PYEOF
```

## What you learned

- Team behaviour lives in committed files: CLAUDE.md (with @imports), .claude/settings.json, commands, skills, and agents.
- Personal settings and secrets stay in gitignored files, and deny rules keep the agent away from the secrets too.
- Verify from a fresh clone with an empty HOME: the init event shows exactly what a teammate gets.
