---
type: task
title: "Write and register a word-count server"
minutes: 30
---

## Set up

Set up creates an empty `/root/mastery/052-mcp` and confirms `python3` and `jq` are available. You write the server yourself, with no SDK.

```bash
rm -rf /root/mastery/052-mcp && mkdir -p /root/mastery/052-mcp && cd /root/mastery/052-mcp
python3 --version && jq --version
```

## What to build

1. Write `wordcount_server.py`, an MCP server over stdio. Standard library only, one JSON-RPC message per line.
   - `initialize`: echo `protocolVersion` if it's one you support (`2025-06-18`, `2025-03-26`, `2024-11-05`), otherwise answer with your newest. Declare `capabilities.tools` and give `serverInfo`.
   - Notifications (no `id`) get no reply. `ping` returns `{}`.
   - `tools/list` returns one tool, `count_words`, with a description and an `inputSchema` requiring a string `text`.
   - `tools/call` returns `structuredContent` `{words, lines, chars}` (`split()`, `splitlines()`, `len()`), plus a text block and `isError: false`.
   - Errors:
     - A non-string `text` returns `isError: true`.
     - An unknown tool returns `-32602`, and an unknown method returns `-32601`.
     - An unparsable line returns `-32700`, and the server keeps reading.
     - Only JSON goes to stdout; logs go to stderr.
2. Write `pipe_test.sh [server]` (default `./wordcount_server.py`).
   - Pipe six messages in: initialize, the initialized notification, tools/list, a call on `"one two  three\nfour"`, a call with no arguments, and an unknown method.
   - Save the replies to `pipe.jsonl`, assert each one, and exit 1 on the first mismatch.
3. Register it with `claude mcp add --scope project wordcount -- python3 wordcount_server.py`. Then approve it in `.claude/settings.local.json` (`enabledMcpjsonServers`).
4. Run headless, allowing only `mcp__wordcount__count_words`, and save the stream as `run.jsonl`:
   > Use the wordcount tool to count the words in this sentence: the quick brown fox jumps over the lazy dog

The checker sends your server messages you never tried, and runs your `pipe_test.sh` against a server that miscounts lines.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Flush after every write (`sys.stdout.flush()`), or the client waits forever for a reply sitting in a buffer.
- `jq -e --slurp` turns the reply lines into one array, so `.[2].result.structuredContent` addresses the third reply.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/052-mcp
cat > wordcount_server.py <<'EOF'
#!/usr/bin/env python3
"""A minimal MCP server over stdio: newline-delimited JSON-RPC 2.0, one tool (count_words). No SDK."""
import json
import sys

SERVER = {"name": "wordcount", "version": "1.0.0"}
SUPPORTED = ["2025-06-18", "2025-03-26", "2024-11-05"]
TOOL = {
    "name": "count_words",
    "title": "Count words",
    "description": "Count the words, lines, and characters in a piece of text.",
    "inputSchema": {
        "type": "object",
        "properties": {"text": {"type": "string", "description": "The text to measure"}},
        "required": ["text"],
        "additionalProperties": False,
    },
    "outputSchema": {
        "type": "object",
        "properties": {"words": {"type": "integer"}, "lines": {"type": "integer"}, "chars": {"type": "integer"}},
        "required": ["words", "lines", "chars"],
    },
}


def log(msg):
    print(f"wordcount: {msg}", file=sys.stderr, flush=True)


