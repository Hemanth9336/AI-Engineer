---
type: task
title: "Build the commit and changelog bot"
minutes: 30
---

## Set up

Set up creates a git repo at `/root/mastery/043-commitbot` with `src/greet.py` and a `CHANGELOG.md`, then leaves one uncommitted change: a new `farewell` function.

```bash
rm -rf /root/mastery/043-commitbot && mkdir -p /root/mastery/043-commitbot/src && cd /root/mastery/043-commitbot
git init -q -b main && git config user.name 'Lab Learner' && git config user.email learner@lab.invalid
cat > src/greet.py <<'EOF'
def greet(name):
    return f"Hello, {name}!"
EOF
cat > CHANGELOG.md <<'EOF'
# Changelog

## Unreleased

## 1.0.0 - 2026-10-01

- First release.
EOF
git add -A && git commit -qm 'feat: greet'
cat > src/greet.py <<'EOF'
def greet(name):
    return f"Hello, {name}!"


def farewell(name):
    return f"Goodbye, {name}."
EOF
git status --short
```

## What to build

Build `commit_bot.sh` and its helpers in `.commitbot/`:

1. `.commitbot/schema.json`:
   - `type`: an enum of `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.
   - `scope`: matches `^[a-z0-9-]*$`.
   - `subject`: `maxLength` 72.
   - `body` and `changelog`.
   - All required, no additional properties.
2. `.commitbot/prompt.txt`:
   > The staged git diff is on stdin. Propose a conventional commit for it: type, scope (lowercase, may be empty), an imperative subject under 72 characters with no trailing period, a short body explaining the change, and a one-line user-facing changelog entry.
3. `.commitbot/apply.py <run.json>`: validate the proposal.
   - Reject it unless the subtype is success, there is a `structured_output`, the type is valid, the scope is lowercase, and the subject has at most 72 characters and no trailing period.
   - Add `- <changelog>` under `## Unreleased`.
   - Commit `type(scope): subject` (or `type: subject` when the scope is empty), with the body as the message body.
   - Exit 1 on anything invalid, without committing.
4. `commit_bot.sh`:
   - On a clean tree, print `nothing to commit` and exit 0.
   - Otherwise `git add -A`, then pipe `git diff --cached` into `claude -p` with `--tools ""`, the schema, and `--max-turns 3`, saving `.commitbot/last-run.json` (git-ignore it).
   - Run `apply.py`. If it fails, `git reset -q` and exit 1.
5. Run the bot to commit the pending change, then run it again on the clean tree.

The checker clones your repo to feed `apply.py` five invalid proposals and one valid one, and runs the bot with a fake `claude` that fails.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Piping into `claude -p` appends stdin to the prompt - here that is exactly what you want.
- Let the validator, not the model, decide what gets committed.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/043-commitbot
mkdir -p .commitbot
cat > .commitbot/schema.json <<'EOF'
{
  "type": "object",
  "properties": {
    "type": { "type": "string", "enum": ["feat", "fix", "docs", "refactor", "test", "chore"] },
    "scope": { "type": "string", "pattern": "^[a-z0-9-]*$" },
    "subject": { "type": "string", "minLength": 1, "maxLength": 72 },
    "body": { "type": "string" },
    "changelog": { "type": "string", "minLength": 1 }
  },
  "required": ["type", "scope", "subject", "body", "changelog"],
  "additionalProperties": false
}
EOF
cat > .commitbot/prompt.txt <<'EOF'
The staged git diff is on stdin. Propose a conventional commit for it: type, scope (lowercase, may be empty), an imperative subject under 72 characters with no trailing period, a short body explaining the change, and a one-line user-facing changelog entry.
EOF
cat > .commitbot/apply.py <<'EOF'
#!/usr/bin/env python3
"""apply.py <run.json> - validate the agent's commit proposal, add the changelog entry, and commit. Exit 1 if anything is invalid."""
import json
import re
import subprocess
import sys

TYPES = {"feat", "fix", "docs", "refactor", "test", "chore"}


def fail(msg):
    print(f"commit bot: {msg}", file=sys.stderr)
    sys.exit(1)


try:
    run = json.load(open(sys.argv[1]))
except (OSError, ValueError, IndexError):
    fail("no JSON from claude")
p = run.get("structured_output")
if run.get("subtype") != "success" or run.get("is_error") or not isinstance(p, dict):
    fail(f"no structured output (subtype={run.get('subtype')})")
if p.get("type") not in TYPES:
    fail(f"bad type {p.get('type')!r}")
scope, subject = p.get("scope") or "", (p.get("subject") or "").strip()
if not re.fullmatch(r"[a-z0-9-]*", scope):
    fail(f"bad scope {scope!r}")
