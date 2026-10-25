---
type: task
title: "Build the PR description generator"
minutes: 30
---

## Set up

Set up creates a git repo at `/root/mastery/045-prdesc` with branch `feature/rate-limit` (three commits). After the branch was cut, `main` got a README change of its own.

```bash
rm -rf /root/mastery/045-prdesc && mkdir -p /root/mastery/045-prdesc/app /root/mastery/045-prdesc/tests && cd /root/mastery/045-prdesc
git init -q -b main && git config user.name 'Lab Learner' && git config user.email learner@lab.invalid
cat > README.md <<'EOF'
# edge

Maintainers: Ana
EOF
cat > app/__init__.py <<'EOF'

EOF
cat > app/server.py <<'EOF'
def handle(request):
    return {"status": 200, "body": "ok"}
EOF
cat > tests/__init__.py <<'EOF'

EOF
git add -A && git commit -qm 'initial'
git switch -q -c feature/rate-limit
cat > app/ratelimit.py <<'EOF'
import time


class TokenBucket:
    """Allow `rate` requests per second with bursts up to `burst`."""

    def __init__(self, rate, burst, clock=time.monotonic):
        self.rate, self.burst, self.clock = rate, burst, clock
        self.tokens, self.last = burst, clock()

    def allow(self):
        now = self.clock()
        self.tokens = min(self.burst, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
EOF
git add -A && git commit -qm 'add token bucket'
cat > app/server.py <<'EOF'
from app.ratelimit import TokenBucket

BUCKET = TokenBucket(rate=5, burst=10)


def handle(request):
    if not BUCKET.allow():
        return {"status": 429, "body": "slow down"}
    return {"status": 200, "body": "ok"}
EOF
git commit -qam 'wire rate limiter into handler'
cat > tests/test_ratelimit.py <<'EOF'
import unittest

from app.ratelimit import TokenBucket


class BucketTest(unittest.TestCase):
    def test_burst_then_refuse(self):
        t = [0.0]
        b = TokenBucket(rate=1, burst=2, clock=lambda: t[0])
        self.assertEqual([b.allow(), b.allow(), b.allow()], [True, True, False])
        t[0] = 1.0
        self.assertTrue(b.allow())
EOF
git add -A && git commit -qm 'test rate limiter'
git switch -q main
cat > README.md <<'EOF'
# edge

Maintainers: Ana, Bo
EOF
git commit -qam 'docs: add Bo as maintainer'
git switch -q feature/rate-limit && git log --oneline --graph --all
```

## What to build

1. `.prdesc/schema.json`: `title` (`maxLength` 70), `summary`, `changes` (an array, `minItems` 1), `risk` (`low` / `medium` / `high`), and `labels` (items from `feature`, `bugfix`, `docs`, `tests`, `breaking`; `minItems` 1). All required.
2. `.prdesc/prompt.txt`:
   > Stdin has this branch's commits and its diff against the base. Write a pull request description: a title of at most 70 characters, a two or three sentence summary of why, one list item per logical change, the risk (low, medium, or high), and labels from the allowed set.
3. `.prdesc/render_pr.py <run.json>`: validate the run (success, a `structured_output`, title of at most 70 characters with no trailing period, a non-empty `changes`, a known `risk`, labels from the set), then write `PR.md` in exactly this layout:

   ```text
   # <title>

   <summary>

   ## Changes

   - <change>

   ## Risk

   <risk>

   **Labels:** <label>, <label>
   ```

   On anything invalid, exit 1 and leave no `PR.md`.
4. `pr_desc.sh [base]` (default `main`):
   - Exit 1 if there are no commits ahead of the base.
   - Otherwise pipe the commit list (`base..HEAD`) and the **three-dot** diff (`base...HEAD`) into `claude -p` with `--tools ""` and the schema, saving `.prdesc/last-run.json`.
   - Then run `render_pr.py`.
5. Compare `git diff --stat main..HEAD` with `main...HEAD`, then run `./pr_desc.sh main`.

