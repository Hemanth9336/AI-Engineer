---
type: task
title: "Plan a change, then execute it"
minutes: 23
---

## Set up

Set up creates `/root/mastery/017-plan/report.py`, a tiny sales report, and `test_report.py`, whose JSON test fails until the flag exists.

```bash
mkdir -p /root/mastery/017-plan && cd /root/mastery/017-plan
cat > report.py <<'EOF'
import sys

SALES = [("north", 1200), ("south", 950), ("east", 700)]


def main(argv):
    for region, total in SALES:
        print(f"{region}: {total}")


if __name__ == "__main__":
    main(sys.argv[1:])
EOF
cat > test_report.py <<'EOF'
import io
import json
import unittest
from contextlib import redirect_stdout

import report


class ReportTest(unittest.TestCase):
    def test_text(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            report.main([])
        self.assertIn("north: 1200", buf.getvalue())

    def test_json(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            report.main(["--json"])
        self.assertEqual(json.loads(buf.getvalue()), {"north": 1200, "south": 950, "east": 700})


if __name__ == "__main__":
    unittest.main()
EOF
```

## What to build

Separate deciding from doing.

1. **Plan** - from `/root/mastery/017-plan`, run headless in plan mode and save the envelope as `plan.json`:
   > Plan how to add a --json flag to report.py that prints the totals as one JSON object. Include Goal, Files, Steps, Verify, and Risks sections.
2. Save the plan's text as `PLAN.md` and read it. Would you approve it?
3. **Execute** - in a new run with edits allowed and only the test command pre-approved, save the envelope as `exec.json`:
   > Implement the plan in PLAN.md exactly. Do not change anything it does not list, then run the verification command.

The checker reads the plan run's transcript to confirm it was in plan mode and edited nothing but its own plan file.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- A plan-mode `-p` run returns the plan as `.result`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/017-plan
sha256sum report.py 2>/dev/null || shasum -a 256 report.py
claude -p "Plan how to add a --json flag to report.py that prints the totals as one JSON object. Include Goal, Files, Steps, Verify, and Risks sections." --permission-mode plan --output-format json > plan.json
jq -r .result plan.json > PLAN.md
claude -p "Implement the plan in PLAN.md exactly. Do not change anything it does not list, then run the verification command." --permission-mode acceptEdits --allowedTools "Bash(python3 -m unittest *)" --output-format json > exec.json
python3 -m unittest -q
```

</details>

## Check your work

```bash
D=/root/mastery/017-plan; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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

pl, ex = load("plan.json") or {}, load("exec.json") or {}
f, rows = transcript(pl.get("session_id") or "none")
modes = {r.get("permissionMode") for r in rows if r.get("permissionMode")}
writes = [u["input"].get("file_path", "") for u in uses(rows) if u.get("name") in ("Edit", "Write", "NotebookEdit")]
ok(pl.get("subtype") == "success" and "plan" in modes and all("/.claude/plans/" in w for w in writes),
   "plan.json is a plan-mode run that changed nothing outside its plan file",
   f"run the planning prompt with --permission-mode plan - modes seen {sorted(m for m in modes if m)}, writes {writes}")
p = text("PLAN.md")
secs = [s for s in ("Goal", "Files", "Steps", "Verify", "Risks") if re.search(rf"(?mi)^#+\s*{s}", p)]
ok(len(secs) == 5 and "report.py" in p and "unittest" in p and p.strip() == (pl.get("result") or "").strip(),
   "PLAN.md is the saved plan, with Goal, Files, Steps, Verify, and Risks",
   f"save the plan run's result as PLAN.md (jq -r .result) - sections found {secs}")
f2, rows2 = transcript(ex.get("session_id") or "none")
touched = {os.path.basename(u["input"].get("file_path", "")) for u in uses(rows2) if u.get("name") in ("Edit", "Write")}
ok(ex.get("session_id") != pl.get("session_id") and any("PLAN.md" in q for q in prompts(rows2)) and touched == {"report.py"},
   "exec.json implemented the plan and touched only report.py", f"execute in a new run that follows PLAN.md - it edited {sorted(touched)}")
rc, out, err = sh("python3 -m unittest -q")
probe = sh("python3 report.py --json")[1].strip()
ok(rc == 0 and json.loads(probe or "null") == {"north": 1200, "south": 950, "east": 700} and "north: 1200" in sh("python3 report.py")[1],
   "the tests pass and both output modes work", "python3 -m unittest should pass and report.py --json should print the totals object")
PYEOF
```

## What you learned

- Plan mode reads and proposes; edits wait for approval.
- The plan is an artifact: save it, review it, and survive compaction with it.
- Execute in a separate run told to follow the plan and nothing else, then verify.
