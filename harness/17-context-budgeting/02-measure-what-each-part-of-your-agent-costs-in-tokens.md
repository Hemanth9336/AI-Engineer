---
type: task
title: "Measure what each part of your agent costs in tokens"
minutes: 9
---

## Set up

`history.json` is the conversation from a real run: the user's question, two tool calls, and their results - one of them a big log excerpt.

```bash
mkdir -p /root/harness-lab/17-budget/workspace/services
cd /root/harness-lab/17-budget
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
cat > history.json <<'EOF'
[
 {
  "role": "user",
  "content": "Why is search slow today?"
 },
 {
  "role": "assistant",
  "content": null,
  "tool_calls": [
   {
    "id": "call_1",
    "type": "function",
    "function": {
     "name": "read_file",
     "arguments": "{\"path\": \"services/search.yaml\"}"
    }
   }
  ]
 },
 {
  "role": "tool",
  "tool_call_id": "call_1",
  "content": "name: search\nport: 9200\nowner: discovery team\nreplicas: 5\n"
 },
 {
  "role": "assistant",
  "content": null,
  "tool_calls": [
   {
    "id": "call_2",
    "type": "function",
    "function": {
     "name": "read_file",
     "arguments": "{\"path\": \"logs/search.log\"}"
    }
   }
  ]
 },
 {
  "role": "tool",
  "tool_call_id": "call_2",
  "content": "2026-03-14T09:00:00Z INFO search: GET /api/items/0 200 12ms\n2026-03-14T09:00:01Z INFO search: GET /api/items/1 200 13ms\n2026-03-14T09:00:02Z INFO search: GET /api/items/2 200 14ms\n2026-03-14T09:00:03Z INFO search: GET /api/items/3 200 15ms\n2026-03-14T09:00:04Z INFO search: GET /api/items/4 200 16ms\n2026-03-14T09:00:05Z INFO search: GET /api/items/5 200 17ms\n2026-03-14T09:00:06Z INFO search: GET /api/items/6 200 18ms\n2026-03-14T09:00:07Z INFO search: GET /api/items/7 200 19ms\n2026-03-14T09:00:08Z INFO search: GET /api/items/8 200 20ms\n2026-03-14T09:00:09Z INFO search: GET /api/items/9 200 21ms\n2026-03-14T09:00:10Z INFO search: GET /api/items/10 200 22ms\n2026-03-14T09:00:11Z INFO search: GET /api/items/11 200 23ms\n2026-03-14T09:00:12Z INFO search: GET /api/items/12 200 24ms\n2026-03-14T09:00:13Z INFO search: GET /api/items/13 200 25ms\n2026-03-14T09:00:14Z INFO search: GET /api/items/14 200 26ms\n2026-03-14T09:00:15Z INFO search: GET /api/items/15 200 27ms\n2026-03-14T09:00:16Z INFO search: GET /api/items/16 200 28ms\n2026-03-14T09:00:17Z INFO search: GET /api/items/17 200 29ms\n2026-03-14T09:00:18Z INFO search: GET /api/items/18 200 30ms\n2026-03-14T09:00:19Z INFO search: GET /api/items/19 200 31ms\n2026-03-14T09:00:20Z INFO search: GET /api/items/20 200 32ms\n2026-03-14T09:00:21Z INFO search: GET /api/items/21 200 33ms\n2026-03-14T09:00:22Z INFO search: GET /api/items/22 200 34ms\n2026-03-14T09:00:23Z INFO search: GET /api/items/23 200 35ms\n2026-03-14T09:00:24Z INFO search: GET /api/items/24 200 36ms\n2026-03-14T09:00:25Z INFO search: GET /api/items/25 200 37ms\n2026-03-14T09:00:26Z INFO search: GET /api/items/26 200 38ms\n2026-03-14T09:00:27Z INFO search: GET /api/items/27 200 39ms\n2026-03-14T09:00:28Z INFO search: GET /api/items/28 200 40ms\n2026-03-14T09:00:29Z INFO search: GET /api/items/29 200 41ms\n2026-03-14T09:00:30Z INFO search: GET /api/items/30 200 42ms\n2026-03-14T09:00:31Z INFO search: GET /api/items/31 200 43ms\n2026-03-14T09:00:32Z INFO search: GET /api/items/32 200 44ms\n2026-03-14T09:00:33Z INFO search: GET /api/items/33 200 45ms\n2026-03-14T09:00:34Z INFO search: GET /api/items/34 200 46ms\n2026-03-14T09:00:35Z INFO search: GET /api/items/35 200 47ms\n2026-03-14T09:00:36Z INFO search: GET /api/items/36 200 48ms\n2026-03-14T09:00:37Z INFO search: GET /api/items/37 200 49ms\n2026-03-14T09:00:38Z INFO search: GET /api/items/38 200 50ms\n2026-03-14T09:00:39Z INFO search: GET /api/items/39 200 51ms\n2026-03-14T09:00:40Z INFO search: GET /api/items/40 200 12ms\n2026-03-14T09:00:41Z INFO search: GET /api/items/41 200 13ms\n2026-03-14T09:00:42Z INFO search: GET /api/items/42 200 14ms\n2026-03-14T09:00:43Z INFO search: GET /api/items/43 200 15ms\n2026-03-14T09:00:44Z INFO search: GET /api/items/44 200 16ms\n2026-03-14T09:00:45Z INFO search: GET /api/items/45 200 17ms\n2026-03-14T09:00:46Z INFO search: GET /api/items/46 200 18ms\n2026-03-14T09:00:47Z INFO search: GET /api/items/47 200 19ms\n2026-03-14T09:00:48Z INFO search: GET /api/items/48 200 20ms\n2026-03-14T09:00:49Z INFO search: GET /api/items/49 200 21ms\n2026-03-14T09:00:50Z INFO search: GET /api/items/50 200 22ms\n2026-03-14T09:00:51Z INFO search: GET /api/items/51 200 23ms\n2026-03-14T09:00:52Z INFO search: GET /api/items/52 200 24ms\n2026-03-14T09:00:53Z INFO search: GET /api/items/53 200 25ms\n2026-03-14T09:00:54Z INFO search: GET /api/items/54 200 26ms\n2026-03-14T09:00:55Z INFO search: GET /api/items/55 200 27ms\n2026-03-14T09:00:56Z INFO search: GET /api/items/56 200 28ms\n2026-03-14T09:00:57Z INFO search: GET /api/items/57 200 29ms\n2026-03-14T09:00:58Z INFO search: GET /api/items/58 200 30ms\n2026-03-14T09:00:59Z INFO search: GET /api/items/59 200 31ms\n2026-03-14T09:01:00Z INFO search: GET /api/items/60 200 32ms\n2026-03-14T09:01:01Z INFO search: GET /api/items/61 200 33ms\n2026-03-14T09:01:02Z INFO search: GET /api/items/62 200 34ms\n2026-03-14T09:01:03Z INFO search: GET /api/items/63 200 35ms\n2026-03-14T09:01:04Z INFO search: GET /api/items/64 200 36ms\n2026-03-14T09:01:05Z INFO search: GET /api/items/65 200 37ms\n2026-03-14T09:01:06Z INFO search: GET /api/items/66 200 38ms\n2026-03-14T09:01:07Z INFO search: GET /api/items/67 200 39ms\n2026-03-14T09:01:08Z INFO search: GET /api/items/68 200 40ms\n2026-03-14T09:01:09Z INFO search: GET /api/items/69 200 41ms\n2026-03-14T09:01:10Z INFO search: GET /api/items/70 200 42ms\n2026-03-14T09:01:11Z INFO search: GET /api/items/71 200 43ms\n2026-03-14T09:01:12Z INFO search: GET /api/items/72 200 44ms\n2026-03-14T09:01:13Z INFO search: GET /api/items/73 200 45ms\n2026-03-14T09:01:14Z INFO search: GET /api/items/74 200 46ms\n2026-03-14T09:01:15Z INFO search: GET /api/items/75 200 47ms\n2026-03-14T09:01:16Z INFO search: GET /api/items/76 200 48ms\n2026-03-14T09:01:17Z INFO search: GET /api/items/77 200 49ms\n2026-03-14T09:01:18Z INFO search: GET /api/items/78 200 50ms\n2026-03-14T09:01:19Z INFO search: GET /api/items/79 200 51ms\n2026-03-14T09:01:20Z INFO search: GET /api/items/80 200 12ms\n2026-03-14T09:01:21Z INFO search: GET /api/items/81 200 13ms\n2026-03-14T09:01:22Z INFO search: GET /api/items/82 200 14ms\n2026-03-14T09:01:23Z INFO search: GET /api/items/83 200 15ms\n2026-03-14T09:01:24Z INFO search: GET /api/items/84 200 16ms\n2026-03-14T09:01:25Z INFO search: GET /api/items/85 200 17ms\n2026-03-14T09:01:26Z INFO search: GET /api/items/86 200 18ms\n2026-03-14T09:01:27Z INFO search: GET /api/items/87 200 19ms\n2026-03-14T09:01:28Z INFO search: GET /api/items/88 200 20ms\n2026-03-14T09:01:29Z INFO search: GET /api/items/89 200 21ms\n2026-03-14T09:01:30Z INFO search: GET /api/items/90 200 22ms\n2026-03-14T09:01:31Z INFO search: GET /api/items/91 200 23ms\n2026-03-14T09:01:32Z INFO search: GET /api/items/92 200 24ms\n2026-03-14T09:01:33Z INFO search: GET /api/items/93 200 25ms\n2026-03-14T09:01:34Z INFO search: GET /api/items/94 200 26ms\n2026-03-14T09:01:35Z INFO search: GET /api/items/95 200 27ms\n2026-03-14T09:01:36Z INFO search: GET /api/items/96 200 28ms\n2026-03-14T09:01:37Z INFO search: GET /api/items/97 200 29ms\n2026-03-14T09:01:38Z INFO search: GET /api/items/98 200 30ms\n2026-03-14T09:01:39Z INFO search: GET /api/items/99 200 31ms\n2026-03-14T09:01:40Z INFO search: GET /api/items/100 200 32ms\n2026-03-14T09:01:41Z INFO search: GET /api/items/101 200 33ms\n2026-03-14T09:01:42Z INFO search: GET /api/items/102 200 34ms\n2026-03-14T09:01:43Z INFO search: GET /api/items/103 200 35ms\n2026-03-14T09:01:44Z INFO search: GET /api/items/104 200 36ms\n2026-03-14T09:01:45Z INFO search: GET /api/items/105 200 37ms\n2026-03-14T09:01:46Z INFO search: GET /api/items/106 200 38ms\n2026-03-14T09:01:47Z INFO search: GET /api/items/107 200 39ms\n2026-03-14T09:01:48Z INFO search: GET /api/items/108 200 40ms\n2026-03-14T09:01:49Z INFO search: GET /api/items/109 200 41ms\n2026-03-14T09:01:50Z INFO search: GET /api/items/110 200 42ms\n2026-03-14T09:01:51Z INFO search: GET /api/items/111 200 43ms\n2026-03-14T09:01:52Z INFO search: GET /api/items/112 200 44ms\n2026-03-14T09:01:53Z INFO search: GET /api/items/113 200 45ms\n2026-03-14T09:01:54Z INFO search: GET /api/items/114 200 46ms\n2026-03-14T09:01:55Z INFO search: GET /api/items/115 200 47ms\n2026-03-14T09:01:56Z INFO search: GET /api/items/116 200 48ms\n2026-03-14T09:01:57Z INFO search: GET /api/items/117 200 49ms\n2026-03-14T09:01:58Z INFO search: GET /api/items/118 200 50ms\n2026-03-14T09:01:59Z INFO search: GET /api/items/119 200 51ms\n2026-03-14T09:02:00Z INFO search: GET /api/items/120 200 12ms\n2026-03-14T09:02:01Z INFO search: GET /api/items/121 200 13ms\n2026-03-14T09:02:02Z INFO search: GET /api/items/122 200 14ms\n2026-03-14T09:02:03Z INFO search: GET /api/items/123 200 15ms\n2026-03-14T09:02:04Z INFO search: GET /api/items/124 200 16ms\n2026-03-14T09:02:05Z INFO search: GET /api/items/125 200 17ms\n2026-03-14T09:02:06Z INFO search: GET /api/items/126 200 18ms\n2026-03-14T09:02:07Z INFO search: GET /api/items/127 200 19ms\n2026-03-14T09:02:08Z INFO search: GET /api/items/128 200 20ms\n2026-03-14T09:02:09Z INFO search: GET /api/items/129 200 21ms\n2026-03-14T09:02:10Z INFO search: GET /api/items/130 200 22ms\n2026-03-14T09:02:11Z INFO search: GET /api/items/131 200 23ms\n2026-03-14T09:02:12Z INFO search: GET /api/items/132 200 24ms\n2026-03-14T09:02:13Z INFO search: GET /api/items/133 200 25ms\n2026-03-14T09:02:14Z INFO search: GET /api/items/134 200 26ms\n2026-03-14T09:02:15Z INFO search: GET /api/items/135 200 27ms\n2026-03-14T09:02:16Z INFO search: GET /api/items/136 200 28ms\n2026-03-14T09:02:17Z INFO search: GET /api/items/137 200 29ms\n2026-03-14T09:02:18Z INFO search: GET /api/items/138 200 30ms\n2026-03-14T09:02:19Z INFO search: GET /api/items/139 200 31ms\n2026-03-14T09:02:20Z INFO search: GET /api/items/140 200 32ms\n2026-03-14T09:02:21Z INFO search: GET /api/items/141 200 33ms\n2026-03-14T09:02:22Z INFO search: GET /api/items/142 200 34ms\n2026-03-14T09:02:23Z INFO search: GET /api/items/143 200 35ms\n2026-03-14T09:02:24Z INFO search: GET /api/items/144 200 36ms\n2026-03-14T09:02:25Z INFO search: GET /api/items/145 200 37ms\n2026-03-14T09:02:26Z INFO search: GET /api/items/146 200 38ms\n2026-03-14T09:02:27Z INFO search: GET /api/items/147 200 39ms\n2026-03-14T09:02:28Z INFO search: GET /api/items/148 200 40ms\n2026-03-14T09:02:29Z INFO search: GET /api/items/149 200 41ms\n2026-03-14T09:02:30Z INFO search: GET /api/items/150 200 42ms\n2026-03-14T09:02:31Z INFO search: GET /api/items/151 200 43ms\n2026-03-14T09:02:32Z INFO search: GET /api/items/152 200 44ms\n2026-03-14T09:02:33Z INFO search: GET /api/items/153 200 45ms\n2026-03-14T09:02:34Z INFO search: GET /api/items/154 200 46ms\n2026-03-14T09:02:35Z INFO search: GET /api/items/155 200 47ms\n2026-03-14T09:02:36Z INFO search: GET /api/items/156 200 48ms\n2026-03-14T09:02:37Z INFO search: GET /api/items/157 200 49ms\n2026-03-14T09:02:38Z INFO search: GET /api/items/158 200 50ms\n2026-03-14T09:02:39Z INFO search: GET /api/items/159 200 51ms\n2026-03-14T09:02:40Z INFO search: GET /api/items/160 200 12ms\n2026-03-14T09:02:41Z INFO search: GET /api/items/161 200 13ms\n2026-03-14T09:02:42Z INFO search: GET /api/items/162 200 14ms\n2026-03-14T09:02:43Z INFO search: GET /api/items/163 200 15ms\n2026-03-14T09:02:44Z INFO search: GET /api/items/164 200 16ms\n2026-03-14T09:02:45Z INFO search: GET /api/items/165 200 17ms\n2026-03-14T09:02:46Z INFO search: GET /api/items/166 200 18ms\n2026-03-14T09:02:47Z INFO search: GET /api/items/167 200 19ms\n2026-03-14T09:02:48Z INFO search: GET /api/items/168 200 20ms\n2026-03-14T09:02:49Z INFO search: GET /api/items/169 200 21ms\n2026-03-14T09:02:50Z INFO search: GET /api/items/170 200 22ms\n2026-03-14T09:02:51Z INFO search: GET /api/items/171 200 23ms\n2026-03-14T09:02:52Z INFO search: GET /api/items/172 200 24ms\n2026-03-14T09:02:53Z INFO search: GET /api/items/173 200 25ms\n2026-03-14T09:02:54Z INFO search: GET /api/items/174 200 26ms\n2026-03-14T09:02:55Z INFO search: GET /api/items/175 200 27ms\n2026-03-14T09:02:56Z INFO search: GET /api/items/176 200 28ms\n2026-03-14T09:02:57Z INFO search: GET /api/items/177 200 29ms\n2026-03-14T09:02:58Z INFO search: GET /api/items/178 200 30ms\n2026-03-14T09:02:59Z INFO search: GET /api/items/179 200 31ms\n2026-03-14T09:03:00Z INFO search: GET /api/items/180 200 32ms\n2026-03-14T09:03:01Z INFO search: GET /api/items/181 200 33ms\n2026-03-14T09:03:02Z INFO search: GET /api/items/182 200 34ms\n2026-03-14T09:03:03Z INFO search: GET /api/items/183 200 35ms\n2026-03-14T09:03:04Z INFO search: GET /api/items/184 200 36ms\n2026-03-14T09:03:05Z INFO search: GET /api/items/185 200 37ms\n2026-03-14T09:03:06Z INFO search: GET /api/items/186 200 38ms\n2026-03-14T09:03:07Z INFO search: GET /api/items/187 200 39ms\n2026-03-14T09:03:08Z INFO search: GET /api/items/188 200 40ms\n2026-03-14T09:03:09Z INFO search: GET /api/items/189 200 41ms\n2026-03-14T09:03:10Z INFO search: GET /api/items/190 200 42ms\n2026-03-14T09:03:11Z INFO search: GET /api/items/191 200 43ms\n2026-03-14T09:03:12Z INFO search: GET /api/items/192 200 44ms\n2026-03-14T09:03:13Z INFO search: GET /api/items/193 200 45ms\n2026-03-14T09:03:14Z INFO search: GET /api/items/194 200 46ms\n2026-03-14T09:03:15Z INFO search: GET /api/items/195 200 47ms\n2026-03-14T09:03:16Z INFO search: GET /api/items/196 200 48ms\n2026-03-14T09:03:17Z INFO search: GET /api/items/197 200 49ms\n2026-03-14T09:03:18Z INFO search: GET /api/items/198 200 50ms\n2026-03-14T09:03:19Z INFO search: GET /api/items/199 200 51ms\n2026-03-14T09:03:20Z INFO search: GET /api/items/200 200 12ms\n2026-03-14T09:03:21Z INFO search: GET /api/items/201 200 13ms\n2026-03-14T09:03:22Z INFO search: GET /api/items/202 200 14ms\n2026-03-14T09:03:23Z INFO search: GET /api/items/203 200 15ms\n2026-03-14T09:03:24Z INFO search: GET /api/items/204 200 16ms\n2026-03-14T09:03:25Z INFO search: GET /api/items/205 200 17ms\n2026-03-14T09:03:26Z INFO search: GET /api/items/206 200 18ms\n2026-03-14T09:03:27Z INFO search: GET /api/items/207 200 19ms\n2026-03-14T09:03:28Z INFO search: GET /api/items/208 200 20ms\n2026-03-14T09:03:29Z INFO search: GET /api/items/209 200 21ms\n2026-03-14T09:03:30Z INFO search: GET /api/items/210 200 22ms\n2026-03-14T09:03:31Z INFO search: GET /api/items/211 200 23ms\n2026-03-14T09:03:32Z INFO search: GET /api/items/212 200 24ms\n2026-03-14T09:03:33Z INFO search: GET /api/items/213 200 25ms\n2026-03-14T09:03:34Z INFO search: GET /api/items/214 200 26ms\n2026-03-14T09:03:35Z INFO search: GET /api/items/215 200 27ms\n2026-03-14T09:03:36Z INFO search: GET /api/items/216 200 28ms\n2026-03-14T09:03:37Z INFO search: GET /api/items/217 200 29ms\n2026-03-14T09:03:38Z INFO search: GET /api/items/218 200 30ms\n2026-03-14T09:03:39Z INFO search: GET /api/items/219 200 31ms"
 }
]
EOF
```