The checker confirms main's README change never reached Claude, and feeds `render_pr.py` five invalid descriptions.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Commits: two dots. Diff: three dots.
- Rendering in code is what keeps a made-up label off GitHub.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/045-prdesc
mkdir -p .prdesc
cat > .prdesc/schema.json <<'EOF'
{
  "type": "object",
  "properties": {
    "title": { "type": "string", "minLength": 1, "maxLength": 70 },
    "summary": { "type": "string", "minLength": 1 },
    "changes": { "type": "array", "items": { "type": "string" }, "minItems": 1 },
    "risk": { "type": "string", "enum": ["low", "medium", "high"] },
    "labels": { "type": "array", "items": { "type": "string", "enum": ["feature", "bugfix", "docs", "tests", "breaking"] }, "minItems": 1 }
  },
  "required": ["title", "summary", "changes", "risk", "labels"],
  "additionalProperties": false
}
EOF
cat > .prdesc/prompt.txt <<'EOF'
Stdin has this branch's commits and its diff against the base. Write a pull request description: a title of at most 70 characters, a two or three sentence summary of why, one list item per logical change, the risk (low, medium, or high), and labels from the allowed set.
EOF
cat > .prdesc/render_pr.py <<'EOF'
#!/usr/bin/env python3
"""render_pr.py <run.json> - validate the agent's PR description and write PR.md. Exit 1 (and no PR.md) if anything is invalid."""
import json
import os
import sys

LABELS = {"feature", "bugfix", "docs", "tests", "breaking"}
RISKS = {"low", "medium", "high"}


def fail(msg):
    if os.path.exists("PR.md"):
        os.remove("PR.md")
    print(f"pr description: {msg}", file=sys.stderr)
    sys.exit(1)


try:
    run = json.load(open(sys.argv[1]))
except (OSError, ValueError, IndexError):
    fail("no JSON from claude")
p = run.get("structured_output")
if run.get("subtype") != "success" or run.get("is_error") or not isinstance(p, dict):
    fail("no structured output")
title = (p.get("title") or "").strip()
if not title or len(title) > 70 or title.endswith(".") or "\n" in title:
    fail(f"bad title {title!r}")
changes = p.get("changes")
if not isinstance(changes, list) or not changes or not all(isinstance(c, str) and c.strip() for c in changes):
    fail("changes must be a non-empty list of strings")
if p.get("risk") not in RISKS:
    fail(f"bad risk {p.get('risk')!r}")
labels = p.get("labels")
if not isinstance(labels, list) or not labels or not set(labels) <= LABELS:
    fail(f"labels must come from {sorted(LABELS)}: {labels!r}")
body = [f"# {title}", "", (p.get("summary") or "").strip(), "", "## Changes", ""]
body += [f"- {c.strip()}" for c in changes]
body += ["", "## Risk", "", p["risk"], "", f"**Labels:** {', '.join(labels)}", ""]
open("PR.md", "w").write("\n".join(body))
print(title)
EOF
cat > pr_desc.sh <<'EOF'
#!/usr/bin/env bash
# pr_desc.sh [base] - describe the current branch as a pull request in PR.md. Exit 1 if there is nothing to describe or the description is invalid.
set -uo pipefail
base=${1:-main}
cd "$(git rev-parse --show-toplevel)" || exit 1
if [ -z "$(git log --oneline "$base"..HEAD)" ]; then
  echo "no commits ahead of $base" >&2
  exit 1
fi
out=.prdesc/last-run.json
{ echo "## Commits"; git log --reverse --format='- %s' "$base"..HEAD; echo; echo "## Diff"; git diff "$base"...HEAD; } \
  | claude -p "$(cat .prdesc/prompt.txt)" --tools "" --max-turns 3 --output-format json \
      --json-schema "$(cat .prdesc/schema.json)" > "$out" 2>/dev/null
