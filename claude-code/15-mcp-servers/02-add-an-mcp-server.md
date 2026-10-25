---
type: task
title: "Add an MCP server"
minutes: 12
---

## Set up

Set up creates `/root/cc-lab/15-mcp` with `notes_server.py` - a small MCP server with one tool, `search_notes` - and the office notes it searches.

```bash
mkdir -p /root/cc-lab/15-mcp && cd /root/cc-lab/15-mcp
cat > notes.json <<'EOF'
[
  {"office": "Oslo", "topic": "wifi", "text": "Guest wifi: StacklineGuest, password fjord-7781"},
  {"office": "Lisbon", "topic": "wifi", "text": "Guest wifi: StacklineGuest, password tram-2290"},
  {"office": "Oslo", "topic": "door", "text": "Side door code 4417, weekdays 07:00-19:00"},
  {"office": "Lisbon", "topic": "parking", "text": "Visitor parking on level -2, ask reception for a card"}
]
EOF
cat > notes_server.py <<'EOF'
"""office-notes: a small MCP server that searches the office notes in notes.json."""
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

HERE = Path(__file__).parent
mcp = FastMCP("office-notes")


@mcp.tool()
def search_notes(query: str) -> dict:
    """Search the office notes (wifi, door codes, parking) with keywords like 'Oslo wifi'. Read-only."""
    with open(HERE / "calls.log", "a") as f:
        f.write(f"search_notes {query}\n")
    notes = json.loads((HERE / "notes.json").read_text())
    words = [w.lower() for w in query.split()]
    def blob(n):
        return f"{n['office']} {n['topic']} {n['text']}".lower()
    hits = [n for n in notes if all(w in blob(n) for w in words)] or [n for n in notes if any(w in blob(n) for w in words)]
    return {"results": hits[:5]}


if __name__ == "__main__":
    mcp.run()
EOF
python3 -c 'import mcp.server.fastmcp' && echo 'mcp package OK' || echo 'mcp package missing - run the install script from setup/README.md (step 7)'
claude --version
```

## What to build

1. Register the server for this project as `office-notes` (so it's written to `.mcp.json`), add a throwaway second server called `scratch`, list them, then remove `scratch`.
2. Ask Claude a question only the notes can answer, allowing just the MCP tool.

```bash
cd /root/cc-lab/15-mcp
claude mcp remove --scope project office-notes >/dev/null 2>&1 || true
claude mcp add --scope project office-notes -- "$(command -v python3)" /root/cc-lab/15-mcp/notes_server.py
claude mcp add --scope project scratch -- "$(command -v python3)" /root/cc-lab/15-mcp/notes_server.py
claude mcp list | tee mcp-list.txt
claude mcp remove --scope project scratch
claude mcp get office-notes
cat .mcp.json
claude -p "Use the office-notes tools to find the guest wifi password for the Oslo office. Reply with just the password." --allowedTools "mcp__office-notes__search_notes" --max-turns 5 > answer.txt
cat answer.txt calls.log
```

`answer.txt` should hold the Oslo guest wifi password, and `calls.log` shows the server really received the call.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Everything after `--` is the command Claude Code runs to start the server.
- `"$(command -v python3)"` records the full path of the Python that has the `mcp` package.

</details>

<details><summary>Solution</summary>

```bash
cd /root/cc-lab/15-mcp
claude mcp remove --scope project office-notes >/dev/null 2>&1 || true
claude mcp add --scope project office-notes -- "$(command -v python3)" /root/cc-lab/15-mcp/notes_server.py
claude mcp add --scope project scratch -- "$(command -v python3)" /root/cc-lab/15-mcp/notes_server.py
claude mcp list | tee mcp-list.txt
claude mcp remove --scope project scratch
claude mcp get office-notes
cat .mcp.json
claude -p "Use the office-notes tools to find the guest wifi password for the Oslo office. Reply with just the password." --allowedTools "mcp__office-notes__search_notes" --max-turns 5 > answer.txt
cat answer.txt calls.log
```

</details>

## Check your work

```bash
D=/root/cc-lab/15-mcp; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
cfg = (load(".mcp.json") or {}).get("mcpServers") or {}
srv = cfg.get("office-notes") or {}
ok("notes_server.py" in " ".join([srv.get("command", "")] + list(srv.get("args") or [])), ".mcp.json registers office-notes running notes_server.py", f".mcp.json should have an office-notes server running notes_server.py - got {list(cfg)}")
ok("scratch" not in cfg, "the scratch server was removed again", "remove the scratch server: claude mcp remove --scope project scratch")
ok("office-notes" in text("mcp-list.txt"), "mcp-list.txt shows office-notes in claude mcp list", "save the output of claude mcp list to mcp-list.txt")
ok("fjord-7781" in text("answer.txt"), "answer.txt holds the Oslo guest wifi password", f"answer.txt should hold the password from the notes - got {text('answer.txt').strip()[:120]!r}")
ok("search_notes" in text("calls.log"), "the office-notes server received a search_notes call", "calls.log has no search_notes call - did Claude use the MCP tool? Allow mcp__office-notes__search_notes")
ok(ran(r"guest wifi password for the Oslo office"), "the question was asked in a session in this folder", "run the claude -p question inside /root/cc-lab/15-mcp")
PYEOF
```

## What you learned

- An MCP server exposes tools in a standard format; Claude Code connects to it as a client.
- `claude mcp add/list/get/remove` manage servers; `--scope project` writes `.mcp.json` for the team.
- MCP tools are named `mcp__<server>__<tool>` and go through normal permissions.
