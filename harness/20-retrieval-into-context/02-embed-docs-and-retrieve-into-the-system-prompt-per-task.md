---
type: task
title: "Embed docs and retrieve into the system prompt per task"
minutes: 11
---

## Set up

`docs/` has eight of Stackline's runbooks: deploys, rollback, on-call, billing, search, certificates, backups and production access.

```bash
mkdir -p /root/harness-lab/20-retrieval/workspace/services
cd /root/harness-lab/20-retrieval
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
mkdir -p docs
cat > docs/deploys.md <<'EOF'
# Deploying a service
Deploy with `stackctl deploy <service>`. Deploys run a canary on 5% of traffic for ten minutes before rolling out. Deploys are frozen on Fridays after 15:00.
EOF
cat > docs/rollback.md <<'EOF'
# Rolling back a bad release
If a release breaks something, undo it with `stackctl rollback <service> --to <version>`. Rollbacks skip the canary and finish in about two minutes. Open an incident ticket afterwards.
EOF
cat > docs/oncall.md <<'EOF'
# On-call
Each team has a weekly on-call rotation, handed over on Mondays at 10:00. Pages come from PagerDuty; acknowledge within 5 minutes or the page escalates to the team lead.
EOF
cat > docs/billing-service.md <<'EOF'
# Billing service
The billing service listens on port 8081 and generates invoices nightly at 02:00 UTC. It is owned by the payments team.
EOF
cat > docs/search-service.md <<'EOF'
# Search service
The search service runs on an Elasticsearch cluster on port 9200. A full reindex takes about 40 minutes and is run with `stackctl reindex search`.
EOF
cat > docs/certificates.md <<'EOF'
# TLS certificates
TLS certificates renew automatically 30 days before they expire. If renewal fails, an alert fires in #infra-alerts and the certificate can be renewed by hand with `stackctl certs renew <domain>`.
EOF
cat > docs/backups.md <<'EOF'
# Database backups
Databases are backed up every 6 hours. Backups are retained for 14 days. Restore with `stackctl restore <db> --at <time>`.
EOF
cat > docs/access.md <<'EOF'
# Production access
To get production access, open an ACCESS ticket. Your team lead approves it, and access expires automatically after 8 hours.
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

1. Write `/root/harness-lab/20-retrieval/retrieve.py`:
   - `python retrieve.py build` embeds every `docs/*.md` with **`lab-embed`** and writes `index.json`: a list of `{"name": "<file name>", "vector": [...]}`.
   - `top_k(question, k=2)` embeds the question and returns the names of the `k` most similar docs (cosine similarity), best first.
2. In `agent.py`, add `build_system(question)` that returns `SYSTEM + "\n\n## Relevant docs\n"` followed by the top 2 docs, each as `### <name>\n<contents>`, separated by a blank line. Use it as the system message for each run.

```bash
cd /root/harness-lab/20-retrieval
python retrieve.py build
python retrieve.py "How do I undo a bad release of search?"
python agent.py "How long are database backups kept?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Embed all docs in one `client.embeddings.create(input=[...])` call.
- Index once; `top_k` should only embed the question.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/20-retrieval
cat > retrieve.py <<'EOF'
"""Embed the runbooks once, then find the most relevant ones for a question.

python retrieve.py build        # embed docs/*.md into index.json
python retrieve.py "question"   # print the top 2 doc names
"""
import json
import math
import sys
from pathlib import Path

from openai import OpenAI

HERE = Path(__file__).parent
DOCS = HERE / "docs"
INDEX = HERE / "index.json"
client = OpenAI()


def embed(texts):
    return [d.embedding for d in client.embeddings.create(model="lab-embed", input=texts).data]


def cos(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def build():
    files = sorted(DOCS.glob("*.md"))
    vectors = embed([f.read_text() for f in files])
    INDEX.write_text(json.dumps([{"name": f.name, "vector": v} for f, v in zip(files, vectors)]))
    return len(files)


def top_k(question, k=2):
    index = json.loads(INDEX.read_text())
    q = embed([question])[0]
    return [d["name"] for d in sorted(index, key=lambda d: -cos(q, d["vector"]))[:k]]


if __name__ == "__main__":
    if sys.argv[1:] == ["build"]:
        print(f"indexed {build()} docs")
    else:
        print(top_k(" ".join(sys.argv[1:])))

EOF
cat > agent.py <<'EOF'
import json
import sys
from pathlib import Path

from openai import OpenAI

from retrieve import DOCS, top_k

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



def build_system(question):
    docs = "\n\n".join(f"### {name}\n{(DOCS / name).read_text().strip()}" for name in top_k(question))
    return f"{SYSTEM}\n\n## Relevant docs\n{docs}"


def run(question, max_steps=8):
    client = OpenAI()
    messages = [{"role": "system", "content": build_system(question)}, {"role": "user", "content": question}]
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
python retrieve.py build
python retrieve.py "How do I undo a bad release of search?"
python agent.py "How long are database backups kept?"
```

</details>

## Check your work

```bash
D=/root/harness-lab/20-retrieval; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/retrieve.py 2>/dev/null && [ -s $D/retrieve.py ] && echo "✅ retrieve.py reads the key from the environment" || echo "❌ retrieve.py must not contain a key - let the SDK read it from the environment"
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
sys.path.insert(0, ".")
idx = load("index.json") or []
names = sorted(d.get("name") for d in idx) if isinstance(idx, list) else []
ok(names == sorted(p.name for p in Path("docs").glob("*.md")) and all(len(d.get("vector") or []) == 384 for d in idx), "index.json has a 384-dimension lab-embed vector for each of the 8 docs", f"index.json names {names}")
if names:
    v = next(d["vector"] for d in idx if d["name"] == "backups.md")
    ref = E([Path("docs/backups.md").read_text()])[0]
    ok(cos(v, ref) > 0.99, "the stored vectors are real lab-embed embeddings of the doc text", f"backups.md's vector doesn't match lab-embed of its text (cosine {cos(v, ref):.2f})")
try:
    from retrieve import top_k
    cases = {"How do I undo a bad release of search?": "rollback.md", "When do TLS certificates get renewed?": "certificates.md",
             "How long are database backups kept?": "backups.md", "Who approves production access?": "access.md"}
    got = {q: top_k(q) for q in cases}
    ok(all(isinstance(g, list) and len(g) == 2 for g in got.values()) and all(got[q][0] == want for q, want in cases.items()), "top_k returns the 2 best docs, and the right runbook comes first", f"got {got}")
    import agent
    s = agent.build_system("How long are database backups kept?")
    heads = re.findall(r"^### (.+)$", s, re.M)
    ok(s.startswith(agent.SYSTEM + "\n\n## Relevant docs\n### ") and len(heads) == 2 and heads[0] == "backups.md" and "retained for 14 days" in s and "TLS certificates renew" not in s,
       "build_system puts the rules first, then exactly the top 2 docs", f"headers {heads}; starts {s[:80]!r}")
except Exception as e:
    ok(False, "", f"retrieve.top_k and agent.build_system should both work - {type(e).__name__}: {e}")
PYEOF
jq -se 'any(.[]; .ok and .api == "embeddings" and .model == "lab-embed" and (.client | startswith("OpenAI/Python")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-embed calls" || echo "❌ no lab-embed call from your scripts in the gateway log"
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")) and .system)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the agent answered with the retrieved docs in its system prompt" || echo "❌ run agent.py with a question - no lab-fast call with a system prompt in the gateway log"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Retrieval puts only the docs this task needs into context, instead of every doc on every step.
- Index once; embed the task and take a small top-k per run.
- Put retrieved text in a clearly labelled section, separate from the rules.