python3 .prdesc/render_pr.py "$out"
EOF
chmod +x pr_desc.sh .prdesc/render_pr.py
git diff --stat main..HEAD     # two dots: also 'reverts' main's README change
git diff --stat main...HEAD    # three dots: only this branch
./pr_desc.sh main && cat PR.md
```

</details>

## Check your work

```bash
D=/root/mastery/045-prdesc; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
DESC = {'title': 'Add a token-bucket rate limiter to the request handler', 'summary': 'The handler had no protection against bursts. This adds a token bucket and returns 429 when a client exceeds it.', 'changes': ['Add TokenBucket in app/ratelimit.py', 'Return 429 from handle() when the bucket is empty', 'Test burst and refill behavior'], 'risk': 'medium', 'labels': ['feature', 'tests']}

sc = load(".prdesc/schema.json") or {}
pr = sc.get("properties") or {}
ok(sorted((pr.get("risk") or {}).get("enum") or []) == ["high", "low", "medium"] and ((pr.get("labels") or {}).get("items") or {}).get("enum")
   and (pr.get("title") or {}).get("maxLength") == 70, "the schema pins risk, labels, and the title length", "schema.json needs risk enum low/medium/high, labels items enum, and title maxLength 70")
rows = run_rows(".prdesc/last-run.json")
pr_text = " ".join(prompts(rows))
ok("TokenBucket" in pr_text and "wire rate limiter into handler" in pr_text, "the branch's commits and diff reached Claude", "pipe the commit list and the diff into claude -p")
ok(rows and "Ana, Bo" not in pr_text, "the diff is three-dot: main's later README change is not in it", "use git diff main...HEAD - the two-dot diff drags in main's README change")
md = text("PR.md")
ok(re.match(r"# \S.{0,69}\n\n\S", md) and "\n## Changes\n\n- " in md and re.search(r"\n## Risk\n\n(low|medium|high)\n", md) and re.search(r"\*\*Labels:\*\* \w", md),
   "PR.md has the title, summary, Changes, Risk, and Labels", "PR.md should follow the format: # title, summary, ## Changes list, ## Risk, **Labels:**")
def render(desc, extra=None):
    with tempfile.TemporaryDirectory() as t:
        run = {"type": "result", "subtype": "success", "is_error": False, "structured_output": desc}
        run.update(extra or {})
        Path(t, "run.json").write_text(json.dumps(run))
        rc, out, err = sh([sys.executable, os.path.abspath(".prdesc/render_pr.py"), "run.json"], cwd=t)
        return rc, text(os.path.join(t, "PR.md"))
bad = {"made-up label": dict(DESC, labels=["feature", "urgent"]), "risk": dict(DESC, risk="extreme"), "long title": dict(DESC, title="x" * 71),
       "no changes": dict(DESC, changes=[]), "title with period": dict(DESC, title="Add a limiter.")}
passed = [k for k, v in bad.items() if (lambda r: r[0] == 0 or r[1])(render(v))]
ok(not passed, "render_pr.py rejects every invalid description and writes no PR.md", f"render_pr.py accepted: {passed}")
rc, body = render(None, {"subtype": "error_max_turns", "is_error": True})
ok(rc != 0 and not body, "render_pr.py rejects a run with no structured output", "a failed run must exit non-zero and write no PR.md")
rc, body = render(DESC)
want = "# Add a token-bucket rate limiter to the request handler\n\n" + DESC["summary"] + "\n\n## Changes\n\n" + "\n".join("- " + c for c in DESC["changes"]) + "\n\n## Risk\n\nmedium\n\n**Labels:** feature, tests\n"
ok(rc == 0 and body == want, "a valid description renders exactly in the agreed format", f"render_pr.py output differs from the format:\n{body[:300]}")
rc, out, err = sh("./pr_desc.sh feature/rate-limit")
ok(rc == 1, "with no commits ahead of the base, pr_desc.sh exits 1 without calling Claude", f"./pr_desc.sh feature/rate-limit should exit 1 (nothing to describe) - rc {rc}")
PYEOF
```

## What you learned

- git log base..HEAD lists the branch's commits; git diff base...HEAD shows only the branch's changes.
- Constrain the description with a schema and render it with code, so every PR has the same shape.
- Labels and risk come from fixed sets that your code enforces.
