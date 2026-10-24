---
type: task
title: "Your first request with curl"
minutes: 8
---

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/05-api
cd /root/ai-lab/05-api
```

## What to build

1. Send this request and save the **whole JSON response** to `/root/ai-lab/05-api/first.json` (use `-o first.json`):

```bash
curl -sS "$LAB_AI_URL/v1/chat/completions" \
  -H "Authorization: Bearer $LAB_AI_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "lab-fast", "messages": [{"role": "user", "content": "In one sentence, what is an API?"}]}' \
  -o first.json
```

2. Look at the response with `jq . first.json`. Find `choices`, `message`, `content`, `finish_reason`, `model`, and `usage`.
3. Extract just the reply text into `/root/ai-lab/05-api/first-reply.txt`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `jq -r` prints a string without the surrounding quotes.
- The reply path is `.choices[0].message.content`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/05-api
curl -sS "$LAB_AI_URL/v1/chat/completions" \
  -H "Authorization: Bearer $LAB_AI_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "lab-fast", "messages": [{"role": "user", "content": "In one sentence, what is an API?"}]}' \
  -o first.json
jq . first.json
jq -r '.choices[0].message.content' first.json > first-reply.txt
cat first-reply.txt
```

</details>

## Check your work

```bash
D=/root/ai-lab/05-api
jq -e '.object == "chat.completion"' $D/first.json >/dev/null 2>&1 && echo "✅ first.json is a chat completion response" || echo "❌ save the whole response to $D/first.json with curl -o"
jq -e '.model == "lab-fast"' $D/first.json >/dev/null 2>&1 && echo "✅ it was answered by lab-fast" || echo "❌ use \"model\": \"lab-fast\" in the request"
jq -e '.usage.total_tokens > 0' $D/first.json >/dev/null 2>&1 && echo "✅ the response has a usage block" || echo "❌ first.json has no usage - did the request succeed?"
[ -s $D/first-reply.txt ] && [ "$(cat $D/first-reply.txt)" = "$(jq -r '.choices[0].message.content' $D/first.json 2>/dev/null)" ] && echo "✅ first-reply.txt holds exactly the reply text" || echo "❌ write jq -r '.choices[0].message.content' first.json to first-reply.txt"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A model call is an HTTP POST with JSON in and JSON out.
- The reply text lives at `.choices[0].message.content`.
- The key comes from `$LAB_AI_KEY` in a header, so it never lands in a file.
