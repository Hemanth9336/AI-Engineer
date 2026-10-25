---
type: task
title: "Audit a repo with two specialists"
minutes: 30
---

## Set up

Set up creates `/root/mastery/056-audit` with:
- `app/`, which contains two hard-coded credentials among safe environment lookups.
- A pinned `requirements.txt`, and `advisories.json`, an offline advisory list.

```bash
rm -rf /root/mastery/056-audit && mkdir -p /root/mastery/056-audit/app /root/mastery/056-audit/reports && cd /root/mastery/056-audit
cat > app/__init__.py <<'EOF'

EOF
cat > app/config.py <<'EOF'
"""App settings. SENTINEL-56: this file is only ever read by the secrets auditor."""
import os

DEBUG = os.environ.get("APP_DEBUG") == "1"
DB_URL = os.environ.get("DB_URL", "sqlite:///app.db")
PAYMENTS_TOKEN = "tok_EXAMPLE_not_real_0000"
TIMEOUT_S = 10
MAILER_PASSWORD = "example-only-password"
EOF
cat > app/search_client.py <<'EOF'
import os

API_KEY = os.environ["SEARCH_API_KEY"]


def headers():
    return {"Authorization": f"Bearer {API_KEY}"}
EOF
cat > requirements.txt <<'EOF'
requests==2.25.1
flask==3.0.3
pyyaml==5.3
rich==13.7.1
EOF
cat > advisories.json <<'EOF'
{
  "requests": {
    "fixed": "2.31.0",
    "id": "ADV-2023-32681"
  },
  "pyyaml": {
    "fixed": "5.4",
    "id": "ADV-2020-14343"
  },
  "jinja2": {
    "fixed": "3.1.4",
    "id": "ADV-2024-34064"
  }
}
EOF
ls -R app
```

## What to build

1. Define two specialists in `.claude/agents/`, both with `tools: Read, Grep, Glob` and `model: haiku`. Each replies with only a JSON array of `{file, line, kind, severity, detail}`.
   - **`secrets-auditor.md`** looks for hard-coded credentials in `app/` and never quotes a value.
   - **`deps-auditor.md`** compares `requirements.txt` against `advisories.json`.
2. Run the audit headless with `--permission-mode acceptEdits` (so the main agent can write the reports), and save `run.json`:
   > Audit this repo with the secrets-auditor and deps-auditor subagents. Do not read the files yourself. Save the secrets-auditor's JSON array as reports/secrets.json and the deps-auditor's as reports/deps.json, exactly as returned.
3. Write `merge.py REPORT.json...`, which prints the merged list:
   - dedupe by `(file, line, kind)`, keeping the first;
   - add `source`, the report's file name without `.json`;
   - sort by severity (critical, high, medium, low, info), then file, then line.
4. Run `./merge.py reports/secrets.json reports/deps.json > AUDIT.json`.

The checker reads each subagent's transcript. It checks that only read-only tools ran and that `app/config.py`'s contents never entered the main conversation.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- The main session's subagents live in `~/.claude/projects/<project>/<session-id>/subagents/`; each `.meta.json` names its `agentType`.
- `sorted(..., key=lambda f: (RANK[f['severity']], f['file'], f['line']))` gives a stable, testable order.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/056-audit
mkdir -p .claude/agents
cat > .claude/agents/secrets-auditor.md <<'EOF'
---
name: secrets-auditor
description: Finds hard-coded credentials in the app/ source tree. Use for the secrets part of an audit.
tools: Read, Grep, Glob
model: haiku
---
Search app/ for hard-coded secrets: variables whose names contain TOKEN, SECRET, PASSWORD, or KEY assigned a string literal.
Values read from os.environ are fine.
Reply with only a JSON array, one object per finding:
[{"file": "app/x.py", "line": 3, "kind": "secret", "severity": "high", "detail": "NAME assigned a string literal"}]
Never include the secret value itself.
EOF
cat > .claude/agents/deps-auditor.md <<'EOF'
---
name: deps-auditor
description: Checks requirements.txt against the offline advisory list in advisories.json. Use for the dependency part of an audit.
tools: Read, Grep, Glob
model: haiku
---
Read requirements.txt and advisories.json. A pinned package is vulnerable when its version is lower than the advisory's "fixed" version.
Reply with only a JSON array, one object per vulnerable package:
[{"file": "requirements.txt", "line": 1, "kind": "dependency", "severity": "medium", "detail": "pkg 1.0 < 1.2 (ADV-ID)"}]
EOF
claude -p 'Audit this repo with the secrets-auditor and deps-auditor subagents. Do not read the files yourself. Save the secrets-auditor's JSON array as reports/secrets.json and the deps-auditor's as reports/deps.json, exactly as returned.' --permission-mode acceptEdits --output-format json < /dev/null > run.json
jq -r .result run.json
cat > merge.py <<'EOF'
#!/usr/bin/env python3
"""merge.py REPORT.json... - merge specialist reports into one sorted, de-duplicated findings list on stdout."""
import json
import sys
from pathlib import Path

RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def merge(paths):
    seen, out = set(), []
    for p in paths:
        source = Path(p).stem
        for f in json.loads(Path(p).read_text()):
            key = (f["file"], f["line"], f["kind"])
            if key in seen:
                continue
            seen.add(key)
            out.append({**f, "source": source})
    return sorted(out, key=lambda f: (RANK.get(f["severity"], 9), f["file"], f["line"]))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: merge.py REPORT.json...")
    print(json.dumps(merge(sys.argv[1:]), indent=2))
EOF
chmod +x merge.py
./merge.py reports/secrets.json reports/deps.json > AUDIT.json
jq -c '.[] | [.severity, .file, .line, .source]' AUDIT.json
```

</details>

## Check your work

```bash
D=/root/mastery/056-audit; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
def subagent_runs(f):
    """(agentType, rows) for each subagent transcript saved beside a main session transcript."""
    out = []
    for m in sorted(glob.glob(os.path.join(f[:-6], "subagents", "*.meta.json"))) if f else []:
        rows = events(m.replace(".meta.json", ".jsonl"))
        out.append(((load(m) or {}).get("agentType"), rows))
    return out
def final_text(rows):
    t = [b.get("text", "") for r in rows if r.get("type") == "assistant" for b in content(r) if b.get("type") == "text"]
    return t[-1] if t else ""
SEC = [{'file': 'app/config.py', 'line': 6, 'kind': 'secret', 'severity': 'high', 'detail': 'PAYMENTS_TOKEN assigned a string literal'}, {'file': 'app/config.py', 'line': 8, 'kind': 'secret', 'severity': 'high', 'detail': 'MAILER_PASSWORD assigned a string literal'}]
DEP = [{'file': 'requirements.txt', 'line': 1, 'kind': 'dependency', 'severity': 'medium', 'detail': 'requests 2.25.1 < 2.31.0 (ADV-2023-32681)'}, {'file': 'requirements.txt', 'line': 3, 'kind': 'dependency', 'severity': 'medium', 'detail': 'pyyaml 5.3 < 5.4 (ADV-2020-14343)'}]

import yaml
def agentdef(p):
    s = text(p)
    if not s.startswith("---\n"):
        return {}
    try:
        return yaml.safe_load(s[4:s.find("\n---", 4)]) or {}
    except Exception:
        return {}
RO = {"Read", "Grep", "Glob"}
for name in ("secrets-auditor", "deps-auditor"):
    a = agentdef(f".claude/agents/{name}.md")
    tools = a.get("tools") or []
    tools = set(re.split(r"[\s,]+", tools.strip())) if isinstance(tools, str) else set(tools)
    ok(a.get("name") == name and a.get("description") and tools and tools <= RO and a.get("model") == "haiku",
       f".claude/agents/{name}.md: read-only tools (Read, Grep, Glob) on haiku", f".claude/agents/{name}.md needs name, description, tools limited to Read/Grep/Glob, and model haiku - got {a}")
