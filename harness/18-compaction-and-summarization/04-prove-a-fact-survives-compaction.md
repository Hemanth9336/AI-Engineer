---
type: task
title: "Prove a fact survives compaction"
minutes: 10
---

## Set up

Continue in the same folder, with your `compact.py` and `agent.py` from the previous task. `/opt/harness/labmock.py` is the scripted model from earlier topics.

```bash
mkdir -p /root/harness-lab/18-compact/workspace/services
cd /root/harness-lab/18-compact
cat > workspace/README.md <<'EOF'
# Stackline services
Two services run in production: billing and search.
Config lives in services/<name>.yaml.
EOF
cat > workspace/services/billing.yaml <<'EOF'
name: billing
port: 8081
owner: payments team
replicas: 3
EOF
cat > workspace/services/search.yaml <<'EOF'
name: search
port: 9200
owner: discovery team
replicas: 5
EOF
python - <<'EOF'
from pathlib import Path
Path('workspace/logs').mkdir(parents=True, exist_ok=True)
for n in range(1, 7):
    Path(f'workspace/logs/part{n}.log').write_text(''.join(f'line {n}.{i} INFO search request ok {i * 7 % 300}ms\n' for i in range(60)))
EOF
[ -f agent.py ] || cat > agent.py <<'EOF'
import json
import sys
from pathlib import Path

from openai import OpenAI

SYSTEM = "You are Stackline's project assistant. Use the tools to look at the workspace before answering. Answer briefly."

SCHEMAS = [
    {"type": "function", "function": {
        "name": "list_dir",
        "description": "List the files and folders inside a workspace folder. Folders end with /. Use it to find files before reading them.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Folder relative to the workspace, for example services. Use . for the top."}},
            "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a text file from the workspace and return its contents. Use it whenever the answer depends on what a file says.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "File path relative to the workspace, for example services/billing.yaml"}},
            "required": ["path"]}}},
]

WORK = Path(__file__).parent / "workspace"


def list_dir(path="."):
    p = WORK / path
    if not p.is_dir():
        return f"error: no such folder {path}"
    return "\n".join(sorted(c.name + ("/" if c.is_dir() else "") for c in p.iterdir()))


def read_file(path):
    p = WORK / path
    if not p.is_file():
        return f"error: no such file {path}"
    return p.read_text()


IMPL = {"list_dir": list_dir, "read_file": read_file}


def run_tool(name, args):
    if name not in IMPL:
        return f"error: unknown tool {name}"
    try:
        return IMPL[name](**args)
    except TypeError as e:
        return f"error: bad arguments for {name}: {e}"


def run(question, max_steps=8):
    client = OpenAI()
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    for _ in range(max_steps):
        msg = client.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=messages).choices[0].message
        if not msg.tool_calls:
            return msg.content
        messages.append(msg)
        for call in msg.tool_calls:
            result = run_tool(call.function.name, json.loads(call.function.arguments or "{}"))
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return f"stopped: reached max steps ({max_steps})"


if __name__ == "__main__":
    answer = run(sys.argv[1])
    print(answer)
    sys.exit(2 if answer.startswith("stopped: reached max steps") else 0)
EOF
echo 'agent.py is your loop with a step limit (topic 08)'
```

## What to build

1. **Pin facts.** Give `agent.py` a `pin_fact(fact)` tool that returns `[pin] <fact>`. In `compact.py`, when old turns are summarized:
   - Collect the facts from `[pin] ` tool results in those old turns, plus the facts already in an earlier `[pinned facts]` message.
   - Put them in one user message right after the task: `[pinned facts]\n- fact one\n- fact two`. That message is never sent to the summarizer and is never dropped.
   - Then the summary message, then the last `keep_last` turns, as before.
2. **Prove it.** Write `/root/harness-lab/18-compact/test_compaction.py` that:
   - Starts a `MockModel` with two rules: a summarizer rule (`"on": "system"`, matching "summari") that returns a **lossy** summary without the fact, and an agent rule (`"by": "calls"`) that first calls `pin_fact` with `Change window is Sunday 02:00-04:00 UTC (CHG-5521)`, then reads `logs/part1.log` to `logs/part6.log`, then answers.
   - Runs `python agent.py ...` against it.
   - Prints `PASS: ...` and exits 0 only if at least one compaction happened **and** `CHG-5521` is in the agent's last request; otherwise prints `FAIL: ...` and exits 1.

```bash
cd /root/harness-lab/18-compact
python test_compaction.py
```

