---
type: task
title: "Write a skill for a repeated workflow"
minutes: 12
---

## Set up

`/root/harness-lab/37-skills/changes/` holds one change list per version (`v2.3.txt`, `v2.4.txt`). The team writes release notes from them by hand every sprint.

```bash
mkdir -p /root/harness-lab/37-skills/changes /root/harness-lab/37-skills/runs
cd /root/harness-lab/37-skills
cat > changes/v2.3.txt <<'EOF'
feat: export ledgers as CSV
fix: timezone in monthly statements
fix: duplicate webhook retries
EOF
cat > changes/v2.4.txt <<'EOF'
feat: multi-currency ledgers
feat: refund reasons in the API
fix: rounding on partial refunds
EOF
claude --version
```

## What to build

1. Write `/root/harness-lab/37-skills/.claude/skills/release-notes/SKILL.md`:
   - Frontmatter `name: release-notes` and a `description` that starts with `Draft release notes` and says when to use it (include `Use when`).
   - Steps that read the change list with `cat changes/<version>.txt` (write it exactly like that), say what to do if it's missing, and sort `feat:` / `fix:` lines.
   - An output template with `## ledger-api <version>`, `### Features` and `### Fixes`.
2. Run it and save the notes:

```bash
cd /root/harness-lab/37-skills
claude -p "Draft the ledger-api v2.4 release notes" --allowedTools Skill "Bash(cat:*)" \
  --max-turns 6 --output-format stream-json --verbose > runs/v2.4.jsonl
jq -r 'select(.type == "result") | .result' runs/v2.4.jsonl > RELEASE_NOTES.md
cat RELEASE_NOTES.md
```

Check `runs/v2.4.jsonl`: the model called the `Skill` tool first, and only then ran `cat`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- The frontmatter sits between two `---` lines at the very top of the file.
- The model only sees the description until it calls the skill - make that line specific.

</details>

<details><summary>Solution</summary>

```bash
mkdir -p /root/harness-lab/37-skills/.claude/skills/release-notes
cat > /root/harness-lab/37-skills/.claude/skills/release-notes/SKILL.md <<'SKILLEOF'
---
name: release-notes
description: Draft release notes for a ledger-api version from its change list. Use when asked for release notes, a changelog, or "what's new" for a version.
---

# Release notes for ledger-api

1. Find the version in the request (like v2.4).
2. Read its change list: run `cat changes/<version>.txt`. If the file is missing, say so and stop - never invent changes.
3. Sort the lines: `feat:` lines go under Features, `fix:` lines under Fixes. Drop the prefixes and capitalize.
4. Reply with exactly this format and nothing else:

~~~
## ledger-api <version>
### Features
- ...
### Fixes
- ...
~~~

SKILLEOF
cd /root/harness-lab/37-skills
claude -p "Draft the ledger-api v2.4 release notes" --allowedTools Skill "Bash(cat:*)" \
  --max-turns 6 --output-format stream-json --verbose > runs/v2.4.jsonl
jq -r 'select(.type == "result") | .result' runs/v2.4.jsonl > RELEASE_NOTES.md
cat RELEASE_NOTES.md
```

</details>

## Check your work

