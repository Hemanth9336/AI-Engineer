---
type: task
title: "Build a metrics ledger"
minutes: 23
---

## Set up

Set up creates `/root/mastery/067-ledger` with two issues and a PR description to run small tasks on.

```bash
rm -rf /root/mastery/067-ledger && mkdir -p /root/mastery/067-ledger && cd /root/mastery/067-ledger
cat > issue-1.txt <<'EOF'
Export button does nothing on Firefox 131.
EOF
cat > issue-2.txt <<'EOF'
Could we get a dark theme for the dashboard?
EOF
cat > pr.txt <<'EOF'
PR #212: Replace the hand-written retry loop in the uploader with the shared backoff helper, and add tests for the 429 path.
EOF
jq --version
```

## What to build

1. Run three real tasks. Save each raw envelope (`--tools Read --max-turns 3 --output-format json`) as `runs/<task>/<timestamp>.json`, using `date -u +%Y-%m-%dT%H-%M-%SZ` plus a counter:
   - `label-issues`: Label the issue in issue-1.txt as bug, feature, or question. Reply with the label only.
   - `label-issues`: Label the issue in issue-2.txt as bug, feature, or question. Reply with the label only.
   - `summarize-pr`: Summarize pr.txt for the changelog in one line.
2. Write `ledger.sh [RUNS_DIR]` (default `runs`). It writes `ledger.csv` using jq with `--slurp`.
   - The header is `task,runs,cost_usd,avg_cost_usd,input_tokens,output_tokens,avg_turns`.
   - Write one row per task folder, then a `TOTAL` row.
   - Skip files that aren't a JSON result envelope, naming each one on stderr.
3. Run `./ledger.sh`.

The checker runs a copy of `ledger.sh` on a hidden run folder that includes an empty file and a truncated one.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Tag each file with its task before slurping: `jq -c '{task: (input_filename | split("/") | .[-2]), ...}' files... | jq -rs '...'`.
- A jq function keeps the per-task row and the TOTAL row identical: `def row(name; rs): [...];`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/067-ledger
cat > ledger.sh <<'EOF'
#!/usr/bin/env bash
# ledger.sh [RUNS_DIR] - build ledger.csv (one row per task plus TOTAL) from runs/<task>/*.json; corrupt files are skipped and named on stderr.
set -euo pipefail
cd "$(dirname "$0")"
dir=${1:-runs}
good=()
for f in "$dir"/*/*.json; do
  [ -e "$f" ] || continue
  if jq -e 'type == "object" and .type == "result"' "$f" > /dev/null 2>&1; then good+=("$f"); else echo "skipped: $f" >&2; fi
done
[ ${#good[@]} -gt 0 ] || { echo "no run files in $dir" >&2; exit 1; }

jq -c '{task: (input_filename | split("/") | .[-2]), cost: (.total_cost_usd // 0), turns: (.num_turns // 0),
        input: (.usage.input_tokens // 0), output: (.usage.output_tokens // 0)}' "${good[@]}" \
  | jq -rs '
      def row(name; rs): [name, (rs | length), (rs | map(.cost) | add), ((rs | map(.cost) | add) / (rs | length)),
                          (rs | map(.input) | add), (rs | map(.output) | add), ((rs | map(.turns) | add) / (rs | length))];
      ["task", "runs", "cost_usd", "avg_cost_usd", "input_tokens", "output_tokens", "avg_turns"],
      (group_by(.task)[] | row(.[0].task; .)),
      row("TOTAL"; .)
      | @csv' > ledger.csv
cat ledger.csv
EOF
chmod +x ledger.sh
save() { mkdir -p "runs/$1" && claude -p "$2" --tools Read --max-turns 3 --output-format json < /dev/null > "runs/$1/$(date -u +%Y-%m-%dT%H-%M-%SZ)-$3.json"; }
save label-issues 'Label the issue in issue-1.txt as bug, feature, or question. Reply with the label only.' 1
save label-issues 'Label the issue in issue-2.txt as bug, feature, or question. Reply with the label only.' 2
save summarize-pr 'Summarize pr.txt for the changelog in one line.' 3
./ledger.sh
```

</details>

## Check your work

```bash
D=/root/mastery/067-ledger; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
import csv, io, shutil
files = sorted(glob.glob("runs/*/*.json"))
tasks = sorted({Path(f).parent.name for f in files})
envs = [load(f) or {} for f in files]
ok(len(files) == 3 and tasks == ["label-issues", "summarize-pr"] and all(e.get("type") == "result" and e.get("session_id") for e in envs),
   "runs/ holds three raw envelopes filed by task (label-issues x2, summarize-pr x1)", f"save each run's --output-format json envelope as runs/<task>/<timestamp>.json - found {files}")
