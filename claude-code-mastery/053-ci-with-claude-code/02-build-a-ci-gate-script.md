---
type: task
title: "Build a CI gate script"
minutes: 30
---

## Set up

Set up creates `/root/mastery/053-ci`: `pricing.py`, a passing test suite, and `ci/review-prompt.txt`, the prompt for the review step.

```bash
rm -rf /root/mastery/053-ci && mkdir -p /root/mastery/053-ci/tests /root/mastery/053-ci/ci && cd /root/mastery/053-ci
cat > pricing.py <<'EOF'
def total(items, discount_pct=0):
    """Order total in dollars: sum of price * qty, minus a percentage discount, rounded to cents."""
    if not 0 <= discount_pct <= 100:
        raise ValueError("discount_pct must be between 0 and 100")
    subtotal = sum(i["price"] * i["qty"] for i in items)
    return round(subtotal * (100 - discount_pct) / 100, 2)
EOF
cat > tests/__init__.py <<'EOF'

EOF
cat > tests/test_pricing.py <<'EOF'
import unittest

from pricing import total


class TotalTest(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(total([{"price": 2.5, "qty": 2}, {"price": 1, "qty": 3}]), 8.0)

    def test_discount(self):
        self.assertEqual(total([{"price": 10, "qty": 1}], 15), 8.5)

    def test_bad_discount(self):
        with self.assertRaises(ValueError):
            total([], 120)
EOF
cat > ci/review-prompt.txt <<'EOF'
CI review: read pricing.py and report problems as findings with file, line, severity (info, warning, blocker), and message. Use severity blocker only for bugs or leaked secrets. Set verdict to block if any blocker exists, otherwise pass.
EOF
python3 -m unittest -q
```

## What to build

1. Write `review.schema.json`.
   - Required `verdict` (`pass` or `block`) and `findings`.
   - Each finding has required `file`, `line` (integer), `severity` (`info`, `warning`, or `blocker`), and `message`.
2. Write `ci.sh` and make it executable. Use `set -uo pipefail`, and write `ci-summary.json` (`{tests, review, findings, exit}`) on every path.
   1. Run the tests. If they fail, exit **1** with review `skipped`, and don't call Claude.
   2. Run the review with `claude -p "$(cat ci/review-prompt.txt)"` and these flags: `--tools Read --allowedTools Read --max-turns 6 --json-schema "$(cat review.schema.json)" --output-format json < /dev/null > review.json`.
   3. **Fail closed.** Exit **3** with review `error` if:
      - `claude` exits non-zero, or `is_error` is true;
      - `structured_output` is missing, or the file isn't JSON;
      - the verdict is unknown.
   4. Exit **2** with review `block` if the verdict is `block` **or** any finding is a `blocker`. Otherwise exit **0**.
3. Run `./ci.sh` for real.

The checker swaps in a fake `claude` that crashes, hits max turns, returns prose instead of structured output, prints garbage, or contradicts itself. Each one must produce the right exit code.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `jq -e` exits non-zero when the expression is false or null, which makes it a one-line validity check for the envelope.
- `finish() { ...; exit "$4"; }` keeps the summary and the exit code in one place, so no path forgets either.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/053-ci
cat > review.schema.json <<'EOF'
{
  "type": "object",
  "properties": {
    "verdict": {
      "type": "string",
      "enum": [
        "pass",
        "block"
      ]
    },
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "file": {
            "type": "string"
          },
          "line": {
            "type": "integer"
          },
          "severity": {
            "type": "string",
            "enum": [
              "info",
              "warning",
              "blocker"
            ]
          },
          "message": {
            "type": "string"
          }
        },
        "required": [
          "file",
          "line",
          "severity",
          "message"
        ],
        "additionalProperties": false
      }
    }
  },
  "required": [
    "verdict",
    "findings"
  ],
  "additionalProperties": false
}
EOF
cat > ci.sh <<'EOF'
#!/usr/bin/env bash
# ci.sh - unit tests, then a headless Claude review that gates the build.
# Exit: 0 pass, 1 tests failed, 2 review blocked, 3 review step failed (fail closed).
set -uo pipefail
cd "$(dirname "$0")"

