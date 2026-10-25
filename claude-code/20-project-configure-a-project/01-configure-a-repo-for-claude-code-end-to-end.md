---
type: task
title: "Configure a repo for Claude Code end to end"
minutes: 45
---

## Scenario

Your team is adopting Claude Code. Before anyone points it at `notes-api`, you set the repository up properly: memory so Claude knows how the project works, a shared command for the team's most common request, and permission rules so the agent can do routine work without asking - and can never touch the token or push.

## Set up

Set up creates `notes-api`, a small git repository in `/root/cc-lab/20-configure`, with a `.env` token and an uncommitted change to `app.py` that deserves a review.

```bash
mkdir -p /root/cc-lab/20-configure && cd /root/cc-lab/20-configure
if [ ! -d .git ]; then
git init -q && git symbolic-ref HEAD refs/heads/main
git config user.name "Lab Learner" && git config user.email "learner@example.com"
mkdir -p tests scripts
cat > app.py <<'EOF'
NOTES = {}


def add_note(note_id, text):
    if not text.strip():
        raise ValueError("note text is empty")
    NOTES[note_id] = text
    return note_id


def get_note(note_id):
    return NOTES.get(note_id)
EOF
cat > tests/__init__.py <<'EOF'

EOF
cat > tests/test_app.py <<'EOF'
import unittest

import app


class AppTest(unittest.TestCase):
    def test_add_and_get(self):
        app.add_note("n1", "hello")
        self.assertEqual(app.get_note("n1"), "hello")


if __name__ == "__main__":
    unittest.main()
EOF
cat > scripts/test.sh <<'EOF'
#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
mkdir -p .lab && touch .lab/tests-ran
python3 -m unittest discover -s tests -q
EOF
chmod +x scripts/test.sh
cat > .gitignore <<'EOF'
.env
.lab/
__pycache__/
EOF
cat > .env <<'EOF'
NOTES_API_TOKEN=tok_fake_9921
EOF
cat > README.md <<'EOF'
# notes-api

A tiny notes service.
EOF
git add . && git commit -qm "initial: notes api"
cat > app.py <<'EOF'
NOTES = {}


def add_note(note_id, text):
    NOTES[note_id] = text
    return note_id


def get_note(note_id):
    return NOTES.get(note_id)


def delete_note(note_id):
    del NOTES[note_id]
EOF
fi
git status --short
claude --version
```

## What to build

In `/root/cc-lab/20-configure`, create:

1. **`CLAUDE.md`** with `## Commands` (the test command is `./scripts/test.sh`), `## Conventions` (at least two bullets) and `## Do not` (never read `.env`, never push).
2. **`.claude/commands/diff-review.md`** - a `/diff-review` command with a `description`, that includes the uncommitted diff (allow `Bash(git diff:*)` in `allowed-tools` and use !`git diff`, or tell Claude to run it) and asks for one finding per line in the form `- [high|medium|low] file:line - issue`.
3. **`.claude/settings.json`** - allow `./scripts/test.sh`, `git diff` and `git status`; deny reading `./.env`, `git push` and `rm`.
4. A personal **`.claude/settings.local.json`** that git ignores.
5. Open `claude` in the folder once, answer **Yes** to "Do you trust the files in this folder?", then `/exit`. Until a folder is trusted, Claude Code ignores its project **allow** rules (deny rules always apply). On a machine with no console, the warning it prints tells you the one-line alternative - setting `hasTrustDialogAccepted` for the folder in `~/.claude.json`.
6. Prove it works:

```bash
cd /root/cc-lab/20-configure
echo ".claude/settings.local.json" >> .gitignore
echo '{}' > .claude/settings.local.json
[ -f ~/.claude.json ] || echo '{}' > ~/.claude.json
tmp=$(mktemp) && jq --arg p "$(pwd -P)" '.projects[$p].hasTrustDialogAccepted = true' ~/.claude.json > "$tmp" && mv "$tmp" ~/.claude.json
claude -p "/diff-review" --max-turns 6 > review.md
cat review.md
claude -p "Run the tests with ./scripts/test.sh, then push the branch to origin." --max-turns 6 --output-format json > push.json
jq '{result, permission_denials}' push.json
```

`review.md` should flag the removed validation; `push.json` should show the tests ran and the push was denied.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `/review` is a built-in command - that's why this one is called `/diff-review`.
- Allowed: tests and read-only git. Denied: secrets, pushing, deleting.

</details>

<details><summary>Solution</summary>