if not subject or len(subject) > 72 or subject.endswith(".") or "\n" in subject:
    fail(f"bad subject {subject!r}")
entry = " ".join((p.get("changelog") or "").split())
if not entry:
    fail("empty changelog entry")

lines = open("CHANGELOG.md").read().splitlines()
if "## Unreleased" not in lines:
    fail("CHANGELOG.md has no '## Unreleased' section")
i = lines.index("## Unreleased")
j = next((k for k in range(i + 1, len(lines)) if lines[k].startswith("## ")), len(lines))
bullets = [l for l in lines[i + 1:j] if l.strip()]
lines[i:j] = ["## Unreleased", "", *bullets, f"- {entry}", ""]
open("CHANGELOG.md", "w").write("\n".join(lines) + "\n")

header = f"{p['type']}({scope}): {subject}" if scope else f"{p['type']}: {subject}"
body = (p.get("body") or "").strip()
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-q", "-m", header] + (["-m", body] if body else []), check=True)
print(header)
EOF
cat > commit_bot.sh <<'EOF'
#!/usr/bin/env bash
# commit_bot.sh - turn the uncommitted changes into a conventional commit plus a changelog entry.
# Exit: 0 committed, or nothing to commit. 1 the agent run or its proposal failed; nothing is committed or left staged.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 1
if [ -z "$(git status --porcelain)" ]; then
  echo "nothing to commit"
  exit 0
fi
git add -A
out=.commitbot/last-run.json
git diff --cached | claude -p "$(cat .commitbot/prompt.txt)" --tools "" --max-turns 3 \
  --output-format json --json-schema "$(cat .commitbot/schema.json)" > "$out" 2>/dev/null
python3 .commitbot/apply.py "$out" || { git reset -q; exit 1; }
EOF
printf '.commitbot/last-run.json\n' > .gitignore
chmod +x commit_bot.sh .commitbot/apply.py
git add .commitbot commit_bot.sh .gitignore && git commit -qm 'chore: add commit bot'   # the bot itself is not the change to describe
./commit_bot.sh; echo "bot exit $?"
git log --format='%h %s%n%b' -1
sed -n '1,8p' CHANGELOG.md
./commit_bot.sh; echo "second run exit $? (clean tree)"
```

</details>

## Check your work

```bash
D=/root/mastery/043-commitbot; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
def rtext(b):
    c = b.get("content")
    return c if isinstance(c, str) else " ".join(x.get("text", "") for x in (c or []) if isinstance(x, dict))
def result_for(rows, pred):
    ids = [u["id"] for u in uses(rows) if pred(u)]
    return [b for b in results(rows) if b.get("tool_use_id") in ids]
def run_rows(p):
    env = load(p) or {}
    return transcript(env.get("session_id") or "none")[1]
PROPOSAL = {'type': 'feat', 'scope': 'greet', 'subject': 'add farewell helper', 'body': 'Adds farewell(name), the counterpart of greet(name), for goodbye messages.', 'changelog': 'Add `farewell(name)` for goodbye messages.'}

import shutil
sc = load(".commitbot/schema.json") or {}
pr = sc.get("properties") or {}
ok(set(sc.get("required") or []) >= {"type", "subject", "changelog"} and sorted((pr.get("type") or {}).get("enum") or []) == sorted(["feat", "fix", "docs", "refactor", "test", "chore"])
   and (pr.get("subject") or {}).get("maxLength") == 72, "the schema pins type to an enum and the subject to 72 characters", "schema.json needs type as an enum of feat/fix/docs/refactor/test/chore and subject maxLength 72")