```bash
D=/root/harness-lab/37-skills; cd $D 2>/dev/null || echo "❌ create $D"
python - <<'PYEOF'
import json, math, os, subprocess, sys
from pathlib import Path
from openai import OpenAI
_C = OpenAI()
sys.excepthook = lambda t, e, tb: print(f"❌ check stopped: {t.__name__}: {e}")
def E(xs):
    return [d.embedding for d in _C.embeddings.create(model="lab-embed", input=xs).data]
def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))
def ok(cond, good, bad):
    print(("✅ " + good) if cond else ("❌ " + bad))
def load(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None
def run(*args, cwd=None):
    r = subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=cwd)
    return r.returncode, r.stdout.strip(), r.stderr.strip()
sys.path.insert(0, '/opt/harness')
from labmock import MockModel
import tempfile
def claude(prompt, *flags, cwd="."):
    cmd = ["claude", "-p", prompt, *flags, "--max-turns", "6", "--output-format", "stream-json", "--verbose"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=240, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return 124, [], "timed out"
    ev = []
    for line in r.stdout.splitlines():
        try:
            ev.append(json.loads(line))
        except ValueError:
            pass
    return r.returncode, ev, r.stderr
def events(path):
    try:
        return [json.loads(l) for l in open(path) if l.strip()]
    except Exception:
        return []
def blocks(e):
    c = (e.get("message") or {}).get("content")
    return c if isinstance(c, list) else []
def calls(ev):
    return [b for e in ev if e.get("type") == "assistant" for b in blocks(e) if b.get("type") == "tool_use"]
def result(ev):
    return next((e for e in ev if e.get("type") == "result"), {})
def init(ev):
    return next((e for e in ev if e.get("type") == "system" and e.get("subtype") == "init"), {})
def gw_claude(tool):
    rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")]
    return any(str(x.get("client", "")).startswith("claude-cli") and tool in (x.get("tool_calls") or []) for x in rows)

import re
p = Path(".claude/skills/release-notes/SKILL.md")
text = p.read_text() if p.exists() else ""
m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
meta = dict(l.split(":", 1) for l in m.group(1).splitlines() if ":" in l) if m else {}
meta = {k.strip(): v.strip() for k, v in meta.items()}
body = m.group(2) if m else ""
ok(meta.get("name") == "release-notes" and meta.get("description", "").startswith("Draft release notes") and "Use when" in meta.get("description", ""), "SKILL.md frontmatter: name release-notes and a what + when description", f"frontmatter should have name: release-notes and a description starting 'Draft release notes' with 'Use when' - got {meta}")
ok("cat changes/<version>.txt" in body and all(h in body for h in ("## ledger-api <version>", "### Features", "### Fixes")) and re.search(r"missing|not found|doesn't exist|does not exist", body, re.I), "the steps read the change list, handle a missing file, and give an exact template", "the body needs `cat changes/<version>.txt`, a missing-file rule and the ## / ### template")
ev = events("runs/v2.4.jsonl")
names = [c["name"] for c in calls(ev)]
ok(names[:2] == ["Skill", "Bash"] and calls(ev)[0]["input"].get("skill") == "release-notes", "runs/v2.4.jsonl: the model loaded the skill, then followed its steps", f"expected Skill then Bash - got {names}")
notes = Path("RELEASE_NOTES.md").read_text() if Path("RELEASE_NOTES.md").exists() else ""
ok(notes.startswith("## ledger-api v2.4") and "Multi-currency ledgers" in notes and "Rounding on partial refunds" in notes, "RELEASE_NOTES.md holds the v2.4 notes in the template", f"RELEASE_NOTES.md - got {notes[:150]!r}")
rc, ev, err = claude("Draft the ledger-api v2.3 release notes", "--allowedTools", "Skill", "Bash(cat:*)")
cs = calls(ev)
out = result(ev).get("result") or ""
ok([c["name"] for c in cs] == ["Skill", "Bash"] and cs[1]["input"].get("command") == "cat changes/v2.3.txt" and out.startswith("## ledger-api v2.3") and "Export ledgers as CSV" in out, "a fresh v2.3 request loads the skill, reads changes/v2.3.txt and answers in the template", f"calls {[(c['name'], c['input']) for c in cs]}, answer {out[:120]!r} {err[-150:]}")
ok("release-notes" in (init(ev).get("skills") or []), "Claude Code lists release-notes among the project's skills", f"skills in the init event: {init(ev).get('skills')}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A skill is a SKILL.md with a name, a what-and-when description, and the full steps.
- Only the description is in context until the model calls the skill - write it with the words users say.
- Give skills exact steps, a missing-input rule and an output template, so every run looks the same.