ok(len({e.get("session_id") for e in envs}) == 3 and all(re.search(r"\d{4}-\d\d-\d\dT\d\d-\d\d-\d\dZ", Path(f).name) for f in files),
   "three distinct real runs, with sortable colon-free timestamps in the file names", "name files with date -u +%Y-%m-%dT%H-%M-%SZ")
def parse(s):
    return list(csv.reader(io.StringIO(s)))
rows = parse(text("ledger.csv"))
by = {r[0]: r for r in rows[1:] if r}
want_cost = sum(e.get("total_cost_usd") or 0 for e in envs if True)
ok(rows and rows[0] == ["task", "runs", "cost_usd", "avg_cost_usd", "input_tokens", "output_tokens", "avg_turns"] and set(by) == {"label-issues", "summarize-pr", "TOTAL"}
   and by["label-issues"][1] == "2" and by["TOTAL"][1] == "3" and abs(float(by["TOTAL"][2]) - want_cost) < 1e-9,
   "ledger.csv: header, one row per task, and a TOTAL that sums all three envelopes", f"build ledger.csv with jq - got {rows}")
src = text("ledger.sh")
ok(re.search(r"jq\b[^\n]*(-\w*s\w*\b|--slurp)", src) and "python" not in src, "ledger.sh aggregates with jq --slurp", "do the aggregation in jq with -s/--slurp")
def env(cost, turns, i, o):
    return json.dumps({"type": "result", "subtype": "success", "is_error": False, "total_cost_usd": cost, "num_turns": turns,
                       "usage": {"input_tokens": i, "output_tokens": o}, "session_id": "s"})
with tempfile.TemporaryDirectory() as t:
    shutil.copy("ledger.sh", t)
    for task, name, body in [("alpha", "1.json", env(0.25, 2, 100, 10)), ("alpha", "2.json", env(0.75, 4, 300, 30)), ("beta", "1.json", env(0.5, 1, 50, 5)),
                             ("beta", "2.json", ""), ("gamma", "1.json", '{"type": "result", "total_cost_us')]:
        Path(t, "r", task).mkdir(parents=True, exist_ok=True); Path(t, "r", task, name).write_text(body)
    rc, so_, se = sh(["./ledger.sh", "r"], cwd=t)
    rows = parse(text(Path(t, "ledger.csv")))
    by = {r[0]: r for r in rows[1:] if r}
    good = set(by) == {"alpha", "beta", "TOTAL"} and by["alpha"][1] == "2" and float(by["alpha"][2]) == 1.0 and float(by["alpha"][3]) == 0.5 \
        and by["alpha"][4] == "400" and float(by["alpha"][6]) == 3 and by["TOTAL"][1] == "3" and float(by["TOTAL"][2]) == 1.5
    ok(rc == 0 and good, "hidden run folder: per-task sums and averages, and a TOTAL row", f"ledger.sh RUNS_DIR should compute runs, cost_usd, avg_cost_usd, tokens, avg_turns - rc {rc}, rows {rows}")
    ok("beta/2.json" in se and "gamma/1.json" in se, "corrupt and empty files are skipped and named on stderr", f"skip unparsable files and say which - stderr {se.strip()[:200]!r}")
PYEOF
```

## What you learned

- File one raw envelope per run under runs/<task>/; the ledger is a view you can rebuild any time.
- jq -s turns many inputs into one array, which is what totals, group_by, and averages need.
- Skip corrupt run files loudly instead of failing the whole report or hiding them.