rc, subj, _ = sh("git log -1 --format=%s")
ok(re.fullmatch(r"(feat|fix|docs|refactor|test|chore)(\([a-z0-9-]+\))?: \S.{0,70}[^.]", subj.strip()), f"HEAD is a conventional commit: {subj.strip()!r}", f"the bot's commit should be type(scope): subject - got {subj.strip()!r}")
rc, files, _ = sh("git show --name-only --format= HEAD")
ok({"src/greet.py", "CHANGELOG.md"} <= set(files.split()), "the commit holds the code change and the changelog entry", f"the commit should include src/greet.py and CHANGELOG.md - it has {files.split()}")
ok(".commitbot/last-run.json" not in files.split(), "the bot's run log is not committed", "git-ignore .commitbot/last-run.json")
log = text("CHANGELOG.md")
unrel = log.split("## Unreleased")[-1].split("\n## ")[0] if "## Unreleased" in log else ""
ok(re.search(r"^- \S", unrel, re.M) and "## 1.0.0" in log, "CHANGELOG.md has the entry under ## Unreleased", "add the changelog entry as a bullet under ## Unreleased")
rows = run_rows(".commitbot/last-run.json")
ok(rows and any("farewell" in p for p in prompts(rows)), "the staged diff reached Claude on stdin", "pipe git diff --cached into claude -p so the diff is part of the prompt")
ok(not uses(rows) or all(u.get("name") == "StructuredOutput" for u in uses(rows)), "the bot run used no tools", "run the bot with --tools \"\" - it needs only the diff")
rc0, head0, _ = sh("git rev-parse HEAD")
rc, out, err = sh("./commit_bot.sh")
rc1, head1, _ = sh("git rev-parse HEAD")
ok(rc == 0 and "nothing to commit" in out and head0 == head1, "on a clean tree the bot exits 0 and commits nothing", f"with nothing to commit the bot should print 'nothing to commit' and exit 0 - rc {rc}")
def clone():
    t = tempfile.mkdtemp()
    subprocess.run(["git", "clone", "-q", ".", t], check=True)
    for k, v in (("user.name", "Checker"), ("user.email", "checker@lab.invalid")):
        subprocess.run(["git", "-C", t, "config", k, v], check=True)
    for f in (".commitbot/apply.py", ".commitbot/schema.json", ".commitbot/prompt.txt"):
        os.makedirs(os.path.join(t, ".commitbot"), exist_ok=True)
        shutil.copy(f, os.path.join(t, f))
    Path(t, "src/greet.py").write_text(text("src/greet.py") + "\n\ndef wave():\n    return 'o/'\n")
    subprocess.run(["git", "-C", t, "add", "-A"], check=True)
    return t
def apply_with(proposal, extra=None):
    t = clone()
    run = {"type": "result", "subtype": "success", "is_error": False, "structured_output": proposal}
    run.update(extra or {})
    Path(t, "run.json").write_text(json.dumps(run))
    before = sh("git rev-parse HEAD", cwd=t)[1]
    rc, out, err = sh([sys.executable, ".commitbot/apply.py", "run.json"], cwd=t)
    after = sh("git rev-parse HEAD", cwd=t)[1]
    return rc, before != after, text(os.path.join(t, "CHANGELOG.md")), sh("git log -1 --format=%s", cwd=t)[1].strip()
bad = {"type": dict(PROPOSAL, type="feature"), "subject with a period": dict(PROPOSAL, subject="add wave."),
       "scope with capitals": dict(PROPOSAL, scope="Greet"), "73-char subject": dict(PROPOSAL, subject="a" * 73), "empty changelog": dict(PROPOSAL, changelog="  ")}
let_through = [k for k, v in bad.items() if (lambda r: r[0] == 0 or r[1])(apply_with(v))]
ok(not let_through, "apply.py rejects every invalid proposal without committing", f"apply.py accepted or committed: {let_through}")
r = apply_with(None, {"subtype": "error_max_turns", "is_error": True})
ok(r[0] != 0 and not r[1], "apply.py rejects a run with no structured output", "a failed run (no structured_output) must exit non-zero and commit nothing")
r = apply_with(dict(PROPOSAL, type="docs", scope="", subject="describe wave", changelog="Document the wave helper."))
ok(r[0] == 0 and r[1] and r[3] == "docs: describe wave" and r[2].split("## 1.0.0")[0].count("- Document the wave helper.") == 1, "a valid empty-scope proposal commits as 'docs: describe wave'", f"a valid proposal with empty scope should commit 'docs: describe wave' - got rc {r[0]}, subject {r[3]!r}")
t = clone()
os.makedirs(os.path.join(t, "bin"))
Path(t, "bin", "claude").write_text("#!/bin/sh\ncat > /dev/null\necho '{\"type\":\"result\",\"subtype\":\"error_max_turns\",\"is_error\":true}'\n")
os.chmod(os.path.join(t, "bin", "claude"), 0o755)
shutil.copy("commit_bot.sh", os.path.join(t, "commit_bot.sh"))
before = sh("git rev-parse HEAD", cwd=t)[1]
rc, out, err = sh("./commit_bot.sh", cwd=t, env={"PATH": os.path.join(t, "bin") + os.pathsep + os.environ["PATH"]})
staged = sh("git diff --cached --name-only", cwd=t)[1].strip()
ok(rc == 1 and sh("git rev-parse HEAD", cwd=t)[1] == before and not staged, "when the agent run fails, the bot exits 1 and leaves nothing staged or committed",
   f"with a failing claude run the bot should exit 1, commit nothing, and unstage - rc {rc}, staged {staged!r}")
PYEOF
```

## What you learned

- An empty diff should cost nothing: check git status before calling the model.
- Pipe the diff in on purpose, remove all tools, and constrain the answer with a schema.
- Validate in code and fail atomically: unstage and exit 1, never commit half a proposal.
