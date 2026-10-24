---
type: task
title: "Project: Docs Q&A Bot"
minutes: 60
---

## Scenario

Pulse is a small open-source monitoring tool. Its docs live in a `docs/` folder split into `getting-started/`, `guides/` and `reference/`, and the same questions keep landing in the community chat: *how do I send alerts to Slack? what port is the dashboard on?* Build a bot that answers them from the docs, shows which pages it used, admits when the docs don't say, and picks up new pages when someone adds them.

This project puts everything from topics 03-13 together. There's no new lesson: pick the pieces you like - your own functions, Chroma, LangChain's splitter - and build it.

## Set up

```bash
ailab status
mkdir -p /root/rag-lab/14-docs-bot /root/answers
cd /root/rag-lab/14-docs-bot
mkdir -p docs/getting-started
cat > docs/getting-started/install.md <<'EOF'
# Installing Pulse
Pulse runs on Linux and macOS. Install it with: curl -fsSL https://get.pulse.example | sh
After installing, run pulse init in your project folder to create pulse.yaml.

## System requirements
Pulse needs 2 GB of memory and Python 3.10 or newer.
EOF
mkdir -p docs/getting-started
cat > docs/getting-started/first-check.md <<'EOF'
# Your first health check
Add a check to pulse.yaml under checks, with a name, a url and an interval. The default interval is 60 seconds.
Run pulse check --once to try every check a single time without starting the scheduler.
EOF
mkdir -p docs/guides
cat > docs/guides/alerts.md <<'EOF'
# Alerts
Pulse sends an alert after three failed checks in a row. Alerts can go to Slack, email or PagerDuty.
To send alerts to Slack, set slack_webhook in pulse.yaml to your incoming webhook URL.

## Quiet hours
Set quiet_hours to a time range such as 22:00-07:00 to hold non-critical alerts until the morning.
EOF
mkdir -p docs/guides
cat > docs/guides/dashboards.md <<'EOF'
# Dashboards
Run pulse dashboard to open the web dashboard on port 9400. The dashboard keeps 14 days of history.
EOF
mkdir -p docs/reference
cat > docs/reference/cli.md <<'EOF'
# Command reference
pulse init creates pulse.yaml. pulse check --once runs every check once. pulse status prints the state of every check.
pulse upgrade installs the latest release.
EOF
mkdir -p docs/reference
cat > docs/reference/config.md <<'EOF'
# Configuration reference
pulse.yaml lives in the project root. The retries setting controls how many times a failed check is retried before it counts as failed; the default is 2.
The timeout setting is in seconds and defaults to 10.
EOF
find docs -name '*.md' | sort
```

## What to build

Write `/root/rag-lab/14-docs-bot/docsbot.py` with two commands.

**`python docsbot.py index`**

