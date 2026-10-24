---
type: task
title: "Add a response cache and measure the savings"
minutes: 7
---

## Set up

`questions.txt` is a morning's worth of FAQ traffic - with repeats.

```bash
mkdir -p /root/fde-lab/33-cost
cd /root/fde-lab/33-cost
cat > questions.txt <<'EOF'
Where is my parcel?
where is my parcel?
When is support open?
Where  is my   PARCEL?
When is support open?
How do I report damage?
EOF
rm -f cache.json
```

## What to build

Write `/root/fde-lab/33-cost/cache.py`:

- `ask(question)` answers with `lab-mini` at `temperature=0`, with a short system prompt.
- Responses are cached in `cache.json` next to the script, keyed by a SHA-256 of the model, the system prompt and the **normalised** question (lower-case, whitespace collapsed). Store the answer and the call's `usage.total_tokens`.
- On a hit, return the stored answer with **no API call** and count the tokens saved.
- `python cache.py QUESTIONS_FILE` asks each non-empty line and prints `calls: N, cache hits: M, tokens saved: T`.

```bash
cd /root/fde-lab/33-cost
python cache.py questions.txt
python cache.py questions.txt
```

The second run should make no calls at all.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `hashlib.sha256(text.encode()).hexdigest()` gives a safe dictionary key.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/33-cost
cat > cache.py <<'EOF'
import hashlib
import json
import sys
from pathlib import Path

from openai import OpenAI

client = OpenAI()
CACHE_FILE = Path(__file__).with_name("cache.json")
MODEL = "lab-mini"
SYSTEM = "You are Meridian Logistics' support assistant. Answer in one or two sentences."
STATS = {"calls": 0, "hits": 0, "saved_tokens": 0}


def normalise(question):
    return " ".join(question.lower().split())


def cache_key(question):
    return hashlib.sha256(f"{MODEL}\n{SYSTEM}\n{normalise(question)}".encode()).hexdigest()


def ask(question):
    cache = json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}
    key = cache_key(question)
    if key in cache:
        STATS["hits"] += 1
        STATS["saved_tokens"] += cache[key]["tokens"]
        return cache[key]["answer"]
    resp = client.chat.completions.create(
        model=MODEL, temperature=0,
        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}],
    )
    STATS["calls"] += 1
    cache[key] = {"answer": resp.choices[0].message.content, "tokens": resp.usage.total_tokens}
    CACHE_FILE.write_text(json.dumps(cache))
    return cache[key]["answer"]


if __name__ == "__main__":
    for line in open(sys.argv[1]):
        if line.strip():
            ask(line.strip())
    print(f"calls: {STATS['calls']}, cache hits: {STATS['hits']}, tokens saved: {STATS['saved_tokens']}")

EOF
python cache.py questions.txt
python cache.py questions.txt
```

</details>

## Check your work

```bash
D=/root/fde-lab/33-cost; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/cache.py 2>/dev/null && [ -s $D/cache.py ] && echo "✅ cache.py reads the key from the environment" || echo "❌ cache.py must not contain a key - let the SDK read it from the environment"
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
Path("cache.json").unlink(missing_ok=True)
Path("/tmp/q33.txt").write_text("Can I change my address?\ncan I change   my address?\nDo you open on Sundays?\nCAN I CHANGE MY ADDRESS?\n\nDo you open on Sundays?\n")
def chats():
    return [json.loads(l) for l in open("/var/log/ailab/requests.jsonl") if '"chat.completions"' in l]
b = len(chats())
rc, out, err = run("cache.py", "/tmp/q33.txt")
new = chats()[b:]
m = re.search(r"calls: (\d+), cache hits: (\d+), tokens saved: (\d+)", out)
ok(rc == 0 and len(new) == 2 and all(r.get("model") == "lab-mini" for r in new) and m and m.group(1, 2) == ("2", "3"),
   "first run: 2 lab-mini calls for 5 questions, 3 cache hits", f"expected 2 lab-mini calls and 'calls: 2, cache hits: 3' - got {len(new)} calls, {out!r} {err[-200:]}")
first = sorted(r["total_tokens"] for r in new)
b = len(chats())
rc, out, err = run("cache.py", "/tmp/q33.txt")
m2 = re.search(r"calls: (\d+), cache hits: (\d+), tokens saved: (\d+)", out)
ok(rc == 0 and len(chats()) == b and m2 and m2.group(1, 2) == ("0", "5"), "second run: every question served from cache, no calls", f"expected no calls and 'calls: 0, cache hits: 5' - got {out!r}")
ok(m and m2 and len(first) == 2 and int(m2.group(3)) > int(m.group(3)) > 0 and int(m.group(3)) >= min(first), "tokens saved add up from the stored usage", f"tokens saved should come from each hit's stored total_tokens - got {out!r}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Everything that can change the answer belongs in the cache key.
- Normalise questions so trivial differences still hit.
- Never cache live, personal or permission-dependent answers across users.
