---
type: task
title: "Your first API call with curl"
minutes: 7
---

## Set up

```bash
ailab status
mkdir -p /root/harness-lab/04-api
```

## What to build

Call the chat API directly with `curl`:

1. Send a POST to `$LAB_AI_URL/v1/chat/completions` with model `lab-mini`, one user message `What does an AI agent harness do? Answer in one sentence.`, and `max_tokens` 100.
2. Save the full JSON response to `/root/harness-lab/04-api/first.json`.
3. Extract only the reply text into `/root/harness-lab/04-api/reply.txt` with `jq -r`.

Use `$LAB_AI_KEY` in the `Authorization` header - don't paste the key.

```bash
cd /root/harness-lab/04-api
curl -sS "$LAB_AI_URL/v1/chat/completions" -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" \
  -d '{"model": "lab-mini", "max_tokens": 100, "messages": [{"role": "user", "content": "..."}]}' > first.json
```

Then look at `usage` and `finish_reason` in `first.json`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `jq -r '.choices[0].message.content' first.json > reply.txt`.
- If `first.json` contains an `error` field, read its message - usually a typo in the JSON body.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/04-api
curl -sS "$LAB_AI_URL/v1/chat/completions" -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" \
  -d '{"model": "lab-mini", "max_tokens": 100, "messages": [{"role": "user", "content": "What does an AI agent harness do? Answer in one sentence."}]}' > first.json
jq -r '.choices[0].message.content' first.json > reply.txt
cat reply.txt
jq '.usage, .choices[0].finish_reason' first.json
```

</details>

## Check your work

```bash
D=/root/harness-lab/04-api; cd $D 2>/dev/null || echo "❌ create $D"
jq -e '.choices[0].message.content and .usage.total_tokens > 0' first.json >/dev/null 2>&1 && echo "✅ first.json is a full chat completion response" || echo "❌ save the full JSON response to first.json"
[ -s reply.txt ] && [ "$(cat reply.txt)" = "$(jq -r '.choices[0].message.content' first.json 2>/dev/null)" ] && echo "✅ reply.txt holds exactly the reply in first.json" || echo "❌ extract .choices[0].message.content from first.json into reply.txt"
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-mini" and (.client | startswith("curl")) and .max_tokens == 100)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your curl call to lab-mini with max_tokens 100" || echo "❌ the gateway has no curl call to lab-mini with max_tokens 100"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- The chat API is a POST with model, messages, and options; the reply is at `choices[0].message.content`.
- `finish_reason` and `usage` tell you whether it was cut off and what it cost.
- Keys come from environment variables, never from files.
