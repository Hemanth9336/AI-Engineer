---
type: task
title: "Configure the status line, vim mode, and a keybinding"
minutes: 14
---

## Set up

Set up makes sure `~/.claude/settings.json` exists. Everything in this task is user-level configuration.

```bash
mkdir -p /root/mastery/021-terminal ~/.claude && cd /root/mastery/021-terminal
[ -f ~/.claude/settings.json ] || echo '{}' > ~/.claude/settings.json
```

## What to build

Wire three pieces of terminal comfort through your user configuration.

1. **Status line** - write `~/.claude/statusline.sh` and point `statusLine` at it in `~/.claude/settings.json`. It must print exactly:

```text
<model display name> | ctx <used percentage, rounded down>% | $<cost, 2 decimals> | <last folder of current_dir>[ | <vim mode>]
```

   The vim segment appears only when `vim.mode` is present, and a missing or null percentage shows as `0`.
2. **Vim mode** - turn on `editorMode: vim` and map `jj` to Escape.
3. **Keybinding** - in `~/.claude/keybindings.json`, bind `meta+k` to run `/compact` from the prompt.

Edit `~/.claude/settings.json` without losing what is already in it. The checker pipes three sample sessions into your script.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `jq '(.context_window.used_percentage // 0) | floor'` handles the null case.
- `command:compact` is the action that runs `/compact`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/021-terminal
cat > $HOME/.claude/statusline.sh <<'EOF'
#!/bin/bash
in=$(cat)
model=$(jq -r '.model.display_name // "?"' <<<"$in")
pct=$(jq -r '(.context_window.used_percentage // 0) | floor' <<<"$in")
cost=$(jq -r '.cost.total_cost_usd // 0' <<<"$in")
dir=$(jq -r '.workspace.current_dir // "" | split("/") | last' <<<"$in")
vim=$(jq -r '.vim.mode // empty' <<<"$in")
printf '%s | ctx %s%% | $%.2f | %s' "$model" "$pct" "$cost" "$dir"
[ -n "$vim" ] && printf ' | %s' "$vim"
echo
EOF
chmod +x ~/.claude/statusline.sh
tmp=$(mktemp) && jq '.statusLine = {"type": "command", "command": "~/.claude/statusline.sh"} | .editorMode = "vim" | .vimInsertModeRemaps = {"jj": "<Esc>"}' \
  ~/.claude/settings.json > "$tmp" && mv "$tmp" ~/.claude/settings.json
cat > $HOME/.claude/keybindings.json <<'EOF'
{
  "$schema": "https://www.schemastore.org/claude-code-keybindings.json",
  "bindings": [
    { "context": "Chat", "bindings": { "meta+k": "command:compact" } }
  ]
}
EOF
echo '{"model":{"display_name":"Opus 5.5"},"workspace":{"current_dir":"/root/mastery/021-terminal"},"cost":{"total_cost_usd":0.1342},"context_window":{"used_percentage":42.5},"vim":{"mode":"NORMAL"}}' | ~/.claude/statusline.sh
```

</details>

## Check your work

```bash
D=/root/mastery/021-terminal; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
home = os.path.expanduser("~")
s = load(home + "/.claude/settings.json") or {}
sl = s.get("statusLine") or {}
cmd = os.path.expanduser(sl.get("command", "").replace("$HOME", home))
ok(sl.get("type") == "command" and os.access(cmd, os.X_OK), "statusLine runs an executable script from user settings",
   "set statusLine to {type: command, command: ~/.claude/statusline.sh} in ~/.claude/settings.json and chmod +x the script")
ok(s.get("editorMode") == "vim" and (s.get("vimInsertModeRemaps") or {}).get("jj") == "<Esc>", "vim mode is on, with jj mapped to Escape",
   "set editorMode to vim and vimInsertModeRemaps {jj: <Esc>} in ~/.claude/settings.json")
samples = [
    ({"model": {"display_name": "Opus 5.5"}, "workspace": {"current_dir": "/srv/billing-api"}, "cost": {"total_cost_usd": 0.1342},
      "context_window": {"used_percentage": 42.5}, "vim": {"mode": "NORMAL"}}, "Opus 5.5 | ctx 42% | $0.13 | billing-api | NORMAL"),
    ({"model": {"display_name": "Haiku 5.5"}, "workspace": {"current_dir": "/root/x/docs-site"}, "cost": {"total_cost_usd": 0},
      "context_window": {"used_percentage": None}}, "Haiku 5.5 | ctx 0% | $0.00 | docs-site"),
    ({"model": {"display_name": "Sonnet 5.5"}, "workspace": {"current_dir": "/w/api"}, "cost": {"total_cost_usd": 2.5},
      "context_window": {"used_percentage": 97.9}, "vim": {"mode": "INSERT"}}, "Sonnet 5.5 | ctx 97% | $2.50 | api | INSERT"),
]
for data, want in samples:
    rc, out, err = sh([cmd], input=json.dumps(data), timeout=10) if os.access(cmd, os.X_OK) else (1, "", "no script")
    ok(rc == 0 and out.strip() == want, f"status line renders {want!r}", f"for {json.dumps(data)[:80]}... expected {want!r}, got {out.strip()!r} {err.strip()[:120]}")
kb = load(home + "/.claude/keybindings.json") or {}
chat = [b for blk in kb.get("bindings") or [] if blk.get("context") == "Chat" for b in (blk.get("bindings") or {}).items()]
ok(("meta+k", "command:compact") in chat, "keybindings.json binds meta+k to /compact in the Chat context",
   "in ~/.claude/keybindings.json add a Chat binding \"meta+k\": \"command:compact\"")
PYEOF
```

## What you learned

- `!` runs shell commands and `@` mentions files at the prompt; Esc, Shift+Tab, Ctrl+R, and Ctrl+G cover most daily needs.
- editorMode and vimInsertModeRemaps give the prompt vim editing; keybindings.json rebinds any action per context.
- The status line is your script reading session JSON on stdin - it must handle absent fields.