## What to build

Write `/root/harness-lab/17-budget/measure.py`, used as `python measure.py HISTORY_FILE`. Import `SYSTEM` and `SCHEMAS` from your `agent.py`, then use `lab-mini` with `max_tokens=1` and read `usage.prompt_tokens` for four requests:

| Name | Messages | Tools |
|---|---|---|
| `base` | one user message `hi` | none |
| `with_system` | system, user `hi` | none |
| `with_tools` | system, user `hi` | `SCHEMAS` |
| `full` | system, then every message from HISTORY_FILE | `SCHEMAS` |

Print JSON:

```json
{"measurements": {"base": 0, "with_system": 0, "with_tools": 0, "full": 0},
 "parts": {"system": 0, "tools": 0, "history": 0},
 "biggest": "history"}
```

where `system = with_system - base`, `tools = with_tools - with_system`, `history = full - with_tools`, and `biggest` is the part with the most tokens.

```bash
cd /root/harness-lab/17-budget
python measure.py history.json | tee parts.json
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Pass `tools=` only when you have tools - `tools=None` isn't the same as leaving it out for every SDK version.
- `max(parts, key=parts.get)` picks the biggest part.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/17-budget
cat > measure.py <<'EOF'
import json
import sys
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).parent))
from agent import SCHEMAS, SYSTEM

client = OpenAI()


def tokens(messages, tools=None):
    kw = {"tools": tools} if tools else {}
    return client.chat.completions.create(model="lab-mini", max_tokens=1, messages=messages, **kw).usage.prompt_tokens


history = json.load(open(sys.argv[1]))
sys_msg = {"role": "system", "content": SYSTEM}
hi = {"role": "user", "content": "hi"}
m = {"base": tokens([hi]), "with_system": tokens([sys_msg, hi]), "with_tools": tokens([sys_msg, hi], SCHEMAS),
     "full": tokens([sys_msg] + history, SCHEMAS)}
parts = {"system": m["with_system"] - m["base"], "tools": m["with_tools"] - m["with_system"], "history": m["full"] - m["with_tools"]}
out = {"measurements": m, "parts": parts, "biggest": max(parts, key=parts.get)}
print(json.dumps(out, indent=2))

EOF
python measure.py history.json | tee parts.json
```

