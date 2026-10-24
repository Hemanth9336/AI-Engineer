---
type: task
title: "Write a system prompt for a support agent harness"
minutes: 9
---

## Set up

`support_tools.py` has the support agent's three tools: `lookup_account`, `search_docs` and `create_ticket` (with stand-in data).

```bash
mkdir -p /root/harness-lab/16-system
cd /root/harness-lab/16-system
cat > support_tools.py <<'EOF'
SCHEMAS = [
    {"type": "function", "function": {"name": "lookup_account", "description": "Look up a Stackline customer account by email: plan, status, open invoices.",
     "parameters": {"type": "object", "properties": {"email": {"type": "string"}}, "required": ["email"]}}},
    {"type": "function", "function": {"name": "search_docs", "description": "Search Stackline's public help center articles.",
     "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "create_ticket", "description": "Open a ticket for the human support team, with a summary.",
     "parameters": {"type": "object", "properties": {"email": {"type": "string"}, "summary": {"type": "string"}}, "required": ["email", "summary"]}}},
]


def lookup_account(email):
    return {"email": email, "plan": "pro", "status": "active", "open_invoices": 1}


def search_docs(query):
    return "Help center: 'Changing your plan' - plans can be changed any time from Settings > Billing; changes apply at the next invoice."


def create_ticket(email, summary):
    return {"ticket": "SUP-4821", "email": email, "summary": summary}


IMPL = {"lookup_account": lookup_account, "search_docs": search_docs, "create_ticket": create_ticket}
EOF
```

## What to build

1. Write `/root/harness-lab/16-system/system_prompt.md` for Stackline's customer support agent, with these five `##` sections, in this order: `## Role`, `## Tools`, `## Rules`, `## When you're stuck`, `## Answer format`.
   - **Tools** says when to use each of `lookup_account`, `search_docs` and `create_ticket`.
   - **Rules** includes: ask for the account email before looking anything up; never promise a **refund** (open a ticket instead); never reveal **another customer**'s data.
   - **When you're stuck** says to open a ticket rather than guess.
   - 150 to 600 words in total.
2. Write `agent.py`: the agent loop (with a step limit) using the tools from `support_tools.py` and the **exact contents** of `system_prompt.md` as the system message.

```bash
cd /root/harness-lab/16-system
python agent.py "Hi, I'm jo@harbor.example. Can I get a refund for last month?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `SYSTEM = (Path(__file__).parent / "system_prompt.md").read_text()` - no copying the text into code.
- Return tool results as `json.dumps(...)` strings.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/16-system
cat > system_prompt.md <<'EOF'
# Stackline support agent

## Role
You are the support agent for Stackline, a cloud hosting company. You help customers with their account, plans and billing questions in a chat window.

## Tools
- Use `lookup_account` whenever a question is about the customer's own account, plan or invoices. You need their account email first.
- Use `search_docs` for how-to questions; answer from the article and name it.
- Use `create_ticket` when the customer needs something you can't do: refunds, billing disputes, outages, or account deletion.

## Rules
- Ask for the account email if the customer hasn't given it, before looking anything up.
- Never promise or issue a refund; refunds are decided by the billing team, so open a ticket instead.
- Only discuss the account of the email the customer gave you. Never reveal another customer's data.
- Don't guess prices or policies; look them up with search_docs, or say you don't know.

## When you're stuck
If the tools can't answer the question after two tries, open a ticket with a clear summary and tell the customer a human will reply within one business day.

## Answer format
Reply in at most four short sentences, in plain text. When you open a ticket, include the ticket number.

EOF
cat > agent.py <<'EOF'
import json
import sys
from pathlib import Path

from openai import OpenAI

from support_tools import IMPL, SCHEMAS

SYSTEM = (Path(__file__).parent / "system_prompt.md").read_text()

def run_tool(name, args):
    if name not in IMPL:
        return f"error: unknown tool {name}"
    try:
        return json.dumps(IMPL[name](**args))
    except Exception as e:
        return f"error: {type(e).__name__}: {e}"


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
python agent.py "Hi, I'm jo@harbor.example. Can I get a refund for last month?"
```

</details>

## Check your work

```bash
D=/root/harness-lab/16-system; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/agent.py 2>/dev/null && [ -s $D/agent.py ] && echo "✅ agent.py reads the key from the environment" || echo "❌ agent.py must not contain a key - let the SDK read it from the environment"
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
import re
text = Path("system_prompt.md").read_text() if Path("system_prompt.md").exists() else ""
heads = re.findall(r"^## (.+?)\s*$", text, re.M)
ok(heads == ["Role", "Tools", "Rules", "When you're stuck", "Answer format"], "system_prompt.md has the five sections in order", f"expected ## Role, Tools, Rules, When you're stuck, Answer format - got {heads}")
words = len(text.split())
ok(150 <= words <= 600, f"the prompt is a focused {words} words", f"the prompt should be 150-600 words - it is {words}")
def section(name):
    m = re.search(r"^## " + re.escape(name) + r"\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1).lower() if m else ""
tools = section("Tools")
ok(all(t in tools for t in ("lookup_account", "search_docs", "create_ticket")), "the Tools section covers all three tools", "## Tools should say when to use lookup_account, search_docs and create_ticket")
rules_ = section("Rules")
ok("email" in rules_ and "refund" in rules_ and "another customer" in rules_, "the Rules cover the email, refund and privacy rules", "## Rules should mention asking for the email, refunds, and another customer's data")
ok("ticket" in section("When you're stuck"), "When you're stuck says to open a ticket", "## When you're stuck should send the agent to create_ticket instead of guessing")
ok(not re.search(r"sk-[A-Za-z0-9_-]{8,}|password\s*[:=]", text, re.I), "no secrets in the prompt", "the system prompt must not contain keys or passwords")
with MockModel([{"tool": "lookup_account", "args": {"email": "jo@harbor.example"}}, {"tool": "create_ticket", "args": {"email": "jo@harbor.example", "summary": "Refund request"}}, "I've opened ticket SUP-4821 for the billing team."]) as m:
    rc, out, err = m.run(["python", "agent.py", "Refund please, jo@harbor.example"], timeout=30)
first = (m.requests[0]["messages"][0] if m.requests else {})
ok(rc == 0 and first.get("role") == "system" and first.get("content") == text, "agent.py sends system_prompt.md, unchanged, as the system message", f"the first message of each request should be the exact file contents - got {str(first)[:120]} {err[-200:]}")
names = sorted(((t.get("function") or {}).get("name")) for t in (m.requests[0].get("tools") or [])) if m.requests else []
res = [x.get("content", "") for x in (m.requests[-1]["messages"] if m.requests else []) if x.get("role") == "tool"]
ok(names == ["create_ticket", "lookup_account", "search_docs"] and len(res) == 2 and "SUP-4821" in res[1] and out.endswith("SUP-4821 for the billing team."), "the loop runs the support tools and answers", f"tools {names}, results {[r[:60] for r in res]}, answer {out[-120:]!r}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A system prompt has a role, a tool policy, rules with reasons, a when-stuck plan and an answer format.
- Secrets, big documents and per-user data don't belong in it.
- Keep it in a file the harness loads, so it can be reviewed, versioned and tested.
