---
type: task
title: "Review a seeded diff"
minutes: 23
---

## Set up

Set up creates `/root/mastery/074-review` with `changes.diff`, a diff with three seeded issues among ordinary changes, and `expected.json`, the answer key a senior reviewer wrote.

```bash
rm -rf /root/mastery/074-review && mkdir -p /root/mastery/074-review && cd /root/mastery/074-review
cat > changes.diff <<'EOF'
diff --git a/shop/orders.py b/shop/orders.py
--- a/shop/orders.py
+++ b/shop/orders.py
@@ -8,10 +8,18 @@ from shop.db import connect
 def order_count(customer):
     return len(find_orders(customer))


-def find_orders(customer):
-    return connect().execute("SELECT * FROM orders WHERE customer = ?", (customer,)).fetchall()
+def find_orders(customer):
+    cur = connect().cursor()
+    cur.execute(f"SELECT * FROM orders WHERE customer = '{customer}'")
+    return cur.fetchall()
+
+
+def cancel(order_id):
+    try:
+        connect().execute("UPDATE orders SET status = 'cancelled' WHERE id = ?", (order_id,))
+    except Exception:
+        pass


 def label(order):
diff --git a/shop/config.py b/shop/config.py
--- a/shop/config.py
+++ b/shop/config.py
@@ -1,3 +1,3 @@
 APP_NAME = "shop"
-DEBUG = False
+DEBUG = True
 PAGE_SIZE = 50
diff --git a/tests/test_orders.py b/tests/test_orders.py
--- a/tests/test_orders.py
+++ b/tests/test_orders.py
@@ -20,3 +20,8 @@ class OrdersTest(unittest.TestCase):
     def test_count(self):
         self.assertEqual(order_count("ann"), 2)
+
+    def test_cancel(self):
+        cancel(1)
+        self.assertEqual(find_orders("ann")[0][2], "cancelled")
EOF
cat > expected.json <<'EOF'
{
  "verdict": "request_changes",
  "findings": [
    {
      "file": "shop/orders.py",
      "line": 14,
      "rule": "SEC-SQL",
      "severity": "blocker"
    },
    {
      "file": "shop/orders.py",
      "line": 21,
      "rule": "ERR-SWALLOW",
      "severity": "major"
    },
    {
      "file": "shop/config.py",
      "line": 2,
      "rule": "CFG-DEBUG",
      "severity": "minor"
    }
  ]
}
EOF
jq --version
```

## What to build

1. Write the skill `.claude/skills/review-checklist/SKILL.md`.
   - Frontmatter: `name: review-checklist`, a `description`, `argument-hint: DIFF_FILE`, and `disable-model-invocation: true`.
   - Body: review the diff in `$ARGUMENTS`. Cite the file and the new line number for each finding.
   - Checklist:
     - `SEC-SQL`: blocker.
     - `ERR-SWALLOW`: major.
     - `CFG-DEBUG`: minor.
     - `TEST-MISSING`: major.
   - Verdict rule: `request_changes` if any finding is a blocker or major, otherwise `approve`.
2. Write `verdict.schema.json` with `verdict`, plus `findings[]` (`file`, `line`, `rule`, `severity`, and an optional `note`).
3. Run `claude -p '/review-checklist changes.diff'` with `--tools Read`, `--json-schema` and `--output-format json`.
   - Save the envelope as `review-run.json`.
   - Save its `.structured_output` as `review.json`.
4. Write `grade.py REVIEW_JSON EXPECTED_JSON`. It writes `grade.json` and exits 0 only on a pass.
   - Match a finding by file and rule, with a line within ±1. Each finding matches at most one key entry.
   - Report `tp`, `fp`, `fn`, `precision` and `recall` (rounded to 3 places), plus `missed`, `verdict_expected`, `verdict_got` and `pass`.
   - `pass` means nothing was missed and the verdict matches.
5. Run `python3 grade.py review.json expected.json`.