</details>

## Check your work

```bash
D=/root/harness-lab/17-budget; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/measure.py 2>/dev/null && [ -s $D/measure.py ] && echo "✅ measure.py reads the key from the environment" || echo "❌ measure.py must not contain a key - let the SDK read it from the environment"
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
sys.path.insert(0, ".")
from agent import SCHEMAS, SYSTEM
def T(msgs, tools=None):
    kw = {"tools": tools} if tools else {}
    return _C.chat.completions.create(model="lab-mini", max_tokens=1, messages=msgs, **kw).usage.prompt_tokens
def expect(hist):
    s, hi = {"role": "system", "content": SYSTEM}, {"role": "user", "content": "hi"}
    m = {"base": T([hi]), "with_system": T([s, hi]), "with_tools": T([s, hi], SCHEMAS), "full": T([s] + hist, SCHEMAS)}
    p = {"system": m["with_system"] - m["base"], "tools": m["with_tools"] - m["with_system"], "history": m["full"] - m["with_tools"]}
    return {"measurements": m, "parts": p, "biggest": max(p, key=p.get)}
got = load("parts.json")
ok(got == expect(json.load(open("history.json"))), "parts.json matches the real usage counts for every part", f"parts.json should be {expect(json.load(open('history.json')))} - got {got}"[:400])
ok(isinstance(got, dict) and got.get("biggest") == "history", "the history - with its big tool result - is the biggest part", f"biggest should be history - got {(got or {}).get('biggest')}")
h2 = [{"role": "user", "content": "Which port does billing use?"}]
Path("/tmp/h17.json").write_text(json.dumps(h2))
rc, out, err = run("measure.py", "/tmp/h17.json")
try:
    g2 = json.loads(out)
except ValueError:
    g2 = None
ok(g2 == expect(h2), "a different history is measured the same way", f"for a one-message history expected {expect(h2)} - got {out[:200]!r} {err[-150:]}")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")]
ok(any(x.get("model") == "lab-mini" and x.get("max_tokens") == 1 and x.get("tools") for x in rows), "measurements used lab-mini with max_tokens=1", "measure with lab-mini, max_tokens=1")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- System prompt, tool definitions and history all compete for the same window and budget.
- Measure each part by difference with max_tokens=1 and the real usage count.
- Tool results in the history are usually the biggest part - and the one to budget first.