def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def error(rid, code, message):
    send({"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}})


def count(text):
    return {"words": len(text.split()), "lines": len(text.splitlines()), "chars": len(text)}


def call_tool(params):
    if params.get("name") != TOOL["name"]:
        return None, (-32602, f"Unknown tool: {params.get('name')}")
    args = params.get("arguments") or {}
    if not isinstance(args.get("text"), str):
        return {"content": [{"type": "text", "text": "count_words needs a 'text' string argument"}], "isError": True}, None
    stats = count(args["text"])
    return {"content": [{"type": "text", "text": json.dumps(stats)}], "structuredContent": stats, "isError": False}, None


def handle(msg):
    rid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}
    if rid is None:
        return  # a notification: never answer
    if method == "initialize":
        asked = params.get("protocolVersion")
        send({"jsonrpc": "2.0", "id": rid, "result": {
            "protocolVersion": asked if asked in SUPPORTED else SUPPORTED[0],
            "capabilities": {"tools": {}},
            "serverInfo": SERVER,
        }})
    elif method == "ping":
        send({"jsonrpc": "2.0", "id": rid, "result": {}})
    elif method == "tools/list":
        send({"jsonrpc": "2.0", "id": rid, "result": {"tools": [TOOL]}})
    elif method == "tools/call":
        result, err = call_tool(params)
        if err:
            error(rid, *err)
        else:
            send({"jsonrpc": "2.0", "id": rid, "result": result})
    else:
        error(rid, -32601, f"Method not found: {method}")


def main():
    log("ready")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            error(None, -32700, "Parse error")
            continue
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0":
            error(msg.get("id") if isinstance(msg, dict) else None, -32600, "Invalid Request")
            continue
        handle(msg)


if __name__ == "__main__":
    main()
EOF
cat > pipe_test.sh <<'EOF'
#!/usr/bin/env bash
# pipe_test.sh [server] - drive an MCP server over stdin/stdout and assert each response. Exit 1 on the first mismatch.
set -u
server=${1:-./wordcount_server.py}
out=$(printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"pipe","version":"0"}}}' \
  '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"count_words","arguments":{"text":"one two  three\nfour"}}}' \
  '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"count_words","arguments":{}}}' \
  '{"jsonrpc":"2.0","id":5,"method":"no/such"}' | python3 "$server" 2> /dev/null)
echo "$out" > pipe.jsonl
check() {
  if echo "$out" | jq -e --slurp "$1" > /dev/null 2>&1; then echo "ok   $2"; else echo "FAIL $2"; exit 1; fi
}
check 'length == 5' "five responses - the notification gets none"
check '.[0].result.protocolVersion == "2025-06-18" and .[0].result.capabilities.tools != null' "initialize negotiates the version and declares tools"
check '.[1].result.tools[0].name == "count_words" and .[1].result.tools[0].inputSchema.required == ["text"]' "tools/list exposes count_words with its schema"
check '.[2].result.structuredContent == {"words": 4, "lines": 2, "chars": 19} and .[2].result.isError == false' "count_words counts words, lines, and chars"
check '.[3].result.isError == true and .[3].error == null' "missing text is a tool error the model can read, not a protocol error"
check '.[4].error.code == -32601' "an unknown method is -32601"
echo "all pipe checks passed"
EOF
chmod +x wordcount_server.py pipe_test.sh
./pipe_test.sh
claude mcp add --scope project wordcount -- python3 wordcount_server.py
mkdir -p .claude && echo '{"enabledMcpjsonServers": ["wordcount"]}' > .claude/settings.local.json
claude -p 'Use the wordcount tool to count the words in this sentence: the quick brown fox jumps over the lazy dog' --allowedTools mcp__wordcount__count_words --output-format stream-json --verbose < /dev/null > run.jsonl
jq -r 'select(.type == "result") | .result' run.jsonl
```

</details>

## Check your work

```bash
D=/root/mastery/052-mcp; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
REF = '#!/usr/bin/env python3\n"""A minimal MCP server over stdio: newline-delimited JSON-RPC 2.0, one tool (count_words). No SDK."""\nimport json\nimport sys\n\nSERVER = {"name": "wordcount", "version": "1.0.0"}\nSUPPORTED = ["2025-06-18", "2025-03-26", "2024-11-05"]\nTOOL = {\n    "name": "count_words",\n    "title": "Count words",\n    "description": "Count the words, lines, and characters in a piece of text.",\n    "inputSchema": {\n        "type": "object",\n        "properties": {"text": {"type": "string", "description": "The text to measure"}},\n        "required": ["text"],\n        "additionalProperties": False,\n    },\n    "outputSchema": {\n        "type": "object",\n        "properties": {"words": {"type": "integer"}, "lines": {"type": "integer"}, "chars": {"type": "integer"}},\n        "required": ["words", "lines", "chars"],\n    },\n}\n\n\ndef log(msg):\n    print(f"wordcount: {msg}", file=sys.stderr, flush=True)\n\n\ndef send(obj):\n    sys.stdout.write(json.dumps(obj) + "\\n")\n    sys.stdout.flush()\n\n\ndef error(rid, code, message):\n    send({"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}})\n\n\ndef count(text):\n    return {"words": len(text.split()), "lines": len(text.splitlines()), "chars": len(text)}\n\n\ndef call_tool(params):\n    if params.get("name") != TOOL["name"]:\n        return None, (-32602, f"Unknown tool: {params.get(\'name\')}")\n    args = params.get("arguments") or {}\n    if not isinstance(args.get("text"), str):\n        return {"content": [{"type": "text", "text": "count_words needs a \'text\' string argument"}], "isError": True}, None\n    stats = count(args["text"])\n    return {"content": [{"type": "text", "text": json.dumps(stats)}], "structuredContent": stats, "isError": False}, None\n\n\ndef handle(msg):\n    rid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}\n    if rid is None:\n        return  # a notification: never answer\n    if method == "initialize":\n        asked = params.get("protocolVersion")\n        send({"jsonrpc": "2.0", "id": rid, "result": {\n            "protocolVersion": asked if asked in SUPPORTED else SUPPORTED[0],\n            "capabilities": {"tools": {}},\n            "serverInfo": SERVER,\n        }})\n    elif method == "ping":\n        send({"jsonrpc": "2.0", "id": rid, "result": {}})\n    elif method == "tools/list":\n        send({"jsonrpc": "2.0", "id": rid, "result": {"tools": [TOOL]}})\n    elif method == "tools/call":\n        result, err = call_tool(params)\n        if err:\n            error(rid, *err)\n        else:\n            send({"jsonrpc": "2.0", "id": rid, "result": result})\n    else:\n        error(rid, -32601, f"Method not found: {method}")\n\n\ndef main():\n    log("ready")\n    for line in sys.stdin:\n        line = line.strip()\n        if not line:\n            continue\n        try:\n            msg = json.loads(line)\n        except ValueError:\n            error(None, -32700, "Parse error")\n            continue\n        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0":\n            error(msg.get("id") if isinstance(msg, dict) else None, -32600, "Invalid Request")\n            continue\n        handle(msg)\n\n\nif __name__ == "__main__":\n    main()'