- Finds every `.md` file under `docs/` **including subfolders**.
- Chunks each file (any sensible chunker - LangChain's `RecursiveCharacterTextSplitter` with 500/100 works well), embeds with `lab-embed`, and stores the chunks in a vector store under `/root/rag-lab/14-docs-bot/` with their **source**: the path relative to `docs/`, like `guides/alerts.md`.
- Is idempotent: running it again without changes leaves the same number of chunks.
- Picks up **new files**: add a page, run `index`, and the bot can answer from it.
- Prints `N chunks indexed`, where N is the total number of chunks in the store.

**`python docsbot.py ask QUESTION...`**

- Retrieves the top 3 chunks and answers with `lab-fast` at `temperature=0`, using only those chunks.
- Prints the answer, a blank line, and `Sources: ` with the retrieved source paths, comma-separated, best first, no repeats.
- When the docs don't contain the answer, prints exactly `I don't know based on the docs.` and nothing else.
- No key or URL in the code.

Then run:

```bash
python docsbot.py index
python docsbot.py ask "How do I send alerts to Slack?" > /root/answers/14-slack.txt
python docsbot.py ask "How much does Pulse cost?" > /root/answers/14-cost.txt
```

The checker asks new questions, re-indexes, and adds a page of its own to `docs/guides/`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `Path("docs").rglob("*.md")` finds files in subfolders; `path.relative_to("docs").as_posix()` gives `guides/alerts.md`.
- Make chunk IDs from the source and the chunk number (`guides/alerts.md#0`) so re-indexing upserts the same IDs.
- Topic 11's `rag_chroma.py` is a good starting point - change the glob, the IDs, the refusal and the output.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-lab/14-docs-bot
cat > docsbot.py <<'EOF'
import os
import sys
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI

HERE = Path(__file__).resolve().parent
DOCS = HERE / "docs"
REFUSAL = "I don't know based on the docs."
client = OpenAI()
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
embed = OpenAIEmbeddingFunction(
    api_key_env_var="OPENAI_API_KEY", api_base=os.environ["OPENAI_BASE_URL"], model_name="lab-embed"
)
collection = chromadb.PersistentClient(path=str(HERE / "db")).get_or_create_collection(
    "pulse-docs", embedding_function=embed, configuration={"hnsw": {"space": "cosine"}}
)


def index():
    ids, texts, metas = [], [], []
    for path in sorted(DOCS.rglob("*.md")):
        source = path.relative_to(DOCS).as_posix()
        for i, text in enumerate(splitter.split_text(path.read_text())):
            ids.append(f"{source}#{i}")
            texts.append(text)
            metas.append({"source": source, "index": i})
    collection.upsert(ids=ids, documents=texts, metadatas=metas)
    return collection.count()


def ask(question, k=3):
    res = collection.query(query_texts=[question], n_results=k)
    hits = list(zip(res["documents"][0], res["metadatas"][0]))
    context = "\n\n".join(f'<document source="{m["source"]}">\n{d}\n</document>' for d, m in hits)
    system = (
        "You answer questions about the Pulse monitoring tool using only the documentation below. "
        f"If it does not contain the answer, reply exactly: {REFUSAL}\n\n{context}"
    )
    resp = client.chat.completions.create(
        model="lab-fast",
        temperature=0,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": question}],
    )
    text = resp.choices[0].message.content.strip()
    if "don't know based on the docs" in text.lower():
        return REFUSAL, []
    return text, list(dict.fromkeys(m["source"] for _, m in hits))


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "index":
        print(f"{index()} chunks indexed")
    elif len(sys.argv) >= 3 and sys.argv[1] == "ask":
        text, sources = ask(" ".join(sys.argv[2:]))
        print(text)
        if sources:
            print()
            print("Sources: " + ", ".join(sources))
    else:
        print("usage: docsbot.py index | docsbot.py ask QUESTION", file=sys.stderr)
        sys.exit(2)
EOF
python docsbot.py index
python docsbot.py ask "How do I send alerts to Slack?" > /root/answers/14-slack.txt
python docsbot.py ask "How much does Pulse cost?" > /root/answers/14-cost.txt
cat /root/answers/14-slack.txt /root/answers/14-cost.txt
```

</details>

## Check your work

```bash
D=/root/rag-lab/14-docs-bot; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/docsbot.py 2>/dev/null && [ -s $D/docsbot.py ] && echo "✅ docsbot.py reads the key from the environment" || echo "❌ docsbot.py must not contain a key - let the SDK read it from the environment"
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
import re
REFUSAL = "I don't know based on the docs."
B = "/root/rag-lab/14-docs-bot/docsbot.py"
def parts(out):
    body, sep, src = out.rpartition("Sources:")
    return (body.strip(), [s.strip() for s in src.split(",")]) if sep else (out.strip(), [])
def count(out):
    m = re.search(r"(\d+) chunks indexed", out)
    return int(m.group(1)) if m else None
a, s = parts(Path("/root/answers/14-slack.txt").read_text() if Path("/root/answers/14-slack.txt").exists() else "")
ok("slack_webhook" in a and s[:1] == ["guides/alerts.md"], "14-slack.txt answers from guides/alerts.md", "/root/answers/14-slack.txt should explain slack_webhook and list guides/alerts.md first in Sources")
ok(Path("/root/answers/14-cost.txt").exists() and Path("/root/answers/14-cost.txt").read_text().strip() == REFUSAL, "14-cost.txt is exactly the refusal", f"/root/answers/14-cost.txt should be exactly: {REFUSAL}")
import shutil
for db in Path("/root/rag-lab/14-docs-bot").rglob("chroma.sqlite3"):
    if db.parent != Path("/root/rag-lab/14-docs-bot"):
        shutil.rmtree(db.parent, ignore_errors=True)
rc1, o1, e1 = run(B, "index")
rc2, o2, e2 = run(B, "index")
n1, n2 = count(o1), count(o2)
ok(rc1 == rc2 == 0 and n1 is not None and n1 == n2 and n1 >= 6, f"index is idempotent ({n1} chunks both times)", f"python docsbot.py index twice should print the same 'N chunks indexed' - got {o1!r}, {o2!r} {e2[-150:]}")
for q, want, src in [("What port does the dashboard use?", "9400", "guides/dashboards.md"), ("How do I install Pulse?", "get.pulse.example", "getting-started/install.md")]:
    rc, out, err = run(B, "ask", q)
    a, s = parts(out)
    ok(rc == 0 and want in a and s[:1] == [src] and len(s) == len(set(s)) <= 3, f"'{q}' -> answered from {src}", f"'{q}' should be answered from {src} - got {out[-250:]!r} {err[-150:]}")
new = Path("/root/rag-lab/14-docs-bot/docs/guides/maintenance.md")
new.write_text("# Maintenance windows\nRun pulse pause --for 2h to silence all checks during planned maintenance. Checks resume automatically when the time is up.\n")
rc, out, err = run(B, "index")
n3 = count(out)
ok(rc == 0 and n1 is not None and n3 is not None and n3 > n1, "a new page is picked up by index", f"after adding docs/guides/maintenance.md, index should report more chunks than {n1} - got {out!r}")
rc, out, err = run(B, "ask", "How do I silence checks during planned maintenance?")
a, s = parts(out)
ok("pulse pause" in a and s[:1] == ["guides/maintenance.md"], "the bot answers from the new page", f"the new page should answer 'How do I silence checks during planned maintenance?' with Sources starting guides/maintenance.md - got {out[-250:]!r}")
rc, out, err = run(B, "ask", "Is there a mobile app for Pulse?")
ok(rc == 0 and out.strip() == REFUSAL, "an uncovered question gets exactly the refusal", f"'Is there a mobile app for Pulse?' should print only: {REFUSAL} - got {out[-200:]!r}")
new.unlink()
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A real docs bot: recursive file discovery, relative-path sources, idempotent re-indexing.
- Stable chunk IDs (source + number) make re-indexing an upsert, so new pages just appear.
- Answers carry sources; uncovered questions get the exact refusal.
