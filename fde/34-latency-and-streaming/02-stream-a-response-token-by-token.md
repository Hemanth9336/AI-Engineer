---
type: task
title: "Stream a response token by token"
minutes: 8
---

## Set up

```bash
mkdir -p /root/fde-lab/34-latency
cd /root/fde-lab/34-latency
```

## What to build

Write `/root/fde-lab/34-latency/stream.py`, used as `python stream.py QUESTION`:

- Call `lab-fast` with `stream=True`.
- Print each content delta as it arrives, with no newline between pieces and `flush=True`. Print one newline at the end.
- Then print to **stderr**: `[stream] first token after X ms, total Y ms, N chunks` - time to first content, total time, and the number of chunks that carried text.

```bash
cd /root/fde-lab/34-latency
python stream.py "Explain how Meridian handles a damaged parcel claim"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Skip chunks with an empty `choices` list - the final usage chunk has none.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/34-latency
cat > stream.py <<'EOF'
import sys
import time

from openai import OpenAI

client = OpenAI()


def stream_answer(question):
    start = time.perf_counter()
    first = None
    chunks = 0
    stream = client.chat.completions.create(
        model="lab-fast",
        stream=True,
        messages=[{"role": "system", "content": "You are Meridian Logistics' support assistant."}, {"role": "user", "content": question}],
    )
    for chunk in stream:
        if not chunk.choices:
            continue
        text = chunk.choices[0].delta.content
        if text:
            if first is None:
                first = time.perf_counter() - start
            chunks += 1
            print(text, end="", flush=True)
    print()
    total = time.perf_counter() - start
    print(f"[stream] first token after {first * 1000:.0f} ms, total {total * 1000:.0f} ms, {chunks} chunks", file=sys.stderr)


if __name__ == "__main__":
    stream_answer(sys.argv[1])

EOF
python stream.py "Explain how Meridian handles a damaged parcel claim"
```

</details>

## Check your work

```bash
D=/root/fde-lab/34-latency; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/stream.py 2>/dev/null && [ -s $D/stream.py ] && echo "✅ stream.py reads the key from the environment" || echo "❌ stream.py must not contain a key - let the SDK read it from the environment"
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
want = 'After two failed delivery attempts, the parcel waits at your local depot for 7 days. If nobody collects it in that time, it goes back to the sender.'
b = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
rc, out, err = run("stream.py", "Explain what happens after two failed delivery attempts")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][b:]
ok(rc == 0 and out.strip() == want, "the streamed pieces join up into the full answer", f"stdout should be exactly the answer - got {out[:200]!r} {err[-200:]}")
ok(rows and rows[-1].get("stream") is True and rows[-1].get("model") == "lab-fast", "the gateway saw a streaming lab-fast request", "call lab-fast with stream=True")
m = re.search(r"\[stream\] first token after (\d+) ms, total (\d+) ms, (\d+) chunks", err)
ok(m and int(m.group(1)) <= int(m.group(2)) and int(m.group(3)) >= 10 and "[stream]" not in out, "timings and chunk count were reported on stderr", f"expected '[stream] first token after X ms, total Y ms, N chunks' on stderr with many chunks - got {err[-200:]!r}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Users judge speed by time to first token; stream to show progress early.
- Shorter answers are the biggest real latency win.
- Streamed text can't be filtered as a whole - plan output checks accordingly.
