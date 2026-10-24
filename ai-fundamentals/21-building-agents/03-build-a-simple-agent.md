---
type: task
title: "Build a simple agent"
minutes: 13
---

## Scenario

On-call wants to ask "which host is about to run out of disk?" in plain English and get an answer based on live numbers, not a guess. Build a small read-only agent with LangChain.

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/21-agent
cd /root/ai-lab/21-agent
cat > disks.json <<'EOF'
{"web-01": "41%", "web-02": "38%", "db-01": "67%", "db-02": "94%", "cache-01": "22%"}
EOF
```

## What to build

Write `/root/ai-lab/21-agent/agent.py` that:

1. Defines a tool with `@tool` named `list_disk_usage` that takes no arguments, returns the contents of `/root/ai-lab/21-agent/disks.json`, and appends a line `tool=list_disk_usage` to `/root/ai-lab/21-agent/agent-tools.log` every time it runs. Give it a clear docstring.
2. Creates an agent with `create_agent`, using `ChatOpenAI(model="lab-fast", ...)` pointed at the gateway, the tool, and a system prompt telling it to use the tool for live data and never guess.
3. Answers the question given on the command line and prints only the final answer.

Run it:

```bash
python agent.py "Which host is almost out of disk space?" > answer.txt
```

The answer must name **db-02**.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `from langchain.agents import create_agent` and `from langchain_core.tools import tool`.
- `create_agent(llm, tools=[list_disk_usage], system_prompt="...")`
- `result["messages"][-1].content` is the final answer.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/21-agent
cat > agent.py <<'EOF'
import os
import sys
from pathlib import Path

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

HERE = Path("/root/ai-lab/21-agent")


@tool
def list_disk_usage() -> str:
    """Return the current disk usage of every host as JSON, e.g. {"web-01": "41%"}."""
    with open(HERE / "agent-tools.log", "a") as f:
        f.write("tool=list_disk_usage\n")
    return (HERE / "disks.json").read_text()


llm = ChatOpenAI(model="lab-fast", base_url=os.environ["OPENAI_BASE_URL"], api_key=os.environ["OPENAI_API_KEY"])
agent = create_agent(
    llm,
    tools=[list_disk_usage],
    system_prompt="You are an on-call assistant. Always use your tools for live data and never guess numbers.",
)

result = agent.invoke({"messages": [{"role": "user", "content": " ".join(sys.argv[1:])}]}, {"recursion_limit": 10})
print(result["messages"][-1].content)
EOF
python agent.py "Which host is almost out of disk space?" > answer.txt
cat answer.txt agent-tools.log
```

</details>

## Check your work

```bash
D=/root/ai-lab/21-agent; P=$D/agent.py
grep -q 'create_agent' $P 2>/dev/null && grep -q '@tool' $P && echo "✅ agent.py uses create_agent and an @tool function" || echo "❌ build the agent with create_agent and define the tool with @tool"
grep -q 'def list_disk_usage' $P 2>/dev/null && echo "✅ it defines list_disk_usage" || echo "❌ name the tool function list_disk_usage"
grep -q 'lab-fast' $P 2>/dev/null && grep -q 'OPENAI_BASE_URL' $P && echo "✅ the agent's model is lab-fast via the gateway" || echo "❌ use ChatOpenAI(model=\"lab-fast\", base_url=os.environ[\"OPENAI_BASE_URL\"], ...)"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $P 2>/dev/null && [ -s $P ] && echo "✅ $P reads the key from the environment" || echo "❌ $P must not contain a key - let the SDK read it from the environment"
grep -q 'db-02' $D/answer.txt 2>/dev/null && echo "✅ answer.txt names db-02" || echo "❌ answer.txt should name db-02, the host at 94%"
grep -qx 'tool=list_disk_usage' $D/agent-tools.log 2>/dev/null && echo "✅ agent-tools.log recorded the tool call" || echo "❌ the tool should append tool=list_disk_usage to agent-tools.log"
N0=$(grep -c . $D/agent-tools.log 2>/dev/null || echo 0); (cd $D && python $P "Which host is almost out of disk space?" > $D/.out 2>/dev/null); N1=$(grep -c . $D/agent-tools.log 2>/dev/null || echo 0)
[ "$N1" -gt "$N0" ] && grep -q 'db-02' $D/.out && echo "✅ a fresh run calls the tool again and answers db-02" || echo "❌ running agent.py again should call the tool and name db-02"
rm -f $D/.out
jq -se 'any(.[]; .ok and (.tool_calls | index("list_disk_usage")) and (.tools | index("list_disk_usage")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway saw the model call list_disk_usage" || echo "❌ the gateway has no list_disk_usage tool call yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- `create_agent` runs the tool loop: the model decides when to call your tools.
- `@tool` turns a function into a tool; its docstring is what the model reads.
- Log every tool call - it is your audit trail for what the agent did.
