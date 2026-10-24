---
type: task
title: "Understand max_tokens limits"
minutes: 8
---

## Scenario

A teammate set `max_tokens` very low "to save money", and now users see answers that stop mid-sentence. See it for yourself, then learn to spot it in the response.

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/05-api
cd /root/ai-lab/05-api
```

## What to build

1. Send `Explain what an API is in two sentences.` to `lab-fast` with **`"max_tokens": 5`**. Save the response to `/root/ai-lab/05-api/capped.json`.
2. Send the same prompt with **`"max_tokens": 300`**. Save it to `/root/ai-lab/05-api/full.json`.
3. Write `/root/answers/05-max-tokens.txt` with three lines, taken from the responses:

```text
capped_finish=<finish_reason in capped.json>
capped_tokens=<usage.completion_tokens in capped.json>
full_finish=<finish_reason in full.json>
```

`finish_reason` is `stop` when the model finished on its own and `length` when it hit `max_tokens`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `max_tokens` goes at the top level of the request, next to `model`.
- `jq -r '.choices[0].finish_reason' capped.json`

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/05-api
ask() {
  curl -sS "$LAB_AI_URL/v1/chat/completions" \
    -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" \
    -d "{\"model\": \"lab-fast\", \"max_tokens\": $1, \"messages\": [{\"role\": \"user\", \"content\": \"Explain what an API is in two sentences.\"}]}"
}
ask 5 > capped.json
ask 300 > full.json
jq -r '.choices[0].message.content' capped.json
{
  echo "capped_finish=$(jq -r '.choices[0].finish_reason' capped.json)"
  echo "capped_tokens=$(jq -r '.usage.completion_tokens' capped.json)"
  echo "full_finish=$(jq -r '.choices[0].finish_reason' full.json)"
} > /root/answers/05-max-tokens.txt
cat /root/answers/05-max-tokens.txt
```

</details>

## Check your work

```bash
D=/root/ai-lab/05-api; F=/root/answers/05-max-tokens.txt
jq -e '.choices[0].finish_reason == "length" and .usage.completion_tokens <= 5' $D/capped.json >/dev/null 2>&1 && echo "✅ capped.json was cut off by max_tokens 5" || echo "❌ capped.json should come from a request with \"max_tokens\": 5"
jq -e '.choices[0].finish_reason == "stop"' $D/full.json >/dev/null 2>&1 && echo "✅ full.json finished on its own" || echo "❌ full.json should come from the same prompt with \"max_tokens\": 300"
jq -se 'any(.[]; .ok and .model == "lab-fast" and .max_tokens == 5)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway saw a request with max_tokens 5" || echo "❌ send a request to lab-fast with max_tokens 5"
grep -qx "capped_finish=$(jq -r '.choices[0].finish_reason' $D/capped.json 2>/dev/null)" $F 2>/dev/null && echo "✅ capped_finish is right" || echo "❌ capped_finish= must be the finish_reason in capped.json"
grep -qx "capped_tokens=$(jq -r '.usage.completion_tokens' $D/capped.json 2>/dev/null)" $F 2>/dev/null && echo "✅ capped_tokens is right" || echo "❌ capped_tokens= must be usage.completion_tokens in capped.json"
grep -qx "full_finish=$(jq -r '.choices[0].finish_reason' $D/full.json 2>/dev/null)" $F 2>/dev/null && echo "✅ full_finish is right" || echo "❌ full_finish= must be the finish_reason in full.json"
```

## What you learned

- `max_tokens` caps the reply; hitting it cuts the answer off mid-thought.
- `finish_reason` tells you why the model stopped: `stop` or `length`.
- Always check `finish_reason` in code before trusting a reply is complete.