```bash
mkdir -p /root/cc-lab/20-configure/.claude/commands && cd /root/cc-lab/20-configure
cat > CLAUDE.md <<'EOF'
# notes-api

A tiny in-memory notes service. Python 3, standard library only.

## Commands
- Run the tests: `./scripts/test.sh`

## Conventions
- Validate input at the edge: reject empty note text with ValueError.
- Every public function in app.py gets a test in tests/.

## Do not
- Never read or print .env - it holds the API token.
- Never push; open a pull request for review instead.
EOF
cat > .claude/commands/diff-review.md <<'EOF'
---
description: Review the uncommitted changes for bugs and missing tests
allowed-tools: Bash(git diff:*)
---
Here are the uncommitted changes:

!`git diff`

Review them for bugs, removed validation and missing tests. Report each finding on its own line as:
- [high|medium|low] file:line - issue

Report findings only, highest severity first. No preamble.
EOF
cat > .claude/settings.json <<'EOF'
{
  "permissions": {
    "allow": ["Bash(./scripts/test.sh:*)", "Bash(git diff:*)", "Bash(git status:*)"],
    "deny": ["Read(./.env)", "Bash(git push:*)", "Bash(rm:*)"]
  }
}
EOF
cd /root/cc-lab/20-configure
echo ".claude/settings.local.json" >> .gitignore
echo '{}' > .claude/settings.local.json
[ -f ~/.claude.json ] || echo '{}' > ~/.claude.json
tmp=$(mktemp) && jq --arg p "$(pwd -P)" '.projects[$p].hasTrustDialogAccepted = true' ~/.claude.json > "$tmp" && mv "$tmp" ~/.claude.json
claude -p "/diff-review" --max-turns 6 > review.md
cat review.md
claude -p "Run the tests with ./scripts/test.sh, then push the branch to origin." --max-turns 6 --output-format json > push.json
jq '{result, permission_denials}' push.json
```

</details>

## Check your work

```bash
D=/root/cc-lab/20-configure; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
md = text("CLAUDE.md")
secs, cur = {}, None
for line in md.splitlines():
    m = re.match(r"^##\s+(.+?)\s*$", line)
    if m:
        cur = m.group(1).strip().lower()
        secs[cur] = []
    elif cur and line.strip():
        secs[cur].append(line.strip())
ok("./scripts/test.sh" in " ".join(secs.get("commands", [])), "CLAUDE.md ## Commands gives ./scripts/test.sh", "CLAUDE.md needs '## Commands' with ./scripts/test.sh")
ok(sum(1 for l in secs.get("conventions", []) if l.startswith(("-", "*"))) >= 2, "CLAUDE.md ## Conventions has at least two bullets", "add at least two bullets under '## Conventions'")
dn = " ".join(secs.get("do not", [])).lower()
ok(".env" in dn and "push" in dn, "CLAUDE.md ## Do not covers .env and pushing", "'## Do not' should forbid reading .env and pushing")
cmd = text(".claude/commands/diff-review.md")
fm = re.match(r"^---\n(.*?)\n---\n(.*)$", cmd, re.S)
ok(fm and re.search(r"^description:\s*\S", fm.group(1), re.M), "/diff-review exists with a description", "create .claude/commands/diff-review.md with a description in its front matter")
ok(fm and "git diff" in cmd and re.search(r"\[\s*high", fm.group(2)), "/diff-review works on git diff and asks for '- [severity] file:line - issue'", "the command should use git diff and ask for '- [high|medium|low] file:line - issue' lines")
s = load(".claude/settings.json") or {}
p = s.get("permissions") or {}
allow = [a.replace(" ", "") for a in p.get("allow") or []]
deny = [d.replace(" ", "") for d in p.get("deny") or []]
ok(any(a.startswith("Bash(./scripts/test.sh") for a in allow) and any(a.startswith("Bash(gitdiff") for a in allow) and any(a.startswith("Bash(gitstatus") for a in allow), "allow: the tests, git diff and git status", f"allow should cover ./scripts/test.sh, git diff and git status - got {p.get('allow')}")
ok(any(d in ("Read(./.env)", "Read(.env)", "Read(**/.env)") for d in deny) and any(d.startswith("Bash(gitpush") for d in deny) and any(d.startswith("Bash(rm") for d in deny), "deny: .env, git push and rm", f"deny should cover Read(./.env), git push and rm - got {p.get('deny')}")
ok(not any(x in a for a in allow for x in ("push", ".env", "rm", "Bash(*)")), "nothing dangerous is allowed", "remove push/.env/rm/Bash(*) from allow")
rc1, _, _ = sh("git check-ignore -q .claude/settings.local.json")
rc2, _, _ = sh("git check-ignore -q .claude/settings.json")
ok(Path(".claude/settings.local.json").exists() and rc1 == 0 and rc2 != 0, "settings.local.json exists and git ignores it (settings.json stays shared)", "create .claude/settings.local.json and add it - only it - to .gitignore")
findings = [l for l in text("review.md").splitlines() if re.match(r"^\s*-\s*\[(high|medium|low)\]\s*\S+", l, re.I)]
ok(findings, f"review.md has {len(findings)} finding(s) in the agreed format", "review.md should have lines like '- [high] app.py:4 - ...' from claude -p \"/diff-review\"")
ok(ran(r"<command-name>/diff-review</command-name>"), "the team command ran as /diff-review", "run claude -p \"/diff-review\" in this folder")
push = load("push.json") or {}
den = push.get("permission_denials") or []
ok(Path(".lab/tests-ran").exists(), "./scripts/test.sh ran without asking (allow rule + trusted folder)", "the tests never ran - allow Bash(./scripts/test.sh:*) and trust the folder")
ok(any("git push" in json.dumps(d.get("tool_input")) for d in den), "the push was denied", f"push.json should list git push in permission_denials - got {[d.get('tool_input') for d in den]}")
ok("tok_fake_9921" not in text("review.md") + json.dumps(push), "the .env token appears nowhere", "the token from .env leaked into review.md or push.json")
PYEOF
```

## What you learned

- A Claude-ready repo has three layers: memory (CLAUDE.md), shared commands, and permission rules.
- Allow the routine, deny the dangerous, keep personal settings out of git.
- Prove each layer with a real run: the command's output, a tool that ran, a push that was refused.
