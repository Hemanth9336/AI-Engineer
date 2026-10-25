---
type: challenge
title: "Build an audited headless pipeline"
minutes: 36
---

## Set up

Set up creates `/root/mastery/036-pipeline` with a `CHANGES.txt` listing versions 2.4.0 and 2.3.1.

```bash
rm -rf /root/mastery/036-pipeline && mkdir -p /root/mastery/036-pipeline/.claude/hooks && cd /root/mastery/036-pipeline
cat > CHANGES.txt <<'EOF'
## 2.4.0
- Added CSV export for invoices
- Faster search on large accounts
- BREAKING: removed the v1 /legacy/invoices endpoint

## 2.3.1
- Fixed rounding in tax totals
EOF
```

## What to build

Build the release-notes pipeline your team will run on every tag. The agent reads and proposes; your script decides and writes.

**Requirements**

1. **Boundaries** - `/root/mastery/036-pipeline/.claude/settings.json` denies `Bash`, `Edit`, `WebFetch`, and `WebSearch`.
2. **Audit** - a PostToolUse hook with matcher `*` appends `{"session", "tool", "tool_use_id"}` per call to `.claude/audit.jsonl`.
3. **Contract** - `notes.schema.json`: `version` (string, `X.Y.Z`), `highlights` (array of strings, at least one), `breaking` (boolean); all required, nothing else.
4. **Run** - `pipeline.sh` runs this headless with only Read, at most 4 turns, `stream-json --verbose`, and the schema, saving the stream to `runs/<timestamp>.jsonl`:
   > Read CHANGES.txt and return the release notes for the newest version: its version number, the user-facing highlights (one short sentence each), and whether it has breaking changes.
5. **Gate and render** - fail closed on a missing result, a failed run, or structured output that breaks the contract: append `FAIL <reason> session=<id>` to `runs/pipeline.log`, exit `1`, and **do not touch** `RELEASE.md`. On success, your code (not the agent) writes `RELEASE.md` - `# Release <version>`, a blank line, the line `**Breaking changes** - read before upgrading.` and a blank line when `breaking` is true, then one `- <highlight>` per line - appends `OK <version> session=<id>`, and exits `0`.

The checker runs the pipeline on the real `CHANGES.txt`, then on a malformed one, and checks the files, the log, the stream, and the audit trail.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Write RELEASE.md from structured_output in the script - the agent has no Edit or Bash anyway.
- Keep the previous RELEASE.md on failure: only write it after every check passes.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/036-pipeline
cat > notes.schema.json <<'EOF'
{
  "type": "object",
  "properties": {
    "version": { "type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$" },
    "highlights": { "type": "array", "items": { "type": "string" }, "minItems": 1 },
    "breaking": { "type": "boolean" }
  },
  "required": ["version", "highlights", "breaking"],
  "additionalProperties": false
}
EOF
cat > .claude/hooks/audit.py <<'EOF'
#!/usr/bin/env python3
"""PostToolUse on every tool: one JSON line per call in .claude/audit.jsonl."""
import json, os, sys

ev = json.load(sys.stdin)
with open(os.path.join(os.environ.get("CLAUDE_PROJECT_DIR", "."), ".claude", "audit.jsonl"), "a") as f:
    f.write(json.dumps({"session": ev.get("session_id"), "tool": ev.get("tool_name"), "tool_use_id": ev.get("tool_use_id")}) + "\n")
EOF
cat > .claude/settings.json <<'EOF'
{
  "permissions": {
    "deny": ["Bash", "Edit", "WebFetch", "WebSearch"]
  },
  "hooks": {
    "PostToolUse": [
      { "matcher": "*", "hooks": [ { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/audit.py\"", "timeout": 10 } ] }
    ]
  }
}
EOF
cat > pipeline.sh <<'EOF'
#!/usr/bin/env bash
# pipeline.sh - release notes from CHANGES.txt. Exit 0: RELEASE.md written. Exit 1: gate failed, RELEASE.md untouched.
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p runs
stream=runs/$(date +%Y%m%dT%H%M%S)-$$.jsonl
claude -p "Read CHANGES.txt and return the release notes for the newest version: its version number, the user-facing highlights (one short sentence each), and whether it has breaking changes." \
  --allowedTools Read --max-turns 4 \
  --output-format stream-json --verbose --json-schema "$(cat notes.schema.json)" < /dev/null > "$stream" 2>/dev/null
python3 - "$stream" <<'PY'
import json, re, sys
stream = sys.argv[1]
def log(line):
    open("runs/pipeline.log", "a").write(line + "\n")
try:
    events = [json.loads(l) for l in open(stream) if l.strip()]
except ValueError as e:
    log(f"FAIL unreadable-stream {stream}"); sys.exit(1)
res = [e for e in events if e.get("type") == "result"]
r = res[-1] if res else {}
sid = r.get("session_id", "-")
out = r.get("structured_output")
ok = (r.get("subtype") == "success" and not r.get("is_error") and isinstance(out, dict)
      and set(out) == {"version", "highlights", "breaking"}
      and isinstance(out["version"], str) and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", out["version"])
      and isinstance(out["highlights"], list) and out["highlights"] and all(isinstance(h, str) and h.strip() for h in out["highlights"])
      and isinstance(out["breaking"], bool))