finish() {  # finish <tests> <review> <findings> <exit>
  jq -n --arg tests "$1" --arg review "$2" --argjson findings "$3" --argjson exit "$4" \
    '{tests: $tests, review: $review, findings: $findings, exit: $exit}' > ci-summary.json
  echo "ci: tests=$1 review=$2 findings=$3 exit=$4"
  exit "$4"
}

if ! python3 -m unittest -q; then
  finish fail skipped 0 1
fi

claude -p "$(cat ci/review-prompt.txt)" --tools Read --allowedTools Read --max-turns 6 \
  --json-schema "$(cat review.schema.json)" --output-format json < /dev/null > review.json
rc=$?
if [ "$rc" -ne 0 ] || ! jq -e '.is_error == false and (.structured_output.verdict | type == "string") and (.structured_output.findings | type == "array")' review.json > /dev/null 2>&1; then
  echo "review step failed (exit $rc)" >&2
  finish pass error 0 3
fi

verdict=$(jq -r '.structured_output.verdict' review.json)
findings=$(jq '.structured_output.findings | length' review.json)
blockers=$(jq '[.structured_output.findings[] | select(.severity == "blocker")] | length' review.json)
jq -r '.structured_output.findings[] | "\(.severity)\t\(.file):\(.line)\t\(.message)"' review.json

if [ "$verdict" = "block" ] || [ "$blockers" -gt 0 ]; then
  finish pass block "$findings" 2
elif [ "$verdict" = "pass" ]; then
  finish pass pass "$findings" 0
else
  finish pass error "$findings" 3
fi
EOF
chmod +x ci.sh
./ci.sh
cat ci-summary.json
```

</details>

## Check your work

```bash
D=/root/mastery/053-ci; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
PRICING = 'def total(items, discount_pct=0):\n    """Order total in dollars: sum of price * qty, minus a percentage discount, rounded to cents."""\n    if not 0 <= discount_pct <= 100:\n        raise ValueError("discount_pct must be between 0 and 100")\n    subtotal = sum(i["price"] * i["qty"] for i in items)\n    return round(subtotal * (100 - discount_pct) / 100, 2)'

import shutil, stat
sc = load("review.schema.json") or {}
props = sc.get("properties") or {}
fi = ((props.get("findings") or {}).get("items") or {})
ok(sorted(props.get("verdict", {}).get("enum") or []) == ["block", "pass"] and set(sc.get("required") or []) >= {"verdict", "findings"},
   "review.schema.json: verdict is pass or block, and verdict and findings are required", "review.schema.json needs verdict {enum: [pass, block]} and findings, both required")
ok(sorted((fi.get("properties") or {}).get("severity", {}).get("enum") or []) == ["blocker", "info", "warning"] and set(fi.get("required") or []) >= {"file", "line", "severity", "message"},
   "each finding has file, line, message, and severity info, warning, or blocker", "findings items need required file, line, severity {enum: [info, warning, blocker]}, and message")
rv = load("review.json") or {}
so = rv.get("structured_output") or {}
ok(rv.get("is_error") is False and so.get("verdict") == "pass" and isinstance(so.get("findings"), list),
   "review.json holds a real schema-validated review (structured_output, verdict pass)", f"run ./ci.sh so review.json holds the --json-schema envelope - got {str(rv)[:200]}")
summ = load("ci-summary.json") or {}
ok(summ == {"tests": "pass", "review": "pass", "findings": len(so.get("findings") or []), "exit": 0},
   "ci-summary.json records tests pass, review pass, the finding count, and exit 0", f"ci-summary.json should be {{tests, review, findings, exit}} for the real run - got {summ}")
STUB = '''#!/usr/bin/env bash
printf '%s\n' "$@" > "$STUB_DIR/args.txt"
touch "$STUB_DIR/called"
[ -n "${STUB_OUT:-}" ] && printf '%s' "$STUB_OUT"
exit "${STUB_RC:-0}"
'''
def env_json(**kw):
    base = {"type": "result", "subtype": "success", "is_error": False, "result": "", "session_id": "s", "total_cost_usd": 0.01}
    base.update(kw)
    return json.dumps(base)
