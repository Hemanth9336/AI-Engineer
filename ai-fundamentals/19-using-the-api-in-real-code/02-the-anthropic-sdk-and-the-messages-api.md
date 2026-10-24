---
type: task
title: "The Anthropic SDK and the Messages API"
minutes: 12
---

## Scenario

Anthropic's **Messages API** (`/v1/messages`) is the other major API shape. Claude Code uses it, and so does the official `anthropic` SDK. The lab gateway serves it too, for every lab model.

It is close to chat completions, with a few differences worth knowing:

| | Chat completions | Messages API |
|---|---|---|
| System prompt | A `system` message in `messages` | A separate `system` parameter |
| Max output | Optional `max_tokens` | `max_tokens` is **required** |
| Reply text | `choices[0].message.content` | `content[0].text` (a list of blocks) |
| Why it stopped | `finish_reason`: `stop`, `length` | `stop_reason`: `end_turn`, `max_tokens` |
| Token counts | `prompt_tokens`, `completion_tokens` | `input_tokens`, `output_tokens` |

```python
from anthropic import Anthropic

client = Anthropic()          # reads ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN
msg = client.messages.create(
    model="lab-fast",
    max_tokens=300,
    system="You are concise.",
    messages=[{"role": "user", "content": "Hello"}],
)
print(msg.content[0].text)
print(msg.usage.input_tokens, msg.usage.output_tokens)
```

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/19-sdk
python -c "import anthropic; print('anthropic', anthropic.__version__)"
```

## What to build

Write `/root/ai-lab/19-sdk/ask_claude.py`:

1. It takes the question from its command-line arguments.
2. It uses `Anthropic()` with **no key and no URL in the code**, and calls `client.messages.create` with `model="lab-fast"`, `max_tokens=300`, and a `system` parameter telling the model to answer in at most two sentences.
3. It prints only the reply text, and prints `in=<input_tokens> out=<output_tokens>` to stderr.

Save the answer to a question of your choice:

```bash
python ask_claude.py "What is a load balancer?" > claude-answer.txt
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- The reply is `msg.content[0].text`.
- `system=` is a keyword argument, not a message.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/19-sdk
cat > ask_claude.py <<'EOF'
import sys

from anthropic import Anthropic

client = Anthropic()
msg = client.messages.create(
    model="lab-fast",
    max_tokens=300,
    system="Answer in at most two sentences.",
    messages=[{"role": "user", "content": " ".join(sys.argv[1:])}],
)
print(msg.content[0].text)
print(f"in={msg.usage.input_tokens} out={msg.usage.output_tokens}", file=sys.stderr)
EOF
python ask_claude.py "What is a load balancer?" > claude-answer.txt
cat claude-answer.txt
```

</details>

## Check your work

```bash
D=/root/ai-lab/19-sdk; P=$D/ask_claude.py
grep -q 'from anthropic import Anthropic' $P 2>/dev/null && grep -q 'Anthropic()' $P && echo "✅ ask_claude.py creates Anthropic() with no arguments" || echo "❌ use from anthropic import Anthropic and client = Anthropic()"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $P 2>/dev/null && [ -s $P ] && echo "✅ $P reads the key from the environment" || echo "❌ $P must not contain a key - let the SDK read it from the environment"
grep -q 'messages.create' $P 2>/dev/null && grep -q 'max_tokens' $P && grep -Eq 'system *=' $P && echo "✅ it uses messages.create with max_tokens and a system parameter" || echo "❌ call client.messages.create with max_tokens and system="
[ "$(wc -w < $D/claude-answer.txt 2>/dev/null || echo 0)" -ge 3 ] && echo "✅ claude-answer.txt holds an answer" || echo "❌ save the output of python ask_claude.py ... to claude-answer.txt"
cd $D && OUT=$(python $P "What is an IP address?" 2>$D/.err); [ -n "$OUT" ] && grep -Eq '^in=[0-9]+ out=[0-9]+$' $D/.err && echo "✅ reply on stdout, in=N out=N on stderr" || echo "❌ print the reply to stdout and in=<input_tokens> out=<output_tokens> to stderr"
rm -f $D/.err
jq -se 'any(.[]; .ok and (.client | startswith("Anthropic/Python")) and .api == "messages")' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged a Anthropic SDK Messages API call" || echo "❌ the gateway has no successful Anthropic SDK Messages API call yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- The Messages API puts `system` outside the messages and requires `max_tokens`.
- Replies are a list of content blocks: `msg.content[0].text`.
- One gateway can serve both API shapes, so you can switch SDKs without switching models.
