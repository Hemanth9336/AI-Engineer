---
type: task
title: "Send your own request"
minutes: 8
---

## Scenario

Typing JSON inside a `-d '...'` string gets painful fast. Real scripts keep the request body in a file.

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/05-api
cd /root/ai-lab/05-api
```

## What to build

1. Write `/root/ai-lab/05-api/request.json`: a chat request for model `lab-fast` with **two** messages -
   - a `system` message: `You are a concise assistant for a DevOps team.`
   - a `user` message with **your own question** of at least five words.
2. Send it with `curl ... -d @request.json` and save the response to `/root/ai-lab/05-api/response.json`.
3. Save the reply text to `/root/ai-lab/05-api/reply.txt`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `-d @request.json` tells curl to read the body from a file.
- Check your JSON before sending: `jq . request.json` fails loudly on a typo.
- Messages are objects like `{"role": "system", "content": "..."}`, in order.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/05-api
cat > request.json <<'EOF'
{
  "model": "lab-fast",
  "messages": [
    {"role": "system", "content": "You are a concise assistant for a DevOps team."},
    {"role": "user", "content": "What is the difference between a process and a thread?"}
  ]
}
EOF
jq . request.json
curl -sS "$LAB_AI_URL/v1/chat/completions" \
  -H "Authorization: Bearer $LAB_AI_KEY" \
  -H "Content-Type: application/json" \
  -d @request.json -o response.json
jq -r '.choices[0].message.content' response.json > reply.txt
cat reply.txt
```

</details>

## Check your work

```bash
D=/root/ai-lab/05-api
jq -e '.model == "lab-fast"' $D/request.json >/dev/null 2>&1 && echo "✅ request.json is valid JSON for lab-fast" || echo "❌ write a valid request.json with \"model\": \"lab-fast\""
jq -e '.messages[0].role == "system" and .messages[0].content == "You are a concise assistant for a DevOps team."' $D/request.json >/dev/null 2>&1 && echo "✅ the first message is the system message" || echo "❌ messages[0] must be the system message, word for word"
jq -e '.messages[1].role == "user" and (.messages[1].content | split(" ") | length) >= 5' $D/request.json >/dev/null 2>&1 && echo "✅ the second message is your own user question" || echo "❌ messages[1] must be a user question of at least five words"
jq -e '.choices[0].message.content | length > 0' $D/response.json >/dev/null 2>&1 && echo "✅ response.json holds a reply" || echo "❌ send request.json with -d @request.json and save the output to response.json"
[ -s $D/reply.txt ] && [ "$(cat $D/reply.txt)" = "$(jq -r '.choices[0].message.content' $D/response.json 2>/dev/null)" ] && echo "✅ reply.txt holds exactly the reply text" || echo "❌ extract the reply text from response.json into reply.txt"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Keep request bodies in files and send them with `-d @file`.
- A system message sets behaviour; the user message carries the question.
- `jq .` is a free JSON validator - run it before you send.
