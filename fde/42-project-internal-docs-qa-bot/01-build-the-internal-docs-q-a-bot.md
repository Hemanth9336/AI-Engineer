---
type: task
title: "Build the internal docs Q&A bot"
minutes: 60
---

## Scenario

Meridian Logistics' HR team answers the same questions every week: holidays, expenses, sick leave, laptops. They've exported the employee handbook from Confluence and want an internal assistant that answers staff questions **with citations**, and says so when the handbook doesn't cover something.

The export is messy: page footers, "CONFIDENTIAL" banners, editor stamps, HTML entities, an empty section. Your job is to turn it into a clean index and build the bot on top - using what you've learned about chunking (topic 16), grounding and citations (topic 18) and abstaining (topic 32).

## Set up

`handbook.md` is the raw Confluence export of the employee handbook.

```bash
mkdir -p /root/fde-lab/42-docs-bot
cd /root/fde-lab/42-docs-bot
cat > handbook.md <<'EOF'
<!-- exported from Confluence space HR -->
# Meridian Logistics Employee Handbook
CONFIDENTIAL - INTERNAL USE ONLY

## Working hours
Core hours are 10:00 to 15:00, Monday to Friday. You can start any time between 07:00 and 10:00.
Page 1 of 6
Overtime must be agreed with your manager in advance.

## Holidays
Full-time staff get 26 days of holiday a year plus public holidays.
Request holidays in the HR portal at least 4 weeks ahead.
Last edited by j.smith on 2025-11-02
You can carry over at most 5 unused days, to be used by 31 March.

## Sick leave
Call your manager before 09:00 on the first day you are ill.


A doctor&#39;s note is needed from the 4th day of absence.
Page 2 of 6

## Expenses
Submit expenses in Expensify within 30 days. The hotel limit is 140 EUR per night.
CONFIDENTIAL - INTERNAL USE ONLY
Expenses above 500 EUR need your manager&#39;s approval before you book.

## Remote work
You can work from home up to 2 days a week once you have passed your first 3 months.
Agree your home days with your team lead.

## Company cars
CONFIDENTIAL - INTERNAL USE ONLY
Page 3 of 6

## Equipment
Laptops are replaced every 3 years. Report a lost or stolen laptop to IT within 24 hours at it-help@meridian.example.
R&amp;D staff can request a second monitor.
Last edited by a.khan on 2026-01-15

## Training budget
Every employee has a training budget of 1,500 EUR a year. Agree courses with your manager first.
Page 4 of 6
EOF
```

## What to build

**1. `ingest.py`** - used as `python ingest.py handbook.md index.json`:

- Split the document into chunks at `## ` headings (ignore anything before the first one). The heading text is the chunk's `section`.
- Clean each section's lines: strip whitespace, `html.unescape`, and drop empty lines and boilerplate - lines matching `^CONFIDENTIAL\b`, `^Page \d+ of \d+$`, `^Last edited by ` or `^<!--.*-->$` (case-insensitive).
- **Skip** sections with nothing left. Number the rest `s01`, `s02`... in order. `text` is the cleaned lines joined with single spaces.
- Embed every chunk as `"<section>. <text>"` with `lab-embed` in **one** call, and write `index.json`: a list of `{"id", "section", "text", "vector"}`.
- Print `N chunks: s01 Working hours, ...`.

**2. `ask.py`** - used as `python ask.py QUESTION`, loading `index.json` next to the script:

- Embed the question, take the top 3 chunks by cosine similarity, and keep those scoring at least **0.3**. If none are left, return the refusal **without a chat call**.
- Otherwise call `lab-fast` at `temperature=0` in JSON mode. The system prompt is followed by the sources as `[s02] Holidays. text` lines:
  ```text
  You answer Meridian employees' questions from the employee handbook. Use only the sections below and cite section ids like [s02]. If they don't answer the question, the answer must be exactly: I don't know based on the provided sources. Reply with JSON: {"answer": "...", "citations": ["s02"]}
  ```
- Validate: keep only citations that are among the sources; a refusal has no citations; a non-refusal with no valid citation becomes the refusal.
- Print `{"answer": ..., "citations": [...], "sources": [ids sent]}`.

