---
type: task
title: "Cap the history and summarize what gets dropped"
minutes: 8
---

## Set up

```bash
mkdir -p /root/fde-lab/12-state
```

## What to build

Write `/root/fde-lab/12-state/memory.py` with `trim_history(history, max_messages, summarize)`:

- `history` is the conversation **without** the main system prompt. It may start with a summary message: `{"role": "system", "content": "Summary of earlier conversation: ..."}`.
- Keep the last `max_messages` non-summary messages.
- If anything was dropped, call `summarize(previous_summary, dropped)` - `previous_summary` is the old summary text (without the prefix) or `None` - and put the result first as a new summary message.
- If nothing was dropped, return the history unchanged (and don't call `summarize`).

Then write `chat_capped.py`, used as `printf ... | python chat_capped.py MAX_MESSAGES`: the chat loop from the previous task, calling `trim_history` before each request, with a `summarize` that asks `lab-mini` to summarize the previous summary and the dropped messages in at most two sentences, keeping names, order numbers and requests.

```bash
cd /root/fde-lab/12-state
printf "Hi, I'm Tom from Harbor Foods and my pallet MER-60311 is late.\nCan you check the depot?\nWhich order did I mention?\n" | python chat_capped.py 3
```

The order number is dropped from the history before the last question - only the summary can answer it.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Split first: `old = history[0] if history and history[0]["role"] == "system" else None`.
- `dropped, kept = rest[:-max_messages], rest[-max_messages:]` - but watch out when `len(rest) <= max_messages`.
- In the summarizer, format each dropped message as `role: content` lines.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/12-state
cat > memory.py <<'EOF'
PREFIX = "Summary of earlier conversation: "


def trim_history(history, max_messages, summarize):
    old = history[0]["content"][len(PREFIX):] if history and history[0]["role"] == "system" else None
    rest = history[1:] if old is not None else history
    if len(rest) <= max_messages:
        return history
    dropped, kept = rest[:-max_messages], rest[-max_messages:]
    return [{"role": "system", "content": PREFIX + summarize(old, dropped)}] + kept
EOF
cat > chat_capped.py <<'EOF'
import sys

from openai import OpenAI

from memory import trim_history

client = OpenAI()
SYSTEM = {"role": "system", "content": "You are Meridian Logistics' support assistant. Answer in at most two sentences."}
MAX_MESSAGES = int(sys.argv[1])


def summarize(previous, dropped):
    text = "\n".join(f"{m['role']}: {m['content']}" for m in dropped)
    prompt = f"Previous summary: {previous or 'none'}\nMessages:\n{text}"
    return client.chat.completions.create(
        model="lab-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": "Summarize this earlier conversation in at most two sentences. Keep names, order numbers and requests."},
            {"role": "user", "content": prompt},
        ],
    ).choices[0].message.content.strip()


history = []
while True:
    try:
        text = input().strip()
    except EOFError:
        break
    if text == "quit":
        break
    if not text:
        continue
    history = trim_history(history + [{"role": "user", "content": text}], MAX_MESSAGES, summarize)
    reply = client.chat.completions.create(model="lab-mini", messages=[SYSTEM] + history).choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    print(f"assistant: {reply}")
EOF
printf "Hi, I'm Tom from Harbor Foods and my pallet MER-60311 is late.\nCan you check the depot?\nWhich order did I mention?\n" | python chat_capped.py 3
```

</details>

## Check your work

```bash
D=/root/fde-lab/12-state; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/chat_capped.py 2>/dev/null && [ -s $D/chat_capped.py ] && echo "✅ chat_capped.py reads the key from the environment" || echo "❌ chat_capped.py must not contain a key - let the SDK read it from the environment"
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
sys.path.insert(0, ".")
try:
    from memory import trim_history
except Exception as e:
    trim_history = None
    print(f"❌ import memory failed: {e}")
if trim_history:
    u = lambda t: {"role": "user", "content": t}
    a = lambda t: {"role": "assistant", "content": t}
    calls = []
    def fake(prev, dropped):
        calls.append((prev, [m["content"] for m in dropped]))
        return f"S{len(calls)}"
    h = [u("u1"), a("a1"), u("u2")]
    ok(trim_history(h, 3, fake) == h and not calls, "nothing is dropped (or summarized) when the history fits", "a history within max_messages should be returned unchanged without calling summarize")
    h = [u("u1"), a("a1"), u("u2"), a("a2"), u("u3")]
    r1 = trim_history(h, 3, fake)
    ok(r1 == [{"role": "system", "content": "Summary of earlier conversation: S1"}, u("u2"), a("a2"), u("u3")] and calls == [(None, ["u1", "a1"])], "the oldest messages are summarized and replaced by a summary message", f"expected the summary message then u2, a2, u3, with summarize(None, [u1, a1]) - got {r1}, calls {calls}")
    r2 = trim_history(r1 + [a("a3"), u("u4")], 3, fake)
    ok(r2 == [{"role": "system", "content": "Summary of earlier conversation: S2"}, u("u3"), a("a3"), u("u4")] and calls[-1] == ("S1", ["u2", "a2"]), "a second trim summarizes the previous summary plus the newly dropped messages", f"expected summarize('S1', [u2, a2]) and the new summary first - got {r2}, calls {calls}")
before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
r = subprocess.run([sys.executable, "chat_capped.py", "3"], input="Hi, I'm Lena from Dockside Retail and my pallet MER-70413 is stuck.\nCan you check the depot?\nWhich order did I mention?\n", capture_output=True, text=True)
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
lines = r.stdout.strip().splitlines()
ok(r.returncode == 0 and len(lines) == 3 and "MER-70413" in lines[-1], "with MAX_MESSAGES 3 the last answer still knows the order, via the summary", f"the third answer should mention MER-70413 - got {lines} {r.stderr[-200:]}")
last = [x for x in rows if x.get("api") == "chat.completions"][-1:] or [{}]
ok(last[0].get("roles") == ["system", "system", "user", "assistant", "user"], "the last request sent the system prompt, the summary and only the last 3 messages", f"the last request should be system, summary, user, assistant, user - got {last[0].get('roles')}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Re-sending everything doesn't scale - cap the history.
- Summarize what you drop, folding in the previous summary each time.
- Inject the summarizer so the trimming policy can be tested without a model.