srv = os.path.abspath("wordcount_server.py")
def talk(*msgs, raw=None):
    data = (raw if raw is not None else "") + "".join(json.dumps(m) + "\n" for m in msgs)
    rc, out, err = sh([sys.executable, srv], input=data, timeout=20)
    rows = []
    for l in out.splitlines():
        try:
            rows.append(json.loads(l))
        except ValueError:
            rows.append({"_bad": l})
    return rows, err
INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "chk", "version": "0"}}}
NOTE = {"jsonrpc": "2.0", "method": "notifications/initialized"}
def call(i, args, name="count_words"):
    return {"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": {"name": name, "arguments": args}}
TEXT = "Héllo   wörld\n\nsecond line here\tand a tab"
rows, err = talk(INIT, NOTE, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, call(3, {"text": TEXT}),
                 call(4, {"text": 42}), call(5, {"text": "x"}, name="nope"), {"jsonrpc": "2.0", "id": 6, "method": "resources/list"},
                 {"jsonrpc": "2.0", "id": 7, "method": "ping"})
bad = [r["_bad"] for r in rows if "_bad" in r]
ok(rows and not bad, "every stdout line is JSON - logs go to stderr", f"stdout must carry only JSON-RPC lines; found {bad[:2]}")
by = {r.get("id"): r for r in rows if "_bad" not in r}
ok(len(rows) == 7 and None not in by, "seven requests, seven replies - the notification got none", f"answer each request once and never a notification - got {len(rows)} replies")
init = (by.get(1) or {}).get("result") or {}
ok(init.get("protocolVersion") == "2025-03-26" and "tools" in (init.get("capabilities") or {}) and (init.get("serverInfo") or {}).get("name"),
   "initialize echoes a supported protocolVersion (2025-03-26) and declares the tools capability", f"initialize should echo 2025-03-26, declare capabilities.tools, and name serverInfo - got {init}")
tools = ((by.get(2) or {}).get("result") or {}).get("tools") or []
t0 = tools[0] if tools else {}
sch = t0.get("inputSchema") or {}
ok(len(tools) == 1 and t0.get("name") == "count_words" and t0.get("description") and sch.get("type") == "object"
   and (sch.get("properties") or {}).get("text", {}).get("type") == "string" and sch.get("required") == ["text"],
   "tools/list: count_words with a description and an inputSchema requiring a string text", f"tools/list should return one tool count_words with inputSchema {{type: object, properties.text: string, required: [text]}} - got {t0}")