The checker also runs your test against a `compact.py` **without** pinning - it must fail there.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Filter the `[pinned facts]` message out before grouping turns, so it's never part of `old`.
- `m.requests` holds every request the mock received - filter by `model` to tell the agent's calls from the summarizer's.
- Use `cwd=Path(__file__).parent` so the test runs the agent next to it, wherever you start it from.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/18-compact
cat > compact.py <<'EOF'
import json

SUMMARIZER = ("You compress an AI agent's working history so it can keep going with less context. "
              "Summarize the earlier steps below: which tools were called, what they found (keep exact names, "
              "numbers, paths and error messages), and what is still unknown. At most 150 words, plain text.")
PREFIX = "[summary of earlier steps]\n"
PIN = "[pin] "
PINNED = "[pinned facts]\n"
LIMIT = 6000
KEEP_LAST = 2


def size(msgs):
    return sum(len(json.dumps(m)) for m in msgs)


def turns(msgs):
    out = []
    for m in msgs:
        if m.get("role") == "tool" and out:
            out[-1].append(m)
        else:
            out.append([m])
    return out


def as_text(msgs):
    lines = []
    for m in msgs:
        if m.get("tool_calls"):
            calls = ", ".join(f"{c['function']['name']}({c['function']['arguments']})" for c in m["tool_calls"])
            lines.append(f"assistant called: {calls}")
        else:
            lines.append(f"{m['role']}: {m.get('content') or ''}")
    return "\n".join(lines)


def pins_in(msgs):
    facts = []
    for m in msgs:
        c = str(m.get("content") or "")
        if c.startswith(PINNED):
            facts += [line[2:] for line in c[len(PINNED):].splitlines() if line.startswith("- ")]
        elif m.get("role") == "tool" and c.startswith(PIN):
            facts.append(c[len(PIN):])
    return list(dict.fromkeys(facts))


def compact(messages, client, limit=LIMIT, keep_last=KEEP_LAST):
    head = messages[:2]
    pinned = [m for m in messages[2:] if str(m.get("content") or "").startswith(PINNED)]
    rest = [m for m in messages[2:] if m not in pinned]
    groups = turns(rest)
    if size(rest) <= limit or len(groups) <= keep_last:
        return messages
    old, recent = groups[:-keep_last], groups[-keep_last:]
    summary = client.chat.completions.create(model="lab-mini", messages=[
        {"role": "system", "content": SUMMARIZER},
        {"role": "user", "content": as_text([m for g in old for m in g])},
    ]).choices[0].message.content
    facts = pins_in(pinned + [m for g in old for m in g])
    keep = [{"role": "user", "content": PINNED + "\n".join(f"- {f}" for f in facts)}] if facts else []
    return head + keep + [{"role": "user", "content": PREFIX + summary}] + [m for g in recent for m in g]

EOF
cat > agent.py <<'EOF'
import json
import sys
from pathlib import Path

from openai import OpenAI

from compact import compact

SYSTEM = "You are Stackline's project assistant. Use the tools to look at the workspace before answering. Answer briefly."

SCHEMAS = [
    {"type": "function", "function": {
        "name": "list_dir",
        "description": "List the files and folders inside a workspace folder. Folders end with /. Use it to find files before reading them.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Folder relative to the workspace, for example services. Use . for the top."}},
            "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a text file from the workspace and return its contents. Use it whenever the answer depends on what a file says.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "File path relative to the workspace, for example services/billing.yaml"}},
            "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "pin_fact",
        "description": "Pin a fact that must survive when old history is summarized: the user's constraints and decisions, IDs, exact values you will need later.",
        "parameters": {"type": "object", "properties": {
            "fact": {"type": "string", "description": "One short, self-contained fact, for example: Change window is Sunday 02:00-04:00 UTC (CHG-5521)"}},
            "required": ["fact"]}}},
]

WORK = Path(__file__).parent / "workspace"


def list_dir(path="."):
    p = WORK / path
    if not p.is_dir():
        return f"error: no such folder {path}"
    return "\n".join(sorted(c.name + ("/" if c.is_dir() else "") for c in p.iterdir()))


def read_file(path):
    p = WORK / path
    if not p.is_file():
        return f"error: no such file {path}"
    return p.read_text()


def pin_fact(fact):
    return f"[pin] {fact}"


IMPL = {"list_dir": list_dir, "read_file": read_file, "pin_fact": pin_fact}