F_INFO = {"file": "pricing.py", "line": 6, "severity": "info", "message": "fine"}
F_BLOCK = {"file": "pricing.py", "line": 6, "severity": "blocker", "message": "API key committed"}
def scenario(out, rc=0, break_tests=False):
    with tempfile.TemporaryDirectory() as t:
        shutil.copytree(".", t, dirs_exist_ok=True, ignore=shutil.ignore_patterns("review.json", "ci-summary.json"))
        stub = Path(t, "stub")
        stub.mkdir()
        Path(stub, "claude").write_text(STUB)
        Path(stub, "claude").chmod(0o755)
        if break_tests:
            Path(t, "pricing.py").write_text(PRICING.replace("(100 - discount_pct)", "(100 + discount_pct)"))
        rc2, o, e = sh("./ci.sh", cwd=t, env={"PATH": f"{stub}:" + os.environ["PATH"], "STUB_DIR": str(stub), "STUB_OUT": out, "STUB_RC": str(rc)})
        return rc2, load(Path(t, "ci-summary.json")) or {}, Path(stub, "called").exists(), text(Path(stub, "args.txt"))
rc, s, called, args = scenario(env_json(structured_output={"verdict": "pass", "findings": [F_INFO]}))
ok(rc == 0 and s.get("review") == "pass", "a passing review exits 0", f"stub review verdict pass should exit 0 - rc {rc}, {s}")
need = [a for a in ("--json-schema", "--max-turns", "--output-format") if a not in args]
ok(not need and "--dangerously-skip-permissions" not in args, "ci.sh calls claude with --json-schema, --max-turns, and --output-format json, without skipping permissions",
   f"ci.sh's claude call is missing {need} (or uses --dangerously-skip-permissions)")
rc, s, called, _ = scenario(env_json(structured_output={"verdict": "pass", "findings": []}), break_tests=True)
ok(rc == 1 and s.get("tests") == "fail" and s.get("review") == "skipped" and not called, "failing tests exit 1 and skip the paid review", f"broken tests should exit 1, record review skipped, and never call claude - rc {rc}, called {called}, {s}")
rc, s, _, _ = scenario(env_json(structured_output={"verdict": "block", "findings": [F_BLOCK]}))
ok(rc == 2 and s.get("review") == "block" and s.get("findings") == 1, "a blocking review exits 2", f"verdict block should exit 2 with findings 1 - rc {rc}, {s}")
rc, s, _, _ = scenario(env_json(structured_output={"verdict": "pass", "findings": [F_INFO, F_BLOCK]}))
ok(rc == 2, "a blocker finding blocks even when the verdict says pass", f"recompute from the evidence: any blocker finding should exit 2 - rc {rc}, {s}")
cases = {
    "claude exits 1 after hitting max turns": (env_json(subtype="error_max_turns", is_error=True, errors=["Reached maximum number of turns (6)"]), 1),
    "exit 0 but is_error true": (env_json(is_error=True, subtype="error_during_execution"), 0),
    "no structured_output": (env_json(result="Looks fine to me!"), 0),
    "not JSON at all": ("Error: authentication failed", 0),
    "an unknown verdict": (env_json(structured_output={"verdict": "maybe", "findings": []}), 0),
}
bad = {}
for name, (out, code) in cases.items():
    rc, s, _, _ = scenario(out, code)
    if rc != 3 or s.get("review") != "error":
        bad[name] = (rc, s.get("review"))
ok(not bad, "fail closed: crash, is_error, missing structured_output, garbage, and unknown verdicts all exit 3", f"these review failures should exit 3 with review error: {bad}")
PYEOF
```

## What you learned

- CI reads exit codes: give each outcome its own (tests failed, review blocked, review broken), and write a summary file on every path.
- Fail closed: only a valid structured_output with a known positive verdict passes; crashes, limits, prose, and garbage all fail.
- Bound the step (--max-turns, narrow tools, job timeout), keep stdin closed, and recompute decisions from the findings rather than trusting the verdict alone.
