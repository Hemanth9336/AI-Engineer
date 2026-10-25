---
type: task
title: "Write rules and prove the agent follows them"
minutes: 10
---

## Set up

```bash
mkdir -p /root/harness-lab/36-hooks
cd /root/harness-lab/36-hooks
[ -x run-tests.sh ] && echo 'project found' || echo 'run the previous task first'
```

## What to build

1. Write `/root/harness-lab/36-hooks/CLAUDE.md` (at most 30 lines) for this project. It must include, word for word:
   - `Run tests with ./run-tests.sh --fast` (backticks around the command are fine), and that pytest must never be called directly.
   - `End every answer with the line -- ledger-bot` (again, backticks are fine).
   - Add any other short, specific rules you like - headings and bullets.
2. Run the same task **with** the file and in a copy of the project **without** it:

```bash
cd /root/harness-lab/36-hooks
claude -p "Run the ledger-api tests and report the result" --allowedTools "Bash(./run-tests.sh:*)" --max-turns 4 > answer.txt
cat answer.txt; tail -1 tests.log
rm -rf /tmp/no-rules && mkdir /tmp/no-rules && cp deploy.sh run-tests.sh /tmp/no-rules/
cd /tmp/no-rules
claude -p "Run the ledger-api tests and report the result" --allowedTools "Bash(./run-tests.sh:*)" --max-turns 4 > /root/harness-lab/36-hooks/no-rules.txt
cat /root/harness-lab/36-hooks/no-rules.txt
```

Compare `answer.txt` and `no-rules.txt`, and which test command each run used.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Claude Code finds `CLAUDE.md` in the folder you run it from - the copy in `/tmp/no-rules` has none.
- Without the rule the model reaches for pytest, which `--allowedTools` doesn't permit.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/36-hooks
cat > CLAUDE.md <<'EOF'
# ledger-api

Payments ledger service. Services are configured in services/.

## Commands
- Run tests with `./run-tests.sh --fast`. Never call pytest directly - it skips the database fixtures.
- Deploy only to staging with `./deploy.sh --env staging`; production goes through the release pipeline.

## Answers
- Keep answers to two or three lines.
- End every answer with the line `-- ledger-bot`.

EOF
cd /root/harness-lab/36-hooks
claude -p "Run the ledger-api tests and report the result" --allowedTools "Bash(./run-tests.sh:*)" --max-turns 4 > answer.txt
cat answer.txt; tail -1 tests.log
rm -rf /tmp/no-rules && mkdir /tmp/no-rules && cp deploy.sh run-tests.sh /tmp/no-rules/
cd /tmp/no-rules
claude -p "Run the ledger-api tests and report the result" --allowedTools "Bash(./run-tests.sh:*)" --max-turns 4 > /root/harness-lab/36-hooks/no-rules.txt
cat /root/harness-lab/36-hooks/no-rules.txt
```

</details>

## Check your work

```bash
D=/root/harness-lab/36-hooks; cd $D 2>/dev/null || echo "❌ create $D"
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
md = Path("CLAUDE.md").read_text() if Path("CLAUDE.md").exists() else ""
flat = md.replace("`", "")
ok(md and len(md.splitlines()) <= 30 and "Run tests with ./run-tests.sh --fast" in flat and re.search(r"never .*pytest|pytest.*never", flat, re.I) and "End every answer with the line -- ledger-bot" in flat, "CLAUDE.md is short and has the test-command and sign-off rules", f"CLAUDE.md needs both rules in at most 30 lines - {len(md.splitlines())} lines")
ok("sk-" not in md and "LAB_AI_KEY" not in md, "CLAUDE.md holds no secrets", "CLAUDE.md must not contain keys")
a = Path("answer.txt").read_text().strip() if Path("answer.txt").exists() else ""
b = Path("no-rules.txt").read_text().strip() if Path("no-rules.txt").exists() else ""
ok(a.endswith("-- ledger-bot") and "14 passed" in a, "answer.txt: with the rules, the tests ran and the answer ends with -- ledger-bot", f"answer.txt should end with -- ledger-bot - got {a[-150:]!r}")
ok(b and not b.endswith("-- ledger-bot"), "no-rules.txt: without CLAUDE.md the answer is different", f"no-rules.txt should come from a run without CLAUDE.md - got {b[-150:]!r}")
tl = lambda: Path("tests.log").read_text().splitlines() if Path("tests.log").exists() else []
n = tl().count("run-tests --fast")
rc, ev, err = claude("Run the ledger-api tests and report the result", "--allowedTools", "Bash(./run-tests.sh:*)")
cmds = [c["input"].get("command") for c in calls(ev) if c["name"] == "Bash"]
ok(cmds == ["./run-tests.sh --fast"] and tl().count("run-tests --fast") == n + 1 and (result(ev).get("result") or "").strip().endswith("-- ledger-bot"), "a fresh run in the project follows both rules", f"commands {cmds}, answer {(result(ev).get('result') or '')[-80:]!r}")
d = tempfile.mkdtemp()
for f in ("run-tests.sh", "deploy.sh"):
    if Path(f).exists():
        Path(d, f).write_text(Path(f).read_text())
        os.chmod(Path(d, f), 0o755)
rc, ev2, err = claude("Run the ledger-api tests and report the result", "--allowedTools", "Bash(./run-tests.sh:*)", cwd=d)
cmds2 = [c["input"].get("command") for c in calls(ev2) if c["name"] == "Bash"]
ok(cmds2 and cmds2 != cmds, "the same run without CLAUDE.md behaves differently - the file is what changed it", f"without CLAUDE.md the commands were {cmds2}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- CLAUDE.md is a per-project system prompt the harness loads every session - commit it.
- Good rules are specific, short and checkable: exact commands, concrete conventions.
- Prove a rule works by running the same task with and without it and comparing what the agent did.