env = load("run.json") or {}
f, rows = transcript(env.get("session_id") or "none")
subs = subagent_runs(f)
types = sorted(t for t, _ in subs)
ok(env.get("subtype") == "success" and "secrets-auditor" in types and "deps-auditor" in types, "the run delegated to both specialists", f"the main run should start secrets-auditor and deps-auditor - subagents seen: {types}")
bad = {t: sorted({u.get("name") for u in uses(r)} - RO) for t, r in subs if {u.get("name") for u in uses(r)} - RO}
ok(subs and not bad, "the specialists used only read-only tools", f"subagents used non-read-only tools: {bad}")
main_txt = json.dumps(rows)
sub_txt = json.dumps([r for _, r in subs])
ok("SENTINEL-56" in sub_txt and "SENTINEL-56" not in main_txt, "app/config.py's contents stayed in the auditor's context; the main conversation never saw them",
   "the main agent should not read app/ itself - delegate, and let only the JSON findings come back")
ok("tok_EXAMPLE_not_real_0000" not in text("reports/secrets.json") and "example-only-password" not in text("reports/secrets.json"),
   "the secrets report cites locations without the secret values", "reports must not contain the secret values")
def norm(xs):
    return sorted((x.get("file"), x.get("line"), x.get("kind"), x.get("severity")) for x in xs or [])
ok(norm(load("reports/secrets.json")) == norm(SEC), "reports/secrets.json lists both hard-coded credentials at the right lines", f"reports/secrets.json should flag {[(s['file'], s['line']) for s in SEC]}")
ok(norm(load("reports/deps.json")) == norm(DEP), "reports/deps.json flags requests and pyyaml (and not flask, rich, or the unused jinja2 advisory)", f"reports/deps.json should flag lines 1 and 3")
mg = os.path.abspath("merge.py")
with tempfile.TemporaryDirectory() as t:
    a = [{"file": "b.py", "line": 9, "kind": "secret", "severity": "low", "detail": "x"},
         {"file": "a.py", "line": 2, "kind": "secret", "severity": "high", "detail": "y"},
         {"file": "a.py", "line": 2, "kind": "secret", "severity": "high", "detail": "dup"}]
    b = [{"file": "a.py", "line": 1, "kind": "dependency", "severity": "high", "detail": "z"},
         {"file": "a.py", "line": 2, "kind": "secret", "severity": "high", "detail": "dup from other"}]
    Path(t, "alpha.json").write_text(json.dumps(a))
    Path(t, "beta.json").write_text(json.dumps(b))
    rc, out, err = sh([sys.executable, mg, "alpha.json", "beta.json"], cwd=t)
    try:
        got = json.loads(out)
    except ValueError:
        got = None
want = [("a.py", 1, "dependency", "beta"), ("a.py", 2, "secret", "alpha"), ("b.py", 9, "secret", "alpha")]
ok(rc == 0 and got is not None and [(g["file"], g["line"], g["kind"], g["source"]) for g in got] == want,
   "merge.py dedupes by file, line, and kind, stamps the source, and sorts by severity, file, and line", f"merge.py on hidden reports should give {want} - got {got if got is None else [(g.get('file'), g.get('line'), g.get('kind'), g.get('source')) for g in got]}")
rc, out, err = sh([sys.executable, mg, "reports/secrets.json", "reports/deps.json"])
ok(rc == 0 and json.loads(out or "null") == load("AUDIT.json") and len(load("AUDIT.json") or []) == 4,
   "AUDIT.json is exactly merge.py's output for the two reports (4 findings)", "write AUDIT.json with ./merge.py reports/secrets.json reports/deps.json > AUDIT.json")
PYEOF
```

## What you learned

- Different checks deserve different specialists: separate prompts, read-only tools, and a cheap model each.
- File contents stay in the subagent's context; only its final message - keep it small and structured - reaches the parent.
- Merge reports with code, not prose: dedupe, attribute, and sort deterministically.
