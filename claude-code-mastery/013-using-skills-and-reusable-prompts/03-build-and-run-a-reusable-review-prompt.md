---
type: task
title: "Build and run a reusable review prompt"
minutes: 23
---

## Set up

Set up creates `/root/mastery/013-review/src/billing.py` and `src/users.py`, each with a few problems a reviewer should catch.

```bash
mkdir -p /root/mastery/013-review/src && cd /root/mastery/013-review
cat > src/billing.py <<'EOF'
"""Billing client."""
API_KEY = "sk_test_fake_013_billing"


def charge(cents):
    """Charge a card."""
    try:
        return {"charged": cents, "key": API_KEY}
    except:
        return None
EOF
cat > src/users.py <<'EOF'
"""User helpers."""


def full_name(first, last):
    print("debug", first, last)
    return f"{first} {last}"


def initials(first, last):
    return first[0] + last[0]
EOF
```

## What to build

Write the review checklist once and run it, unchanged, against two files.

1. Save this prompt as `/root/mastery/013-review/prompts/review.md`:

```text
Review the file named on the last line against this checklist:
R1 No print() debugging left in the code
R2 No bare `except:` clauses
R3 No hard-coded secrets (API keys, passwords, tokens)
R4 Every public function has a docstring

Reply with exactly four lines, one per check, in order:
R<n>: PASS
or
R<n>: FAIL - line <number>: <reason>
```

2. For each of `src/billing.py` and `src/users.py`, run the prompt file headless with `File: src/<name>.py` appended on its own last line. Save the envelope as `reviews/<name>.json` and the answer as `reviews/<name>.txt`.

The checker confirms both runs used the file verbatim and that each review flags the right checks.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `"$(cat prompts/review.md)
 File: src/$f.py"` - put a real newline before `File:` inside the quotes.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/013-review
mkdir -p prompts reviews
cat > prompts/review.md <<'EOF'
Review the file named on the last line against this checklist:
R1 No print() debugging left in the code
R2 No bare `except:` clauses
R3 No hard-coded secrets (API keys, passwords, tokens)
R4 Every public function has a docstring

Reply with exactly four lines, one per check, in order:
R<n>: PASS
or
R<n>: FAIL - line <number>: <reason>
EOF
for f in billing users; do
  claude -p "$(cat prompts/review.md)
File: src/$f.py" --output-format json > reviews/$f.json
  jq -r .result reviews/$f.json > reviews/$f.txt
done
cat reviews/*.txt
```

</details>

## Check your work

```bash
D=/root/mastery/013-review; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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

p = text("prompts/review.md")
ok(all(f"R{i} " in p for i in range(1, 5)) and "except" in p and "docstring" in p and "exactly four lines" in p,
   "prompts/review.md holds the four checks and the output format", "prompts/review.md needs checks R1-R4 and the 'exactly four lines' format")
want = {"billing": {"R2", "R3"}, "users": {"R1", "R4"}}
for name, fails in want.items():
    lines = text(f"reviews/{name}.txt").strip().splitlines()
    shape = len(lines) == 4 and all(re.fullmatch(rf"R{i}: (PASS|FAIL - line \d+: .+)", l) for i, l in enumerate(lines, 1))
    got = {l.split(":")[0] for l in lines if "FAIL" in l}
    ok(shape and got == fails, f"reviews/{name}.txt is four checklist lines failing {sorted(fails)}",
       f"reviews/{name}.txt should be exactly four R-lines failing {sorted(fails)} - got {lines}")
    env = load(f"reviews/{name}.json") or {}
    f, rows = transcript(env.get("session_id") or "none")
    ok(any(p.strip() and p.strip() in q and f"src/{name}.py" in q for q in prompts(rows)),
       f"the {name} run used the saved prompt file verbatim", f"run reviews/{name}.json with the contents of prompts/review.md plus the file name")
PYEOF
```

## What you learned

- A skill loads its full instructions only when needed; only its description sits in context.
- Bundled skills such as /doctor and /code-review come with Claude Code; your own live in .claude/skills/.
- A saved prompt with stable ids and a fixed output format gives consistent, comparable results.
