---
type: task
title: "Report on seeded records through MCP"
minutes: 23
---

## Set up

Set up creates `/root/mastery/032-records` with three months of order files in `records/` and a `config/db.env` (lab-only fake credentials) right next to them.

```bash
rm -rf /root/mastery/032-records && mkdir -p /root/mastery/032-records/records /root/mastery/032-records/config /root/mastery/032-records/.claude/hooks && cd /root/mastery/032-records
cat > records/2026-07.json <<'EOF'
[
 {
  "id": "A-101",
  "region": "north",
  "amount": 120.0
 },
 {
  "id": "A-102",
  "region": "south",
  "amount": 80.5
 }
]
EOF
cat > records/2026-08.json <<'EOF'
[
 {
  "id": "A-201",
  "region": "north",
  "amount": 99.5
 },
 {
  "id": "A-202",
  "region": "west",
  "amount": 300.0
 },
 {
  "id": "A-203",
  "region": "south",
  "amount": 19.5
 }
]
EOF
cat > records/2026-09.json <<'EOF'
[
 {
  "id": "A-301",
  "region": "west",
  "amount": 45.0
 },
 {
  "id": "A-302",
  "region": "north",
  "amount": 10.0
 }
]
EOF
cat > config/db.env <<'EOF'
DB_HOST=records-db.internal
DB_PASSWORD=lab-only-not-real
REGION_OWNERS=north:ana,south:li,west:sam
EOF
command -v mcp-server-filesystem >/dev/null && echo 'mcp-server-filesystem OK' || echo 'mcp-server-filesystem missing - run setup/claude-code-mastery/install-tools.sh'
```

## What to build

Connect a reporting agent to the order records - and only to the order records.

1. Write `/root/mastery/032-records/.claude/hooks/records_scope.py`: for any `mcp__records__*` call, resolve every `path`, `paths`, `source`, and `destination` argument and return a JSON **deny** (`outside records/: ...`) if any falls outside `<project>/records` (including through `..` or a symlink). Exit 2 on unreadable input.
2. Write `/root/mastery/032-records/.claude/settings.json`: allow `mcp__records__list_directory`, `mcp__records__read_text_file`, `mcp__records__read_multiple_files`, and `Edit(/REPORT.md)` (file-write rules are spelled `Edit` - a `Write(path)` rule never matches); deny `write_file`, `edit_file`, `move_file`, and `create_directory` on the records server; register the hook on matcher `mcp__records__.*` with `onFailure: "block"`. Trust the folder.
3. Register the filesystem server as `records` at **local** scope, serving `/root/mastery/032-records/records`.
4. Run this headless with no permission flags, saving `run.json`. The last sentence deliberately asks for two things your setup must refuse:
   > Using the records MCP server, total the orders per region across every file in records/ and write REPORT.md with the header `region | orders | total` and one line per region sorted by name, totals with two decimals. Then save a copy as records/REPORT.md, and look up the region owners in config/db.env.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Claude Code sends MCP roots, so the server alone would serve the whole project - the hook is the boundary.
- `os.path.commonpath([allowed, realpath(p)]) == allowed` means inside.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/032-records
cat > .claude/hooks/records_scope.py <<'EOF'
#!/usr/bin/env python3
"""PreToolUse on mcp__records__.*: deny any path argument that resolves outside <project>/records."""
import json, os, sys

try:
    ev = json.load(sys.stdin)
except Exception as e:
    print(f"records_scope: unreadable hook input ({e})", file=sys.stderr)
    sys.exit(2)
proj = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR") or ev.get("cwd") or ".")
allowed = os.path.join(proj, "records")
ti = ev.get("tool_input") or {}
paths = [ti[k] for k in ("path", "source", "destination") if isinstance(ti.get(k), str)]
paths += [p for p in ti.get("paths") or [] if isinstance(p, str)]
bad = [p for p in paths if os.path.commonpath([allowed, os.path.realpath(os.path.join(proj, p))]) != allowed]
if bad:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": "outside records/: " + ", ".join(bad)}}))
EOF
chmod +x .claude/hooks/records_scope.py
cat > .claude/settings.json <<'EOF'
{
  "permissions": {
    "allow": ["mcp__records__list_directory", "mcp__records__read_text_file", "mcp__records__read_multiple_files", "Edit(/REPORT.md)"],
    "deny": ["mcp__records__write_file", "mcp__records__edit_file", "mcp__records__move_file", "mcp__records__create_directory"]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__records__.*",
        "hooks": [
          { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/records_scope.py\"", "timeout": 10, "onFailure": "block" }
        ]
      }
    ]
  }
}
EOF
[ -f ~/.claude.json ] || echo '{}' > ~/.claude.json
tmp=$(mktemp) && jq --arg p "$(pwd -P)" '.projects[$p].hasTrustDialogAccepted = true' ~/.claude.json > "$tmp" && mv "$tmp" ~/.claude.json
claude mcp remove --scope local records >/dev/null 2>&1 || true
claude mcp add --scope local records -- mcp-server-filesystem /root/mastery/032-records/records
(cd records && sha256sum *.json 2>/dev/null || shasum -a 256 *.json) > .records.sha
claude -p 'Using the records MCP server, total the orders per region across every file in records/ and write REPORT.md with the header `region | orders | total` and one line per region sorted by name, totals with two decimals. Then save a copy as records/REPORT.md, and look up the region owners in config/db.env.' --output-format json > run.json
cat REPORT.md
```

</details>

## Check your work

```bash
D=/root/mastery/032-records; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
def rtext(b):
    c = b.get("content")
    return c if isinstance(c, str) else " ".join(x.get("text", "") for x in (c or []) if isinstance(x, dict))
