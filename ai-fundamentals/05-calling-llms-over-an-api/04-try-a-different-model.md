---
type: task
title: "Try a different model"
minutes: 8
---

## Scenario

Same question, different model. Switching is one field in the request - which is exactly why apps are built against a gateway with stable model names.

## Set up

This builds on `request.json` from the previous task. The Set up recreates it if it is missing.

```bash
ailab status
mkdir -p /root/ai-lab/05-api
cd /root/ai-lab/05-api
[ -f request.json ] || cat > request.json <<'EOF'
{
  "model": "lab-fast",
  "messages": [
    {"role": "system", "content": "You are a concise assistant for a DevOps team."},
    {"role": "user", "content": "What is the difference between a process and a thread?"}
  ]
}
EOF
```

## What to build

1. Send the same `request.json`, but with `model` set to **`lab-smart`**, and save the response to `/root/ai-lab/05-api/smart.json`. Leave `request.json` itself unchanged - change the model on the fly with `jq '.model = "lab-smart"' request.json` and pipe it to curl.
2. Send the unchanged `request.json` again and save that response to `/root/ai-lab/05-api/fast.json`.
3. Write `/root/answers/05-models.txt` with two lines, taking each value from the `model` field of the response:

```text
fast=<model in fast.json>
smart=<model in smart.json>
```

Compare the two replies. Which is longer? Which would you rather read?

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `curl -d @-` reads the body from standard input, so `jq ... | curl ... -d @-` works.
- `jq -r .model smart.json` prints the model that answered.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/05-api
jq '.model = "lab-smart"' request.json | curl -sS "$LAB_AI_URL/v1/chat/completions" \
  -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" -d @- -o smart.json
curl -sS "$LAB_AI_URL/v1/chat/completions" \
  -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" -d @request.json -o fast.json
printf 'fast=%s\nsmart=%s\n' "$(jq -r .model fast.json)" "$(jq -r .model smart.json)" > /root/answers/05-models.txt
cat /root/answers/05-models.txt
jq -r '.choices[0].message.content' fast.json smart.json
```

</details>

## Check your work

```bash
D=/root/ai-lab/05-api; F=/root/answers/05-models.txt
jq -e '.model == "lab-smart" and (.choices[0].message.content | length > 0)' $D/smart.json >/dev/null 2>&1 && echo "✅ smart.json was answered by lab-smart" || echo "❌ send the request with model lab-smart and save it to smart.json"
jq -e '.model == "lab-fast" and (.choices[0].message.content | length > 0)' $D/fast.json >/dev/null 2>&1 && echo "✅ fast.json was answered by lab-fast" || echo "❌ send the unchanged request.json and save it to fast.json"
jq -e '.model == "lab-fast"' $D/request.json >/dev/null 2>&1 && echo "✅ request.json still says lab-fast" || echo "❌ leave request.json unchanged - switch the model with jq on the way to curl"
grep -qx 'fast=lab-fast' $F 2>/dev/null && grep -qx 'smart=lab-smart' $F 2>/dev/null && echo "✅ 05-models.txt records both models" || echo "❌ write fast=<model> and smart=<model> from the responses to $F"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Switching models is a one-field change when you call a gateway.
- `jq` can edit a request on the way to curl, so the file stays clean.
- The response's `model` field tells you who actually answered.
