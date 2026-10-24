---
type: task
title: "Count the tokens in real prompts"
minutes: 7
---

## Set up

```bash
ailab status
mkdir -p /root/fde-lab/04-tokens
cd /root/fde-lab/04-tokens
cat > prompts.txt <<'EOF'
Hello!
Summarize the shipping policy for international parcels in three bullet points.
Bitte fassen Sie die Rückgaberichtlinie für beschädigte Pakete in zwei Sätzen zusammen.
Order MER-88412-XZ was scanned at hub LHR-07 at 2026-03-14T09:32:11Z with weight 18.4 kg.
EOF
```

## What to build

`prompts.txt` holds four prompts, one per line: a greeting, an English instruction, the same kind of instruction in German, and a line full of IDs and numbers.

Write `/root/fde-lab/04-tokens/tokens.py`, used as `python tokens.py PROMPTS_FILE OUT_FILE`:

1. For each non-empty line, call `lab-mini` with the line as the only user message and `max_tokens=1`.
2. Record the real `usage.prompt_tokens` from the response.
3. Write OUT_FILE as a JSON list, one object per line: `{"text", "chars", "words", "prompt_tokens", "chars_per_token"}`, where `chars_per_token` is chars divided by prompt tokens, rounded to 2 decimals.

```bash
cd /root/fde-lab/04-tokens
python tokens.py prompts.txt tokens.json
```

Look at `chars_per_token` for the four lines: which kinds of text are expensive?

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `words = len(text.split())`.
- `resp.usage.prompt_tokens` is the billed count.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/04-tokens
cat > tokens.py <<'EOF'
import json
import sys

from openai import OpenAI

client = OpenAI()
rows = []
for text in [line.strip() for line in open(sys.argv[1]) if line.strip()]:
    resp = client.chat.completions.create(model="lab-mini", max_tokens=1, messages=[{"role": "user", "content": text}])
    tokens = resp.usage.prompt_tokens
    rows.append({"text": text, "chars": len(text), "words": len(text.split()), "prompt_tokens": tokens,
                 "chars_per_token": round(len(text) / tokens, 2)})
json.dump(rows, open(sys.argv[2], "w"), indent=2, ensure_ascii=False)
for r in rows:
    print(f"{r['prompt_tokens']:4d} tokens  {r['chars_per_token']:5.2f} chars/token  {r['text'][:50]}")
EOF
python tokens.py prompts.txt tokens.json
```

</details>

## Check your work

```bash
D=/root/fde-lab/04-tokens; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/tokens.py 2>/dev/null && [ -s $D/tokens.py ] && echo "✅ tokens.py reads the key from the environment" || echo "❌ tokens.py must not contain a key - let the SDK read it from the environment"
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
from openai import OpenAI
C = OpenAI()
def real(t):
    return C.chat.completions.create(model="lab-mini", max_tokens=1, messages=[{"role": "user", "content": t}]).usage.prompt_tokens
def verify(rows, texts, label):
    good = isinstance(rows, list) and [r.get("text") for r in rows] == texts
    ok(good, f"{label}: one row per prompt, in order", f"{label}: expected one row per non-empty line, in order")
    if not good:
        return
    ok(all(r.get("chars") == len(t) and r.get("words") == len(t.split()) for r, t in zip(rows, texts)), f"{label}: chars and words are right", f"{label}: chars should be len(text) and words len(text.split())")
    ok(all(r.get("prompt_tokens") == real(t) for r, t in zip(rows, texts)), f"{label}: prompt_tokens are the billed counts", f"{label}: prompt_tokens should come from resp.usage.prompt_tokens")
    ok(all(r.get("chars_per_token") == round(r["chars"] / r["prompt_tokens"], 2) for r in rows if r.get("prompt_tokens")), f"{label}: chars_per_token is right", f"{label}: chars_per_token = chars / prompt_tokens rounded to 2")
texts = [l.strip() for l in open("prompts.txt") if l.strip()]
verify(load("tokens.json"), texts, "tokens.json")
Path("/tmp/new-prompts.txt").write_text("Where is my parcel?\n\nInvoice INV-2026-0042-B total EUR 1,204.50\n")
rc, out, err = run("tokens.py", "/tmp/new-prompts.txt", "/tmp/new-tokens.json")
verify(load("/tmp/new-tokens.json"), ["Where is my parcel?", "Invoice INV-2026-0042-B total EUR 1,204.50"], "new prompts")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Tokens are the unit of price, context and speed.
- IDs, numbers and non-English text use more tokens per character.
- `usage.prompt_tokens` is the authoritative, billed count.