def run_tool(name, args):
    if name not in IMPL:
        return f"error: unknown tool {name}"
    try:
        return IMPL[name](**args)
    except TypeError as e:
        return f"error: bad arguments for {name}: {e}"


def run(question, max_steps=8):
    client = OpenAI()
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    for _ in range(max_steps):
        messages = compact(messages, client)
        msg = client.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=messages).choices[0].message
        if not msg.tool_calls:
            return msg.content
        messages.append({"role": "assistant", "content": msg.content,
                         "tool_calls": [{"id": c.id, "type": "function", "function": {"name": c.function.name, "arguments": c.function.arguments}}
                                        for c in msg.tool_calls]})
        for call in msg.tool_calls:
            result = run_tool(call.function.name, json.loads(call.function.arguments or "{}"))
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return f"stopped: reached max steps ({max_steps})"


if __name__ == "__main__":
    answer = run(sys.argv[1])
    print(answer)
    sys.exit(2 if answer.startswith("stopped: reached max steps") else 0)

EOF
cat > test_compaction.py <<'EOF'
"""Prove a pinned fact survives compaction, with a scripted model. Usage: python test_compaction.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, "/opt/harness")
from labmock import MockModel

FACT = "Change window is Sunday 02:00-04:00 UTC (CHG-5521)"
LOSSY = "Read several search logs; nothing unusual so far."
script = ([{"tool": "pin_fact", "args": {"fact": FACT}}]
          + [{"tool": "read_file", "args": {"path": f"logs/part{n}.log"}} for n in range(1, 7)]
          + ["Done."])

with MockModel(rules=[{"match": "summari", "on": "system", "steps": [LOSSY]},
                      {"match": "", "by": "calls", "steps": script}]) as m:
    rc, out, err = m.run(["python", "agent.py", "Check the search logs and plan the restart."], cwd=Path(__file__).parent, timeout=60)

agent = [r for r in m.requests if r.get("model") == "lab-fast"]
summaries = [r for r in m.requests if r.get("model") == "lab-mini"]
last = json.dumps(agent[-1]["messages"]) if agent else ""
problems = []
if rc != 0:
    problems.append(f"agent exited {rc}: {err[-200:]}")
if not summaries:
    problems.append("no compaction happened, so this run proves nothing")
if "CHG-5521" not in last:
    problems.append("the pinned fact is missing from the final request")
if problems:
    print("FAIL: " + "; ".join(problems))
    sys.exit(1)
print(f"PASS: CHG-5521 survived {len(summaries)} compaction(s)")

EOF
python test_compaction.py
```

</details>

## Check your work

```bash
D=/root/harness-lab/18-compact; cd $D 2>/dev/null || echo "❌ create $D"
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
def valid(h):
    pending = set()
    for x in h:
        if x.get("role") == "tool":
            if x.get("tool_call_id") not in pending:
                return False
            pending.discard(x["tool_call_id"])
        else:
            if pending:
                return False
            pending = {c["id"] for c in x.get("tool_calls") or []}
    return not pending

sys.path.insert(0, ".")
import shutil, tempfile
from openai import OpenAI
def turn(i, n, tag):
    return [{"role": "assistant", "content": None, "tool_calls": [{"id": f"c{i}", "type": "function", "function": {"name": "read_file", "arguments": "{}"}}]},
            {"role": "tool", "tool_call_id": f"c{i}", "content": tag + " " + "x" * n}]
pin = [{"role": "assistant", "content": None, "tool_calls": [{"id": "p1", "type": "function", "function": {"name": "pin_fact", "arguments": "{}"}}]},
       {"role": "tool", "tool_call_id": "p1", "content": "[pin] Don't restart billing (decided by Ana)"}]
head = [{"role": "system", "content": "S"}, {"role": "user", "content": "task"}]
try:
    import compact as C
    with MockModel(rules=[{"match": "summari", "on": "system", "steps": ["Read some files."]}]) as m:
        cl = OpenAI(base_url=m.url, api_key="mock")
        r = C.compact(head + pin + [x for i in range(1, 6) for x in turn(i, 1500, f"T{i}")], cl)
        pinned = [x for x in r if str(x.get("content") or "").startswith("[pinned facts]")]
        ok(r[:2] == head and len(pinned) == 1 and r[2] == pinned[0] and pinned[0]["role"] == "user" and "- Don't restart billing (decided by Ana)" in pinned[0]["content"] and valid(r),
           "a pinned fact moves into one [pinned facts] message right after the task", f"got {[str(x.get('content'))[:40] for x in r[2:4]]}")
        r2 = C.compact(r + [x for i in range(6, 10) for x in turn(i, 1500, f"T{i}")], cl)
        pinned2 = [x for x in r2 if str(x.get("content") or "").startswith("[pinned facts]")]
        ok(len(pinned2) == 1 and r2[2] == pinned2[0] and "Don't restart billing (decided by Ana)" in pinned2[0]["content"] and "[pinned facts]" not in json.dumps(m.requests[-1]["messages"]),
           "pinned facts survive a second compaction and are never sent to the summarizer", "after another compaction the fact must still be in the single [pinned facts] message, which shouldn't be summarized")
except Exception as e:
    ok(False, "", f"compact.py should still define compact(messages, client) - {type(e).__name__}: {e}")
with MockModel([{"tool": "pin_fact", "args": {"fact": "Use port 9201"}}, "ok"]) as m:
    rc, out, err = m.run(["python", "agent.py", "hi"], timeout=20)
names = [(t.get("function") or {}).get("name") for t in (m.requests[0].get("tools") or [])] if m.requests else []
res = [x.get("content") for x in (m.requests[-1]["messages"] if m.requests else []) if x.get("role") == "tool"]
ok("pin_fact" in names and res == ["[pin] Use port 9201"], "agent.py has a pin_fact tool that returns [pin] <fact>", f"tools {names}, results {res}, {err[-150:]}")
r = subprocess.run([sys.executable, "test_compaction.py"], capture_output=True, text=True, timeout=120)
ok(r.returncode == 0 and r.stdout.strip().startswith("PASS"), "test_compaction.py passes on your harness", f"exit {r.returncode}: {(r.stdout + r.stderr)[-300:]}")
tmp = Path(tempfile.mkdtemp())
shutil.copytree(".", tmp / "h", ignore=shutil.ignore_patterns("__pycache__"))
(tmp / "h" / "compact.py").write_text("import json\n\nSUMMARIZER = (\"You compress an AI agent's working history so it can keep going with less context. \"\n              \"Summarize the earlier steps below: which tools were called, what they found (keep exact names, \"\n              \"numbers, paths and error messages), and what is still unknown. At most 150 words, plain text.\")\nPREFIX = \"[summary of earlier steps]\\n\"\nLIMIT = 6000\nKEEP_LAST = 2\n\n\ndef size(msgs):\n    return sum(len(json.dumps(m)) for m in msgs)\n\n\ndef turns(msgs):\n    out = []\n    for m in msgs:\n        if m.get(\"role\") == \"tool\" and out:\n            out[-1].append(m)\n        else:\n            out.append([m])\n    return out\n\n\ndef as_text(msgs):\n    lines = []\n    for m in msgs:\n        if m.get(\"tool_calls\"):\n            calls = \", \".join(f\"{c['function']['name']}({c['function']['arguments']})\" for c in m[\"tool_calls\"])\n            lines.append(f\"assistant called: {calls}\")\n        else:\n            lines.append(f\"{m['role']}: {m.get('content') or ''}\")\n    return \"\\n\".join(lines)\n\n\ndef compact(messages, client, limit=LIMIT, keep_last=KEEP_LAST):\n    head, rest = messages[:2], messages[2:]\n    groups = turns(rest)\n    if size(rest) <= limit or len(groups) <= keep_last:\n        return messages\n    old, recent = groups[:-keep_last], groups[-keep_last:]\n    summary = client.chat.completions.create(model=\"lab-mini\", messages=[\n        {\"role\": \"system\", \"content\": SUMMARIZER},\n        {\"role\": \"user\", \"content\": as_text([m for g in old for m in g])},\n    ]).choices[0].message.content\n    return head + [{\"role\": \"user\", \"content\": PREFIX + summary}] + [m for g in recent for m in g]\n")
r = subprocess.run([sys.executable, "test_compaction.py"], cwd=tmp / "h", capture_output=True, text=True, timeout=120)
ok(r.returncode != 0 and "FAIL" in r.stdout, "test_compaction.py fails when compaction forgets pins - so it really tests something", f"with a compact.py that has no pinning, your test should FAIL - it exited {r.returncode}: {r.stdout[-200:]}")
shutil.rmtree(tmp, ignore_errors=True)
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Constraints, decisions, exact IDs, the task and the latest turns must never be summarized away.
- Pinning keeps critical facts outside the summary, in a message the compactor only merges.
- Test compaction with a scripted model and a lossy summarizer - and check the test fails without the fix.