if not ok:
    reason = "no-result" if not res else (r.get("subtype") if r.get("subtype") != "success" else "bad-structured-output")
    log(f"FAIL {reason} session={sid}"); sys.exit(1)
body = f"# Release {out['version']}\n\n"
if out["breaking"]:
    body += "**Breaking changes** - read before upgrading.\n\n"
body += "\n".join(f"- {h.strip()}" for h in out["highlights"]) + "\n"
open("RELEASE.md", "w").write(body)
log(f"OK {out['version']} session={sid}")
PY
EOF
chmod +x pipeline.sh .claude/hooks/audit.py
./pipeline.sh; echo "pipeline exit $?"
cat RELEASE.md runs/pipeline.log
```

</details>

## Check your work

```bash
D=/root/mastery/036-pipeline; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
WANT = "# Release 2.4.0\n\n**Breaking changes** - read before upgrading.\n\n- Invoices can be exported as CSV.\n- Search is faster on large accounts.\n- The v1 /legacy/invoices endpoint was removed."
GOODCH = "## 2.4.0\n- Added CSV export for invoices\n- Faster search on large accounts\n- BREAKING: removed the v1 /legacy/invoices endpoint\n\n## 2.3.1\n- Fixed rounding in tax totals"
BADCH = "MALFORMED-LAB release draft - nothing final here yet"

s = load(".claude/settings.json") or {}
deny = (s.get("permissions") or {}).get("deny") or []
ok({"Bash", "Edit"} <= set(deny), "settings deny Bash and Edit - the agent can only read", f"deny Bash and Edit in .claude/settings.json - deny is {deny}")
hk = [h for g in (s.get("hooks") or {}).get("PostToolUse") or [] if (g.get("matcher") or "*") in ("*", "") for h in g.get("hooks") or []]
ok(hk, "a PostToolUse hook with matcher * audits every tool call", "register an audit hook under PostToolUse with matcher *")
sc = load("notes.schema.json") or {}
ok(set(sc.get("required") or []) == {"version", "highlights", "breaking"} and sc.get("additionalProperties") is False
   and ((sc.get("properties") or {}).get("highlights") or {}).get("minItems") == 1,
   "notes.schema.json requires version, at least one highlight, and breaking, with no extra fields", "notes.schema.json: required [version, highlights, breaking], highlights minItems 1, additionalProperties false")
Path("CHANGES.txt").write_text(GOODCH + "\n")
for f_ in ("RELEASE.md",):
    if os.path.exists(f_):
        os.remove(f_)
n0 = len(text("runs/pipeline.log").splitlines())
rc, out, err = sh("./pipeline.sh", timeout=300)
ok(rc == 0 and text("RELEASE.md").strip() == WANT, "a good run exits 0 and renders RELEASE.md from the structured output",
   f"./pipeline.sh should exit 0 and write exactly:\n{WANT}\n- got exit {rc} and {text('RELEASE.md')[:200]!r}")
log1 = text("runs/pipeline.log").splitlines()[n0:]
sid = log1[-1].split("session=")[-1] if log1 and log1[-1].startswith("OK 2.4.0") else None
ok(sid, "runs/pipeline.log got 'OK 2.4.0 session=<id>'", f"append OK <version> session=<id> to runs/pipeline.log - new lines {log1}")
streams = sorted(glob.glob("runs/*.jsonl"), key=os.path.getmtime)
ok(streams and any(e.get("type") == "result" and e.get("session_id") == sid for e in events(streams[-1])), "the run's full event stream is kept under runs/",
   "save each run's stream-json output to runs/<timestamp>.jsonl")
aud = [x for x in events(".claude/audit.jsonl") if x.get("session") == sid]
ok(any(x.get("tool") == "Read" for x in aud), "the audit log has that session's Read call", f"audit.jsonl should have the Read call for session {sid}")
Path("CHANGES.txt").write_text(BADCH + "\n")
rc, out, err = sh("./pipeline.sh", timeout=300)
log2 = text("runs/pipeline.log").splitlines()[n0 + len(log1):]
ok(rc == 1 and text("RELEASE.md").strip() == WANT and log2 and log2[-1].startswith("FAIL"),
   "a run with no usable structured output exits 1, logs FAIL, and leaves the last good RELEASE.md",
   f"with a malformed CHANGES.txt the pipeline must exit 1, log a FAIL line, and keep RELEASE.md - got exit {rc}, log {log2}")
Path("CHANGES.txt").write_text(GOODCH + "\n")
PYEOF
```

## What you learned

- A trustworthy pipeline layers boundaries, audit, a schema, a bounded run, a fail-closed gate, and a log.
- Let the agent produce data and let deterministic code render artifacts and decide exit codes.
- On failure, keep the last good artifact and record why.
