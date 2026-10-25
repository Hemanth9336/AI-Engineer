---
type: task
title: "Build the retry wrapper"
minutes: 30
---

## Set up

Set up creates `/root/mastery/065-retry` with a buggy `slug.py` and four unit tests in `tests/`.

```bash
rm -rf /root/mastery/065-retry && mkdir -p /root/mastery/065-retry/tests && cd /root/mastery/065-retry
cat > slug.py <<'EOF'
def slugify(text):
    """Make a URL slug: lowercase ASCII letters and digits, words joined by single hyphens."""
    return text.lower().replace(" ", "-")
EOF
cat > tests/test_slugify.py <<'EOF'
import unittest

from slug import slugify


class SlugifyTest(unittest.TestCase):
    def test_spaces(self):
        self.assertEqual(slugify("  Hello World  "), "hello-world")

    def test_punctuation(self):
        self.assertEqual(slugify("Fish & Chips!"), "fish-chips")

    def test_repeated_separators(self):
        self.assertEqual(slugify("a -- b"), "a-b")

    def test_empty(self):
        self.assertEqual(slugify(""), "")


if __name__ == "__main__":
    unittest.main()
EOF
touch tests/__init__.py
jq --version
```

## What to build

1. Write `reliable.sh MAX_ATTEMPTS PROMPT VERIFY_CMD`. The exit codes are 0 when verified, 1 when out of attempts, and 2 for the wrong number of arguments.
   - **Each attempt.** Run `claude -p`:
     - Use `--permission-mode acceptEdits`, allow `Bash(python3 -m unittest*)`, and deny `Edit(tests/**)` and `Write(tests/**)`.
     - Use `--max-turns 8` and `--output-format json`.
     - On attempts 2 and later, add `--resume <session_id>`.
   - **Protect the tests.** Hash `tests/` before the loop. After each attempt, if the hash changed, mark the attempt as tampered and restore the tests from a copy.
   - **Verify.** Run `VERIFY_CMD` yourself after every attempt. An attempt succeeds only when the envelope has `is_error: false`, `claude` exited 0, the tests are untampered, and the verifier passed.
   - **Retry prompt.** Say what failed, and include the last 40 lines of the verifier's output (or the tampering notice).
   - **Log.** Append one row per attempt to `attempts.jsonl`: `attempt`, `session_id`, `agent_ok`, `verify_rc`, `tests_tampered`, and `cost_usd`.
2. Run:

   ```bash
   ./reliable.sh 3 'Fix slugify in slug.py so the tests in tests/ pass.' 'python3 -m unittest discover -s tests -t . -q'
   ```

