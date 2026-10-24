---
type: task
title: "Compare two models on one prompt"
minutes: 10
---

## Scenario

Your team wants an assistant that explains error messages to junior engineers. Before choosing a model, compare `lab-fast` and `lab-smart` on the same prompt.

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/13-compare /root/answers
```

## What to build

1. Write `/root/ai-lab/13-compare/prompt.json` for `lab-fast` with a user message asking the model to explain, for a junior engineer, what `connection refused` means when calling `http://localhost:8080`, in at most 3 sentences.
2. Make `prompt-smart.json`: the same request with only the model changed to `lab-smart` (use `jq`, don't retype it).
3. Send both and save the responses to `fast.json` and `smart.json`.
4. Write `/root/answers/13-compare.txt` with exactly these four lines:

```text
fast_tokens=<completion_tokens from fast.json>
smart_tokens=<completion_tokens from smart.json>
winner=<lab-fast or lab-smart - the one you would choose>
reason=<one short sentence>
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `jq '.model = "lab-smart"' prompt.json > prompt-smart.json` changes only the model.
- `jq .usage.completion_tokens fast.json` reads the token count.
- There is no single right winner - but your reason should mention quality, speed, or cost.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/13-compare
jq -n '{model: "lab-fast", messages: [{role: "user", content: "Explain to a junior engineer what \"connection refused\" means when calling http://localhost:8080. At most 3 sentences."}]}' > prompt.json
jq '.model = "lab-smart"' prompt.json > prompt-smart.json
curl -sS "$LAB_AI_URL/v1/chat/completions" -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" -d @prompt.json -o fast.json
curl -sS "$LAB_AI_URL/v1/chat/completions" -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" -d @prompt-smart.json -o smart.json
jq -r '.choices[0].message.content' fast.json smart.json
cat > /root/answers/13-compare.txt <<EOF
fast_tokens=$(jq .usage.completion_tokens fast.json)
smart_tokens=$(jq .usage.completion_tokens smart.json)
winner=lab-fast
reason=Both answers are correct and clear, and lab-fast is cheaper and quicker for a simple explanation.
EOF
cat /root/answers/13-compare.txt
```

</details>

## Check your work

```bash
D=/root/ai-lab/13-compare; A=/root/answers/13-compare.txt
jq -e '.model == "lab-fast" and (.messages[-1].content | test("connection refused"; "i"))' $D/prompt.json >/dev/null 2>&1 && echo "✅ prompt.json asks lab-fast about connection refused" || echo "❌ prompt.json needs model lab-fast and a question about 'connection refused'"
jq -e --slurpfile p $D/prompt.json '.model == "lab-smart" and (del(.model) == ($p[0] | del(.model)))' $D/prompt-smart.json >/dev/null 2>&1 && echo "✅ prompt-smart.json differs from prompt.json only in the model" || echo "❌ prompt-smart.json must be prompt.json with only the model changed to lab-smart"
jq -e '.model == "lab-fast" and .choices[0].message.content != null' $D/fast.json >/dev/null 2>&1 && echo "✅ fast.json is a lab-fast response" || echo "❌ save the lab-fast response to fast.json"
jq -e '.model == "lab-smart" and .choices[0].message.content != null' $D/smart.json >/dev/null 2>&1 && echo "✅ smart.json is a lab-smart response" || echo "❌ save the lab-smart response to smart.json"
[ "$(grep -c . $A 2>/dev/null)" = 4 ] && echo "✅ 13-compare.txt has four lines" || echo "❌ /root/answers/13-compare.txt needs exactly four lines"
[ -n "$(jq .usage.completion_tokens $D/fast.json 2>/dev/null)" ] && grep -qx "fast_tokens=$(jq .usage.completion_tokens $D/fast.json 2>/dev/null)" $A 2>/dev/null && echo "✅ fast_tokens matches fast.json" || echo "❌ fast_tokens must equal .usage.completion_tokens in fast.json"
[ -n "$(jq .usage.completion_tokens $D/smart.json 2>/dev/null)" ] && grep -qx "smart_tokens=$(jq .usage.completion_tokens $D/smart.json 2>/dev/null)" $A 2>/dev/null && echo "✅ smart_tokens matches smart.json" || echo "❌ smart_tokens must equal .usage.completion_tokens in smart.json"
grep -Eqx 'winner=lab-(fast|smart)' $A 2>/dev/null && echo "✅ you picked a winner" || echo "❌ add winner=lab-fast or winner=lab-smart"
grep -Eiq '^reason=.*(cheap|cost|fast|quick|speed|slow|quality|clear|accurate|detail|better|correct)' $A 2>/dev/null && echo "✅ your reason weighs quality, speed, or cost" || echo "❌ add reason=... mentioning quality, speed, or cost"
jq -se 'any(.[]; .model == "lab-smart" and .ok)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway log shows a lab-smart call" || echo "❌ the gateway has no successful lab-smart request yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Compare models on the same prompt by changing only the model field.
- Weigh quality against tokens (cost) and speed - bigger is not automatically better.
- Keep the model name in one place so switching is a one-line change.
