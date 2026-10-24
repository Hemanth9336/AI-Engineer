---
type: task
title: "Write a few-shot prompt"
minutes: 13
---

## Scenario

The support team wants every incoming message tagged `billing`, `outage`, or `access` - one lower-case word, because a script reads the tag. Zero-shot answers keep coming back as `Outage.` or `Category: Outage`. Fix it with examples.

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/07-few-shot
cd /root/ai-lab/07-few-shot
printf '%s\n' "Since 9am every request to the API returns 503 and our status page is blank." > ticket.txt
```

## What to build

Write `/root/ai-lab/07-few-shot/few-shot.json` for `lab-fast`:

1. A **system** message telling the model to classify support messages and reply with exactly one word: `billing`, `outage`, or `access`.
2. At least **two example pairs** - a `user` message with a sample support message, then an `assistant` message whose content is exactly one of the three labels. Use at least two different labels across your examples.
3. A final `user` message whose content is **exactly** the text in `ticket.txt`.

Send it, save the response to `few-shot-response.json` and the reply text to `/root/ai-lab/07-few-shot/label.txt`. The correct label for the ticket is `outage`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Build the last message from the file so it matches exactly: `jq --arg t "$(cat ticket.txt)" '.messages += [{role: "user", content: $t}]'`.
- Every assistant example must be one bare lower-case word - the model copies that exactly.
- `tr -d '[:space:]'` strips a stray newline or space before you compare.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/07-few-shot
cat > examples.json <<'EOF'
{
  "model": "lab-fast",
  "temperature": 0,
  "messages": [
    {"role": "system", "content": "You classify customer support messages. Reply with exactly one lower-case word: billing, outage, or access. No punctuation, no explanation."},
    {"role": "user", "content": "I was charged twice for my subscription this month."},
    {"role": "assistant", "content": "billing"},
    {"role": "user", "content": "I reset my password and still can't sign in to the console."},
    {"role": "assistant", "content": "access"},
    {"role": "user", "content": "Uploads have failed for all of our users for the last hour."},
    {"role": "assistant", "content": "outage"}
  ]
}
EOF
jq --arg t "$(cat ticket.txt)" '.messages += [{role: "user", content: $t}]' examples.json > few-shot.json
curl -sS "$LAB_AI_URL/v1/chat/completions" -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" -d @few-shot.json -o few-shot-response.json
jq -r '.choices[0].message.content' few-shot-response.json > label.txt
cat label.txt
```

</details>

## Check your work

```bash
D=/root/ai-lab/07-few-shot; R=$D/few-shot.json
jq -e '.model == "lab-fast" and .messages[0].role == "system" and (.messages[0].content | test("billing") and test("outage") and test("access"))' $R >/dev/null 2>&1 && echo "✅ the system message names the three labels" || echo "❌ few-shot.json needs model lab-fast and a system message naming billing, outage and access"
jq -e '[.messages[1:-1][] | select(.role == "assistant")] | length >= 2' $R >/dev/null 2>&1 && echo "✅ there are at least two worked examples" || echo "❌ add at least two user/assistant example pairs between the system message and the ticket"
jq -e '[.messages[1:-1][] | select(.role == "assistant") | .content] | all(. == "billing" or . == "outage" or . == "access")' $R >/dev/null 2>&1 && echo "✅ every example answer is exactly one label" || echo "❌ each assistant example must be exactly billing, outage or access"
jq -e '[.messages[1:-1][] | select(.role == "assistant") | .content] | unique | length >= 2' $R >/dev/null 2>&1 && echo "✅ the examples use at least two different labels" || echo "❌ use at least two different labels in your examples"
[ "$(jq -r '.messages[-1].role + ":" + .messages[-1].content' $R 2>/dev/null)" = "user:$(cat $D/ticket.txt)" ] && echo "✅ the last message is the ticket, word for word" || echo "❌ the final message must be a user message with exactly the text of ticket.txt"
[ "$(tr -d '[:space:]' < $D/label.txt 2>/dev/null)" = "outage" ] && echo "✅ the model answered: outage" || echo "❌ label.txt should be outage - got '$(cat $D/label.txt 2>/dev/null)'"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Examples as user/assistant pairs show the model the exact answer format.
- The model copies examples literally, so every example answer must be perfect.
- Build the final message from the data file so nothing is mistyped.