The checker runs copies of your wrapper against an agent that lies about success, one that rewrites the tests, and one that errors.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Hash each file in a sorted list, then hash that list: `find tests -type f ! -path '*/__pycache__/*' | LC_ALL=C sort | while IFS= read -r f; do shasum -a 256 "$f"; done | shasum -a 256`. Skip `__pycache__`, which running the tests creates.
- Build the arguments as a bash array (`args=(-p "$prompt" ...)`, then `args+=(--resume "$sid")`) so prompts with spaces and newlines survive.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/065-retry
cat > reliable.sh <<'EOF'
#!/usr/bin/env bash
# reliable.sh MAX_ATTEMPTS PROMPT VERIFY_CMD - run an agent task until VERIFY_CMD passes, at most MAX_ATTEMPTS times.
# Every attempt is logged to attempts.jsonl. Exit 0 when verified, 1 when attempts run out, 2 on bad usage.
set -uo pipefail
cd "$(dirname "$0")"
[ $# -eq 3 ] || { echo "usage: reliable.sh MAX_ATTEMPTS PROMPT VERIFY_CMD" >&2; exit 2; }
max=$1 task=$2 verify=$3
mkdir -p work
: > attempts.jsonl
rm -rf work/tests.orig && cp -R tests work/tests.orig
hash_tests() {
  find tests -type f ! -path '*/__pycache__/*' | LC_ALL=C sort | while IFS= read -r f; do shasum -a 256 "$f"; done | shasum -a 256 | cut -d' ' -f1
}
want=$(hash_tests)

sid="" prompt=$task
for attempt in $(seq 1 "$max"); do
  args=(-p "$prompt" --permission-mode acceptEdits --allowedTools "Bash(python3 -m unittest*)"
        --disallowedTools "Edit(tests/**)" "Write(tests/**)" --max-turns 8 --output-format json)
  [ -n "$sid" ] && args+=(--resume "$sid")
  rc=0
  claude "${args[@]}" < /dev/null > "work/attempt-$attempt.json" 2> "work/attempt-$attempt.err" || rc=$?
  agent_ok=false
  jq -e '.is_error == false' "work/attempt-$attempt.json" > /dev/null 2>&1 && [ "$rc" = 0 ] && agent_ok=true
  new_sid=$(jq -r '.session_id // empty' "work/attempt-$attempt.json" 2> /dev/null || true)
  [ -n "$new_sid" ] && sid=$new_sid
  cost=$(jq -r '.total_cost_usd // 0' "work/attempt-$attempt.json" 2> /dev/null || echo 0)

  tampered=false
  if [ "$(hash_tests)" != "$want" ]; then
    tampered=true
    rm -rf tests && cp -R work/tests.orig tests
  fi
  vrc=0
  bash -c "$verify" > "work/verify-$attempt.txt" 2>&1 || vrc=$?

  jq -nc --argjson a "$attempt" --arg s "$sid" --argjson ok "$agent_ok" --argjson v "$vrc" --argjson t "$tampered" --argjson c "${cost:-0}" \
    '{attempt: $a, session_id: $s, agent_ok: $ok, verify_rc: $v, tests_tampered: $t, cost_usd: $c}' >> attempts.jsonl

  if [ "$agent_ok" = true ] && [ "$tampered" = false ] && [ "$vrc" = 0 ]; then
    echo "verified on attempt $attempt"
    exit 0
  fi
  if [ "$tampered" = true ]; then
    prompt="Your last attempt modified files under tests/. They have been restored. Tests are off limits: fix the code, not the tests."
  else
    prompt="Verification failed (exit $vrc). Output of: $verify
$(tail -40 "work/verify-$attempt.txt")
Fix the code so this passes. Do not change tests/."
  fi
done
echo "not verified after $max attempts" >&2
exit 1
EOF
chmod +x reliable.sh
./reliable.sh 3 'Fix slugify in slug.py so the tests in tests/ pass.' 'python3 -m unittest discover -s tests -t . -q'
cat attempts.jsonl
```

</details>

## Check your work

```bash
D=/root/mastery/065-retry; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
def stub(t, body):
    b = Path(t, "bin"); b.mkdir(exist_ok=True)
    p = b / "claude"; p.write_text("#!/usr/bin/env bash\n" + body + "\n"); p.chmod(0o755)
    return {"PATH": f"{b}:{os.environ['PATH']}"}
def envelope(sid, err=False, cost=0.01, turns=2, result="done"):
    return json.dumps({"type": "result", "subtype": "error_during_execution" if err else "success", "is_error": err, "result": result,
                       "session_id": sid, "num_turns": turns, "duration_ms": 1200, "total_cost_usd": cost,
                       "usage": {"input_tokens": 1000, "output_tokens": 50, "cache_read_input_tokens": 200}, "modelUsage": {"lab-fast": {}}})
TEST = 'import unittest\n\nfrom slug import slugify\n\n\nclass SlugifyTest(unittest.TestCase):\n    def test_spaces(self):\n        self.assertEqual(slugify("  Hello World  "), "hello-world")\n\n    def test_punctuation(self):\n        self.assertEqual(slugify("Fish & Chips!"), "fish-chips")\n\n    def test_repeated_separators(self):\n        self.assertEqual(slugify("a -- b"), "a-b")\n\n    def test_empty(self):\n        self.assertEqual(slugify(""), "")\n\n\nif __name__ == "__main__":\n    unittest.main()\n'

import importlib.util, shutil
rows = events("attempts.jsonl")
ok(len(rows) == 2 and rows[0].get("verify_rc") != 0 and rows[1].get("verify_rc") == 0 and rows[0].get("session_id") and rows[0]["session_id"] == rows[1].get("session_id"),
   "attempts.jsonl: attempt 1 failed verification, attempt 2 passed in the same resumed session",
   f"run ./reliable.sh 3 '<task>' '<verify>' and log one row per attempt (attempt, session_id, verify_rc, ...) - got {rows}")
ok(text("tests/test_slugify.py") == TEST, "the tests are unchanged", "the agent must not edit tests/ - restore tests/test_slugify.py")
spec = importlib.util.spec_from_file_location("slug_chk", "slug.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
hidden = {"Rock 'n' Roll": "rock-n-roll", "--x--": "x", "Version 2.0 Notes": "version-2-0-notes", "!!!": ""}
got = {k: m.slugify(k) for k in hidden}
ok(got == hidden, "slug.py now handles hidden inputs too", f"slugify should pass the hidden cases - got {got}")
def copy(t):
    shutil.copy("reliable.sh", t)
    shutil.copytree("tests", Path(t, "tests"))
    Path(t, "slug.py").write_text("def slugify(text):\n    return text\n")
V = "python3 -m unittest discover -s tests -t . -q"
with tempfile.TemporaryDirectory() as t:
    copy(t)
    env = stub(t, f'echo "$*" | tr "\\n" " " >> {t}/args.log; echo >> {t}/args.log; echo \'' + envelope("s-liar", result="Fixed! All tests pass.") + "'")
    rc, so_, se = sh(["./reliable.sh", "3", "fix it", V], cwd=t, env=env, timeout=120)
    r = events(Path(t, "attempts.jsonl"))
    args = text(Path(t, "args.log")).splitlines()
    ok(rc == 1 and len(r) == 3 and all(x.get("verify_rc") != 0 for x in r), "an agent that claims success but changes nothing: 3 failed attempts, exit 1",
       f"verify every attempt yourself and stop after MAX_ATTEMPTS - rc {rc}, {len(r)} rows")
    ok(len(args) == 3 and "--resume" not in args[0] and all("--resume s-liar" in a for a in args[1:]) and "unittest" in args[1] and "Fix" not in args[0],
       "retries resume the same session and carry the verifier's output", f"attempts 2+ should pass --resume <session_id> and include the failing output - args {[a[:80] for a in args]}")
with tempfile.TemporaryDirectory() as t:
    copy(t)
    body = ("printf 'import unittest\\n' > tests/test_slugify.py\n"
            "printf 'import re\\n\\ndef slugify(text):\\n    return re.sub(r\"[^a-z0-9]+\", \"-\", text.lower()).strip(\"-\")\\n' > slug.py\n"
            "echo '" + envelope("s-cheat") + "'")
    rc, so_, se = sh(["./reliable.sh", "2", "fix it", V], cwd=t, env=stub(t, body), timeout=120)
    r = events(Path(t, "attempts.jsonl"))
    ok(rc == 1 and r and r[0].get("tests_tampered") is True and text(Path(t, "tests/test_slugify.py")) == TEST,
       "an attempt that edits tests/ is failed and the tests are restored", f"hash tests/ before and after each attempt - rc {rc}, rows {r[:1]}")
with tempfile.TemporaryDirectory() as t:
    copy(t)
    Path(t, "slug.py").write_text("import re\n\ndef slugify(text):\n    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')\n")
    rc, so_, se = sh(["./reliable.sh", "2", "fix it", V], cwd=t, env=stub(t, "echo '" + envelope("s-err", err=True) + "'; exit 1"), timeout=120)
    r = events(Path(t, "attempts.jsonl"))
    ok(rc == 1 and len(r) == 2 and all(x.get("agent_ok") is False for x in r), "an error envelope is a failed attempt even when the tests happen to pass",
       f"treat is_error or a non-zero exit as a failed attempt - rc {rc}, rows {r}")
    rc, _, _ = sh(["./reliable.sh", "2"], cwd=t)
    ok(rc == 2, "wrong arguments exit 2", f"exit 2 on bad usage - rc {rc}")
PYEOF
```

## What you learned

- Treat every agent run as an attempt and verify it with a command the agent doesn't control.
- Retry in the same session with the failing evidence, and protect the verifier both by permission rules and by hash.
- Bound the loop, count errors as failures, and log each attempt so flaky tasks become visible.