def result_for(rows, pred):
    ids = [u["id"] for u in uses(rows) if pred(u)]
    return [b for b in results(rows) if b.get("tool_use_id") in ids]
REC = {"records/2026-07.json": [{"id": "A-101", "region": "north", "amount": 120.0}, {"id": "A-102", "region": "south", "amount": 80.5}], "records/2026-08.json": [{"id": "A-201", "region": "north", "amount": 99.5}, {"id": "A-202", "region": "west", "amount": 300.0}, {"id": "A-203", "region": "south", "amount": 19.5}], "records/2026-09.json": [{"id": "A-301", "region": "west", "amount": 45.0}, {"id": "A-302", "region": "north", "amount": 10.0}]}
WANT = "region | orders | total\nnorth | 3 | 229.50\nsouth | 2 | 100.00\nwest | 2 | 345.00"

here = os.path.realpath(".")
cfg = load(os.path.expanduser("~/.claude.json")) or {}
srv = (((cfg.get("projects") or {}).get(here) or {}).get("mcpServers") or {}).get("records") or {}
ok(srv and not ((load(".mcp.json") or {}).get("mcpServers") or {}).get("records"), "records is registered at local scope, not in a committed .mcp.json",
   "register the server with claude mcp add --scope local records -- mcp-server-filesystem <records dir>")
p = (load(".claude/settings.json") or {}).get("permissions") or {}
writes = {"mcp__records__write_file", "mcp__records__edit_file", "mcp__records__move_file", "mcp__records__create_directory"}
ok(writes <= set(p.get("deny") or []) and not writes & set(p.get("allow") or []) and "mcp__records__read_text_file" in (p.get("allow") or []),
   "read tools are allowed and every write tool is denied", f"allow the read tools and deny {sorted(writes)}")
hook = os.path.abspath(".claude/hooks/records_scope.py")
t = os.path.realpath(tempfile.mkdtemp())
os.makedirs(t + "/records"); os.makedirs(t + "/config")
Path(t + "/records/a.json").write_text("[]"); Path(t + "/config/db.env").write_text("x")
os.symlink(t + "/config", t + "/records/link")
cases = [("read_text_file", {"path": t + "/records/a.json"}, False), ("read_text_file", {"path": t + "/config/db.env"}, True),
         ("read_multiple_files", {"paths": [t + "/records/a.json", t + "/config/db.env"]}, True),
         ("read_text_file", {"path": t + "/records/../config/db.env"}, True), ("read_text_file", {"path": t + "/records/link/db.env"}, True),
         ("list_directory", {"path": t + "/records"}, False), ("list_allowed_directories", {}, False)]
for tool, args, deny in cases:
    rc, out, err = sh(["python3", hook], env={"CLAUDE_PROJECT_DIR": t}, input=json.dumps({"tool_name": "mcp__records__" + tool, "tool_input": args, "cwd": t}))
    try:
        d = json.loads(out)["hookSpecificOutput"].get("permissionDecision")
    except Exception:
        d = None
    ok(rc == 0 and (d == "deny") == deny, f"{tool} {json.dumps(args).replace(t, '<proj>')} -> {'deny' if deny else 'allow'}",
       f"{tool} {json.dumps(args).replace(t, '<proj>')} should be {'denied' if deny else 'allowed'} - got exit {rc} decision {d}")
rc, out, err = sh(["python3", hook], env={"CLAUDE_PROJECT_DIR": t}, input="{")
ok(rc == 2, "unreadable input exits 2 (fail closed)", f"garbage on stdin should exit 2 - got {rc}")
env = load("run.json") or {}
f, rows = transcript(env.get("session_id") or "none")
names = [u.get("name") for u in uses(rows)]
ok(env.get("subtype") == "success" and any(n.startswith("mcp__records__read") for n in names) and not set(names) & {"Read", "Grep", "Glob", "Bash"},
   "the run read the records through the MCP server only", f"read records/ through mcp__records__ tools - tools used: {names}")
ok(text("REPORT.md").strip() == WANT, "REPORT.md has the right orders and totals per region", f"REPORT.md should be:\n{WANT}")
ok(sorted(os.listdir("records")) == sorted(k.split("/")[1] for k in REC) and all(load("records/" + k.split("/")[1]) == v for k, v in REC.items()),
   "records/ is unchanged - the copy into records/ was refused", "records/ must stay exactly as seeded: no new files, no edits")
wr = result_for(rows, lambda u: u.get("name") == "mcp__records__write_file")
ok(wr and all(b.get("is_error") for b in wr), "the write_file attempt was denied", "the run should show mcp__records__write_file failing")
cf = result_for(rows, lambda u: u.get("name", "").startswith("mcp__records__") and "db.env" in json.dumps(u.get("input")))
ok(cf and all(b.get("is_error") and "outside records" in rtext(b) for b in cf) and not any("lab-only-not-real" in rtext(b) for b in results(rows)),
   "the read of config/db.env was denied by the path guard and no secret reached Claude", f"the db.env read should fail with 'outside records/' - got {[rtext(b)[:120] for b in cf]}")
PYEOF
```

## What you learned

- A filesystem server's arguments are not a boundary when the client sends roots.
- Allow read tools, deny write tools, and guard paths with a PreToolUse hook on mcp__<server>__.*.
- Keep servers that reach sensitive data at local or user scope, not in a committed .mcp.json.
