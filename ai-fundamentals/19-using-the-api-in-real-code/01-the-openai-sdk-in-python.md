---
type: task
title: "The OpenAI SDK in Python"
minutes: 12
---

## Scenario

`curl` is great for learning, but real tools are written in a programming language. The official **OpenAI Python SDK** speaks the chat completions API you already know - and because the lab gateway is OpenAI-compatible, it works against every lab model.

The SDK reads two environment variables, already set on your lab machine:

```bash
echo $OPENAI_BASE_URL      # http://localhost:4000/v1  - the gateway, not openai.com
echo ${OPENAI_API_KEY:0:7} # sk-lab-                   - your lab key
```

So `OpenAI()` with no arguments connects to the gateway, and **no key ever appears in your code**. The request mirrors the JSON you wrote by hand:

```python
from openai import OpenAI

client = OpenAI()
resp = client.chat.completions.create(
    model="lab-fast",
    messages=[{"role": "user", "content": "Hello"}],
)
print(resp.choices[0].message.content)
print(resp.usage.total_tokens)
```

`resp` is an object, not raw JSON: `resp.choices[0].message.content`, `resp.choices[0].finish_reason`, `resp.usage.prompt_tokens`. The SDK also retries on transient errors and raises clear exceptions (`openai.AuthenticationError`, `openai.RateLimitError`, `openai.APIConnectionError`).

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/19-sdk
python -c "import openai; print('openai', openai.__version__)"
```

## What to build

Write `/root/ai-lab/19-sdk/ask_openai.py`, a small command-line tool:

1. It takes the question as its command-line arguments: `python ask_openai.py What is DNS?`
2. It uses `OpenAI()` with **no key and no URL in the code**, calls `lab-fast` with a system message telling the model to answer in at most two sentences, and prints only the reply.
3. It prints the token usage to **stderr** as `tokens=<total_tokens>`, so it doesn't mix with the answer.
4. With no arguments, it prints `usage: ask_openai.py QUESTION` to stderr and exits with code 2.

Run it once and save its stdout to `/root/ai-lab/19-sdk/openai-answer.txt`:

```bash
python ask_openai.py "What does DNS do?" > openai-answer.txt
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `question = " ".join(sys.argv[1:])` joins the arguments.
- `print(f"tokens={resp.usage.total_tokens}", file=sys.stderr)` writes to stderr.
- `sys.exit(2)` sets the exit code.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/19-sdk
cat > ask_openai.py <<'EOF'
import sys

from openai import OpenAI

if len(sys.argv) < 2:
    print("usage: ask_openai.py QUESTION", file=sys.stderr)
    sys.exit(2)

client = OpenAI()
resp = client.chat.completions.create(
    model="lab-fast",
    messages=[
        {"role": "system", "content": "Answer in at most two sentences."},
        {"role": "user", "content": " ".join(sys.argv[1:])},
    ],
)
print(resp.choices[0].message.content)
print(f"tokens={resp.usage.total_tokens}", file=sys.stderr)
EOF
python ask_openai.py "What does DNS do?" > openai-answer.txt
cat openai-answer.txt
```

</details>

## Check your work

```bash
D=/root/ai-lab/19-sdk; P=$D/ask_openai.py
grep -q 'from openai import OpenAI' $P 2>/dev/null && grep -q 'OpenAI()' $P && echo "✅ ask_openai.py creates OpenAI() with no arguments" || echo "❌ use from openai import OpenAI and client = OpenAI()"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $P 2>/dev/null && [ -s $P ] && echo "✅ $P reads the key from the environment" || echo "❌ $P must not contain a key - let the SDK read it from the environment"
! grep -q 'localhost:4000\|api.openai.com' $P 2>/dev/null && [ -f $P ] && echo "✅ no URL is hard-coded" || echo "❌ don't hard-code the URL - OPENAI_BASE_URL already points at the gateway"
[ "$(wc -w < $D/openai-answer.txt 2>/dev/null || echo 0)" -ge 3 ] && echo "✅ openai-answer.txt holds an answer" || echo "❌ save the output of python ask_openai.py ... to openai-answer.txt"
cd $D && OUT=$(python $P "What is a TCP port?" 2>$D/.err); [ -n "$OUT" ] && grep -Eq '^tokens=[0-9]+$' $D/.err && ! echo "$OUT" | grep -q '^tokens=' && echo "✅ answer on stdout, tokens=N on stderr" || echo "❌ print the reply to stdout and tokens=<total> to stderr"
python $P >/dev/null 2>$D/.err; rc=$?; [ $rc = 2 ] && grep -q 'usage' $D/.err && echo "✅ no arguments: usage message and exit 2" || echo "❌ with no arguments print usage to stderr and exit 2 (exit was $rc)"
rm -f $D/.err
jq -se 'any(.[]; .ok and (.client | startswith("OpenAI/Python")) and .model == "lab-fast" and .system)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged an OpenAI SDK call with a system message" || echo "❌ the gateway has no OpenAI SDK call to lab-fast with a system message"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- `OpenAI()` reads `OPENAI_BASE_URL` and `OPENAI_API_KEY` from the environment - no key in code.
- The SDK call mirrors the JSON request: model, messages, then `choices[0].message.content`.
- Send answers to stdout and diagnostics to stderr so your tool works in pipelines.