The checker grades hidden reviews: one with off-by-one lines, one that misses an issue, and one with duplicate findings.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Slash skills work headless: `claude -p '/review-checklist changes.diff'` expands the skill with `$ARGUMENTS` set to `changes.diff`.
- Mark key entries as used while matching, so one finding can't satisfy two seeded issues.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/074-review
mkdir -p .claude/skills/review-checklist
cat > .claude/skills/review-checklist/SKILL.md <<'EOF'
---
name: review-checklist
description: Review a diff file against the team checklist and return a verdict.
argument-hint: DIFF_FILE
disable-model-invocation: true
---
Review the unified diff in $ARGUMENTS against this checklist. Report only issues on added lines, citing the file path
(without a/ or b/) and the line number in the new file.

| Rule | Look for | Severity |
|---|---|---|
| SEC-SQL | SQL built with f-strings, %, +, or .format instead of parameters | blocker |
| ERR-SWALLOW | except blocks that pass, or otherwise hide the error | major |
| CFG-DEBUG | Debug or insecure settings switched on | minor |
| TEST-MISSING | Behaviour changed with no test change in the diff | major |

Verdict: request_changes if any finding is blocker or major; otherwise approve.
Return every finding with file, line, rule, severity, and a one-line note.
EOF
cat > verdict.schema.json <<'EOF'
{
  "type": "object",
  "required": [
    "verdict",
    "findings"
  ],
  "additionalProperties": false,
  "properties": {
    "verdict": {
      "enum": [
        "approve",
        "request_changes"
      ]
    },
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "file",
          "line",
          "rule",
          "severity"
        ],
        "properties": {
          "file": {
            "type": "string"
          },
          "line": {
            "type": "integer"
          },
          "rule": {
            "enum": [
              "SEC-SQL",
              "ERR-SWALLOW",
              "CFG-DEBUG",
              "TEST-MISSING"
            ]
          },
          "severity": {
            "enum": [
              "blocker",
              "major",
              "minor"
            ]
          },
          "note": {
            "type": "string"
          }
        }
      }
    }
  }
}
EOF
cat > grade.py <<'EOF'
#!/usr/bin/env python3
"""grade.py REVIEW_JSON EXPECTED_JSON - score a review against an answer key and write grade.json."""
import json
import sys
from pathlib import Path

review = json.loads(Path(sys.argv[1]).read_text())
key = json.loads(Path(sys.argv[2]).read_text())
found = list(review.get("findings") or [])
expected = list(key.get("findings") or [])


def same(f, e):
    return f.get("file") == e["file"] and f.get("rule") == e["rule"] and abs(int(f.get("line", -99)) - e["line"]) <= 1


matched, used = [], set()
for e in expected:
    hit = next((i for i, f in enumerate(found) if i not in used and same(f, e)), None)
    if hit is not None:
        used.add(hit)
        matched.append(e)
tp = len(matched)
fp = len(found) - len(used)
fn = len(expected) - tp
grade = {
    "tp": tp, "fp": fp, "fn": fn,
    "precision": round(tp / len(found), 3) if found else (1.0 if not expected else 0.0),
    "recall": round(tp / len(expected), 3) if expected else 1.0,
    "missed": [e for e in expected if e not in matched],
    "verdict_expected": key.get("verdict"), "verdict_got": review.get("verdict"),
}
grade["pass"] = fn == 0 and grade["verdict_expected"] == grade["verdict_got"]
Path("grade.json").write_text(json.dumps(grade, indent=2) + "\n")
print(json.dumps(grade, indent=2))
sys.exit(0 if grade["pass"] else 1)
EOF
chmod +x grade.py
claude -p '/review-checklist changes.diff' --tools Read --json-schema "$(cat verdict.schema.json)" --output-format json < /dev/null > review-run.json
jq '.structured_output' review-run.json > review.json
python3 grade.py review.json expected.json
```

</details>

## Check your work

```bash
D=/root/mastery/074-review; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
sk = text(".claude/skills/review-checklist/SKILL.md")
fm = sk.split("---")[1] if sk.startswith("---") else ""
ok(re.search(r"^name:\s*review-checklist\s*$", fm, re.M) and "disable-model-invocation: true" in fm and "$ARGUMENTS" in sk
   and all(r in sk for r in ["SEC-SQL", "ERR-SWALLOW", "CFG-DEBUG", "TEST-MISSING"]),
   "the review-checklist skill has its frontmatter, takes $ARGUMENTS, and lists the four rule ids", "write .claude/skills/review-checklist/SKILL.md as described")