```bash
cd /root/fde-lab/42-docs-bot
python ingest.py handbook.md index.json
python ask.py "How many holiday days do I get?"
python ask.py "How much is the company car allowance?"
python ask.py "What's the weather in Rotterdam?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Look at the raw file first: `cat -A handbook.md | head -40` shows the blank lines and footers you need to drop.
- The 'Company cars' section contains only boilerplate - after cleaning it's empty, so it gets no id.
- Compute each chunk's score once and reuse it for ranking and the threshold.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/42-docs-bot
cat > ingest.py <<'EOF'
import html
import json
import re
import sys

from openai import OpenAI

BOILERPLATE = [r"^CONFIDENTIAL\b", r"^Page \d+ of \d+$", r"^Last edited by ", r"^<!--.*-->$"]


def clean_lines(lines):
    out = []
    for line in lines:
        line = html.unescape(line.strip())
        if not line or any(re.search(p, line, re.I) for p in BOILERPLATE):
            continue
        out.append(line)
    return out


def chunk(markdown):
    sections, current = [], None
    for line in markdown.splitlines():
        if line.startswith("## "):
            current = {"section": line[3:].strip(), "lines": []}
            sections.append(current)
        elif current is not None:
            current["lines"].append(line)
    chunks = []
    for s in sections:
        body = clean_lines(s["lines"])
        if body:
            chunks.append({"id": f"s{len(chunks) + 1:02d}", "section": s["section"], "text": " ".join(body)})
    return chunks


if __name__ == "__main__":
    chunks = chunk(open(sys.argv[1]).read())
    data = OpenAI().embeddings.create(model="lab-embed", input=[f"{c['section']}. {c['text']}" for c in chunks]).data
    for c, d in zip(chunks, data):
        c["vector"] = d.embedding
    with open(sys.argv[2], "w") as f:
        json.dump(chunks, f)
    print(f"{len(chunks)} chunks: " + ", ".join(f"{c['id']} {c['section']}" for c in chunks))

EOF
cat > ask.py <<'EOF'
import json
import math
import sys
from pathlib import Path

from openai import OpenAI

client = OpenAI()
INDEX = json.loads(Path(__file__).with_name("index.json").read_text())
REFUSE = "I don't know based on the provided sources."
SYSTEM = 'You answer Meridian employees\' questions from the employee handbook. Use only the sections below and cite section ids like [s02]. If they don\'t answer the question, the answer must be exactly: I don\'t know based on the provided sources. Reply with JSON: {"answer": "...", "citations": ["s02"]}'


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def ask(question, k=3, min_score=0.3):
    q = client.embeddings.create(model="lab-embed", input=[question]).data[0].embedding
    ranked = sorted(INDEX, key=lambda c: cosine(c["vector"], q), reverse=True)[:k]
    sources = [c for c in ranked if cosine(c["vector"], q) >= min_score]
    if not sources:
        return {"answer": REFUSE, "citations": [], "sources": []}
    context = "\n".join(f"[{c['id']}] {c['section']}. {c['text']}" for c in sources)
    raw = client.chat.completions.create(
        model="lab-fast",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": f"{SYSTEM}\n\n{context}"}, {"role": "user", "content": question}],
    ).choices[0].message.content
    result = json.loads(raw)
    ids = [c["id"] for c in sources]
    answer = str(result.get("answer", "")).strip()
    citations = [] if answer == REFUSE else [c for c in result.get("citations") or [] if c in ids]
    if answer != REFUSE and not citations:
        answer, citations = REFUSE, []
    return {"answer": answer, "citations": citations, "sources": ids}


if __name__ == "__main__":
    print(json.dumps(ask(sys.argv[1])))

EOF
python ingest.py handbook.md index.json
python ask.py "How many holiday days do I get?"
python ask.py "How much is the company car allowance?"
python ask.py "What's the weather in Rotterdam?"
```

</details>

## Check your work