res = (by.get(3) or {}).get("result") or {}
want = {"words": len(TEXT.split()), "lines": len(TEXT.splitlines()), "chars": len(TEXT)}
txt = " ".join(c.get("text", "") for c in res.get("content") or [] if c.get("type") == "text")
ok(res.get("structuredContent") == want and res.get("isError") is False and txt,
   f"count_words on hidden unicode text returns {want} as structuredContent plus a text block", f"count_words should return structuredContent {want}, a text content block, and isError false - got {res}")
r4 = by.get(4) or {}
ok((r4.get("result") or {}).get("isError") is True and "error" not in r4, "a non-string text is a tool error (isError: true) the model can read", f"wrong arguments should give result.isError true, not a protocol error - got {r4}")
ok(((by.get(5) or {}).get("error") or {}).get("code") == -32602, "an unknown tool name is a -32602 protocol error", f"tools/call for an unknown tool should be error -32602 - got {by.get(5)}")
ok(((by.get(6) or {}).get("error") or {}).get("code") == -32601 and (by.get(7) or {}).get("result") == {},
   "unknown methods get -32601, and ping gets an empty result", f"resources/list should be -32601 and ping should return {{}} - got {by.get(6)}, {by.get(7)}")
rows, err = talk({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "1999-01-01", "capabilities": {}, "clientInfo": {"name": "c", "version": "0"}}},
                 raw="this is not json\n")
ok(len(rows) == 2 and ((rows[0].get("error") or {}).get("code") == -32700) and str(((rows[1].get("result") or {}).get("protocolVersion") or "")).startswith("20"),
   "a garbage line gets -32700 and the server keeps going; an unknown version gets the server's own", f"reply -32700 to an unparsable line, keep reading, and answer an unsupported version with one you support - got {rows}")
rc, out, err = sh("./pipe_test.sh")
ok(rc == 0 and "all pipe checks passed" in out and len(events("pipe.jsonl")) == 5, "./pipe_test.sh passes and saves pipe.jsonl", f"pipe_test.sh should pass against your server - rc {rc}: {out.strip()[-200:]}")
with tempfile.TemporaryDirectory() as t:
    broken = Path(t, "broken.py")
    broken.write_text(REF.replace('"lines": len(text.splitlines())', '"lines": text.count("\\n")'))
    rc, out, err = sh(["./pipe_test.sh", str(broken)])
ok(rc == 1 and "FAIL" in out, "pipe_test.sh catches a server that miscounts lines", f"pipe_test.sh <server> must test the given server and exit 1 when a count is wrong - rc {rc}")
sh("./pipe_test.sh")
mj = (load(".mcp.json") or {}).get("mcpServers", {}).get("wordcount") or {}
ok(mj.get("command") and any("wordcount_server.py" in a for a in [mj.get("command", "")] + list(mj.get("args") or [])),
   ".mcp.json registers wordcount (project scope)", "run claude mcp add --scope project wordcount -- python3 wordcount_server.py")
st = load(".claude/settings.local.json") or {}
ok("wordcount" in (st.get("enabledMcpjsonServers") or []), "you approved the project server in .claude/settings.local.json", "add wordcount to enabledMcpjsonServers in .claude/settings.local.json")
ev = events("run.jsonl")
init = next((e for e in ev if e.get("type") == "system" and e.get("subtype") == "init"), {})
st = {s.get("name"): s.get("status") for s in init.get("mcp_servers") or []}
ok(st.get("wordcount") == "connected", "the headless run connected to wordcount", f"run.jsonl's init event should list wordcount as connected - got {st.get('wordcount')}")
used = [u for u in uses(ev) if u.get("name") == "mcp__wordcount__count_words"]
outs = [b for b in results(ev) if b.get("tool_use_id") in {u.get("id") for u in used}]
body = json.dumps([b.get("content") for b in outs])
ok(used and outs and not any(b.get("is_error") for b in outs) and re.search(r'words\\?"?\s*:\s*9\b', body),
   "Claude called mcp__wordcount__count_words and got 9 words back", f"the run should call mcp__wordcount__count_words (allow it with --allowedTools) and get words 9 - got {body[:200]}")
PYEOF
```

## What you learned

- An stdio MCP server is a loop: read a JSON-RPC line, answer requests by id, ignore notifications, and keep stdout for protocol only.
- Tool failures belong in the result (isError: true) where the model can read them; protocol errors are for malformed requests.
- Claude sees the tool as mcp__<server>__<tool> - the name you allow, deny, and match in hooks.