run = load("review-run.json") or {}
rv = load("review.json") or {}
ok(run.get("subtype") == "success" and run.get("structured_output") == rv and rv.get("verdict") in ("approve", "request_changes"),
   "review.json is the schema-validated structured_output of the run", "run claude -p '/review-checklist changes.diff' with --json-schema and save .structured_output as review.json")
def expanded(r):
    s = json.dumps((r.get("message") or {}).get("content")) if r.get("type") == "user" and isinstance(r.get("message"), dict) else ""
    return "Base directory for this skill" in s and "review-checklist" in s and "SEC-SQL" in s and "changes.diff" in s
ok(any(expanded(r) for rows in sessions(".") for r in rows), "the run expanded your skill with changes.diff as its argument", "invoke the skill as /review-checklist changes.diff")
gr = load("grade.json") or {}
ok(gr.get("pass") is True and gr.get("fn") == 0 and gr.get("verdict_got") == "request_changes",
   "grade.json: every seeded issue found and the verdict is request_changes", f"python3 grade.py review.json expected.json - got {gr}")
KEY = {"verdict": "request_changes", "findings": [{"file": "a.py", "line": 10, "rule": "SEC-SQL", "severity": "blocker"},
                                                  {"file": "a.py", "line": 30, "rule": "ERR-SWALLOW", "severity": "major"}]}
def trial(review):
    with tempfile.TemporaryDirectory() as t:
        shutil.copy("grade.py", t)
        Path(t, "r.json").write_text(json.dumps(review)); Path(t, "k.json").write_text(json.dumps(KEY))
        rc, so_, se = sh([sys.executable, "grade.py", "r.json", "k.json"], cwd=t)
        return rc, load(Path(t, "grade.json")) or {}
rc, g = trial({"verdict": "request_changes", "findings": [{"file": "a.py", "line": 11, "rule": "SEC-SQL"}, {"file": "a.py", "line": 29, "rule": "ERR-SWALLOW"},
                                                          {"file": "b.py", "line": 1, "rule": "CFG-DEBUG"}]})
ok(rc == 0 and g.get("tp") == 2 and g.get("fp") == 1 and g.get("precision") == 0.667 and g.get("recall") == 1.0 and g.get("pass") is True,
   "hidden review with lines off by one and an extra finding: 2 matched, 1 false positive, still a pass", f"match by file, rule, and line within 1 - got rc {rc}, {g}")
rc, g = trial({"verdict": "approve", "findings": [{"file": "a.py", "line": 10, "rule": "SEC-SQL"}]})
ok(rc == 1 and g.get("fn") == 1 and g.get("pass") is False and len(g.get("missed") or []) == 1,
   "a review that misses one issue and approves fails the grade (exit 1)", f"missed issues or a wrong verdict should fail - got rc {rc}, {g}")
rc, g = trial({"verdict": "request_changes", "findings": [{"file": "a.py", "line": 10, "rule": "SEC-SQL"}, {"file": "a.py", "line": 10, "rule": "SEC-SQL"}]})
ok(g.get("tp") == 1 and g.get("fp") == 1 and g.get("fn") == 1, "one finding can't match two seeded issues, and duplicates count as false positives", f"use each finding at most once - got {g}")
PYEOF
```

## What you learned

- /code-review with an effort level is the fast first pass; managed Code Review never approves or blocks, so humans still own the merge.
- A checklist skill with rule ids and severities plus a verdict schema makes reviews consistent and machine-readable.
- Grade the reviewer against seeded diffs (recall, precision, verdict) before trusting it in a pipeline.