```bash
D=/root/fde-lab/42-docs-bot; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/ingest.py 2>/dev/null && [ -s $D/ingest.py ] && echo "✅ ingest.py reads the key from the environment" || echo "❌ ingest.py must not contain a key - let the SDK read it from the environment"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/ask.py 2>/dev/null && [ -s $D/ask.py ] && echo "✅ ask.py reads the key from the environment" || echo "❌ ask.py must not contain a key - let the SDK read it from the environment"
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
def sections(path):
    text = Path(path).read_text() if Path(path).exists() else ""
    out, name = {}, None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            name = m.group(1).strip().lower()
            out[name] = []
        elif name is not None and line.strip():
            out[name].append(line.strip())
    return out
def chats():
    return sum(1 for l in open("/var/log/ailab/requests.jsonl") if '"chat.completions"' in l)

REFUSE = "I don't know based on the provided sources."
idx = load("index.json") or []
ok([c.get("section") for c in idx] == ['Working hours', 'Holidays', 'Sick leave', 'Expenses', 'Remote work', 'Equipment', 'Training budget'] and [c.get("id") for c in idx] == [f"s{i:02d}" for i in range(1, 8)], "index.json has the seven non-empty sections, numbered s01-s07", f"expected sections ['Working hours', 'Holidays', 'Sick leave', 'Expenses', 'Remote work', 'Equipment', 'Training budget'] as s01-s07 - got {[(c.get('id'), c.get('section')) for c in idx]}")
texts = " ".join(str(c.get("text", "")) for c in idx)
dirty = [p for p in ("CONFIDENTIAL", "Page 1 of", "Last edited", "<!--", "&amp;", "&#39;") if p in texts]
ok(idx and not dirty and "R&D staff" in texts and "doctor's note" in texts and "\n" not in texts, "chunks are clean: no boilerplate, entities decoded, lines joined", f"boilerplate or entities left in the chunks: {dirty}" if dirty else "decode HTML entities and join lines with spaces")
dims = {len(c.get("vector") or []) for c in idx}
ok(idx and len(dims) == 1 and min(dims) > 100, "every chunk has an embedding vector", f"each chunk needs a lab-embed vector - got lengths {dims}")
Path("/tmp/hb42.md").write_text("intro line\n## Parking\nPage 9 of 9\nStaff park in zone B.\n## Lockers\nCONFIDENTIAL\n\n## Bikes\nLast edited by x\nBike racks are at gate 2 &amp; gate 4.\n")
rc, out, err = run("ingest.py", "/tmp/hb42.md", "/tmp/idx42.json")
small = load("/tmp/idx42.json") or []
ok(rc == 0 and [(c.get("id"), c.get("section"), c.get("text")) for c in small] == [("s01", "Parking", "Staff park in zone B."), ("s02", "Bikes", "Bike racks are at gate 2 & gate 4.")], "ingest.py cleans and chunks an unseen export correctly", f"on an unseen export expected two chunks (Parking, Bikes) - got {[(c.get('id'), c.get('section'), c.get('text')) for c in small]} {err[-200:]}")
def ask(q):
    before = chats()
    rc, out, err = run("ask.py", q)
    try:
        return json.loads(out.splitlines()[-1]), chats() - before
    except Exception:
        return {"raw": out[-200:] + err[-200:]}, chats() - before
r, n = ask("How many holiday days do I get?")
ok(r.get("citations") == ["s02"] and "26" in str(r.get("answer")) and n == 1, "a holiday question is answered from s02 with a citation", f"expected an answer with 26 days citing s02 - got {r}")
r, n = ask("What's the hotel limit per night when travelling?")
ok(r.get("citations") == ["s04"] and "140" in str(r.get("answer")), "an expenses question is answered from s04", f"expected an answer with 140 EUR citing s04 - got {r}")
r, n = ask("How much is the company car allowance?")
ok(r.get("answer") == REFUSE and r.get("citations") == [] and n == 1, "a question the handbook doesn't answer is refused by the model", f"expected exactly the refusal with no citations, after one chat call - got {r}, {n} calls")
r, n = ask("What's the weather in Rotterdam?")
ok(r.get("answer") == REFUSE and r.get("sources") == [] and n == 0, "an off-topic question is refused without a chat call", f"expected the refusal, no sources and no chat call - got {r}, {n} calls")
sys.path.insert(0, ".")
try:
    import ask as bot, types
    reply = '{"answer": "Laptops are replaced yearly [s09].", "citations": ["s09"]}'
    emb = types.SimpleNamespace(create=lambda **k: types.SimpleNamespace(data=[types.SimpleNamespace(embedding=bot.INDEX[5]["vector"])]))
    bot.client = types.SimpleNamespace(embeddings=emb, chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=lambda **k: types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=reply))]))))
    r = bot.ask("laptops?")
    ok(r["answer"] == REFUSE and r["citations"] == [], "an answer citing only unknown sections is turned into the refusal", f"citations outside the sources must be dropped, and an uncited answer refused - got {r}")
except Exception as e:
    print(f"❌ import ask failed: {e}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")) and .json_mode and .temperature == 0 and .system)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-fast call" || echo "❌ the gateway has no lab-fast call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Messy exports need cleaning before chunking: boilerplate, entities, empty sections.
- Index once with one embedding call; retrieve with a score threshold.
- Validate citations in code and refuse when the sources don't support an answer.
