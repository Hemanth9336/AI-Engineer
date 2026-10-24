---
type: task
title: "Let the model call a tool"
minutes: 13
---

## Scenario

An on-call assistant should answer "is X healthy?" from live data, not from guesswork. You will give the model a `get_service_status` tool and run the tool loop by hand. The "live data" is the file `services.json`.

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/16-tools
cd /root/ai-lab/16-tools
cat > services.json <<'EOF'
{
  "checkout": {"status": "degraded", "error_rate": "4.2%", "since": "09:41 UTC"},
  "search":   {"status": "up", "error_rate": "0.1%", "since": "yesterday"},
  "payments": {"status": "up", "error_rate": "0.0%", "since": "yesterday"}
}
EOF
```

## What to build

1. Write `/root/ai-lab/16-tools/step1.json` for `lab-fast` with the user question **"Is the checkout service healthy right now?"** and a `tools` list containing one function, `get_service_status`, with a required string argument `service`. Send it and save the response to `step1-response.json`. Its `finish_reason` must be `tool_calls`.
2. **Run the tool yourself**: read the `service` argument from the tool call and look it up in `services.json`. Save the result (a JSON object) to `tool-result.json`.
3. Write `step2.json`: the step 1 messages, plus the assistant message from `step1-response.json` exactly as received, plus a `tool` message whose `tool_call_id` matches the call and whose `content` is the text of `tool-result.json`. Keep the same `tools`. Send it, save the response to `step2-response.json` and the reply to `answer.txt`.

The answer must say the service is **degraded**.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `jq -r '.choices[0].message.tool_calls[0].function.arguments | fromjson | .service' step1-response.json`
- `jq --arg s "$SVC" '.[$s]' services.json > tool-result.json` is your 'tool'.
- Build step 2 with `jq --slurpfile r step1-response.json --arg out "$(cat tool-result.json)" '.messages += [$r[0].choices[0].message, {role: "tool", tool_call_id: $r[0].choices[0].message.tool_calls[0].id, content: $out}]' step1.json`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/16-tools
jq -n '{
  model: "lab-fast",
  messages: [{role: "user", content: "Is the checkout service healthy right now?"}],
  tools: [{type: "function", function: {
    name: "get_service_status",
    description: "Get the current health of one production service.",
    parameters: {type: "object", properties: {service: {type: "string", description: "Service name, e.g. checkout"}}, required: ["service"]}
  }}]
}' > step1.json
curl -sS "$LAB_AI_URL/v1/chat/completions" -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" -d @step1.json -o step1-response.json
jq '.choices[0] | {finish_reason, tool_calls: .message.tool_calls}' step1-response.json
SVC=$(jq -r '.choices[0].message.tool_calls[0].function.arguments | fromjson | .service' step1-response.json)
jq --arg s "$SVC" '.[$s]' services.json > tool-result.json
jq --slurpfile r step1-response.json --arg out "$(cat tool-result.json)" \
  '.messages += [$r[0].choices[0].message, {role: "tool", tool_call_id: $r[0].choices[0].message.tool_calls[0].id, content: $out}]' \
  step1.json > step2.json
curl -sS "$LAB_AI_URL/v1/chat/completions" -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" -d @step2.json -o step2-response.json
jq -r '.choices[0].message.content' step2-response.json > answer.txt
cat answer.txt
```

</details>

## Check your work

```bash
D=/root/ai-lab/16-tools
jq -e '.model == "lab-fast" and (.messages[0].content | test("checkout"; "i")) and .tools[0].type == "function" and .tools[0].function.name == "get_service_status"' $D/step1.json >/dev/null 2>&1 && echo "✅ step1.json offers get_service_status to lab-fast" || echo "❌ step1.json needs model lab-fast, the checkout question, and a get_service_status function tool"
jq -e '.tools[0].function.parameters | .properties.service.type == "string" and (.required | index("service"))' $D/step1.json >/dev/null 2>&1 && echo "✅ the tool takes a required string argument 'service'" || echo "❌ give the tool a required string parameter named service"
jq -e '.choices[0].finish_reason == "tool_calls" and .choices[0].message.tool_calls[0].function.name == "get_service_status"' $D/step1-response.json >/dev/null 2>&1 && echo "✅ the model asked to call the tool" || echo "❌ step1-response.json should finish with tool_calls for get_service_status"
jq -e '.status == "degraded"' $D/tool-result.json >/dev/null 2>&1 && echo "✅ tool-result.json holds checkout's status from services.json" || echo "❌ look up the requested service in services.json and save it to tool-result.json"
jq -e --slurpfile r $D/step1-response.json '.messages[1].role == "assistant" and .messages[1].tool_calls[0].id == $r[0].choices[0].message.tool_calls[0].id' $D/step2.json >/dev/null 2>&1 && echo "✅ step 2 replays the model's tool call" || echo "❌ step2.json must include the assistant message from step1-response.json"
jq -e --slurpfile r $D/step1-response.json '.messages[2].role == "tool" and .messages[2].tool_call_id == $r[0].choices[0].message.tool_calls[0].id and (.messages[2].content | fromjson | .status == "degraded")' $D/step2.json >/dev/null 2>&1 && echo "✅ the tool message matches the call id and carries the result" || echo "❌ add a tool message with the matching tool_call_id and the text of tool-result.json"
jq -e '.tools[0].function.name == "get_service_status"' $D/step2.json >/dev/null 2>&1 && echo "✅ step 2 still offers the tool" || echo "❌ keep the tools list in step2.json"
[ -s $D/answer.txt ] && [ "$(cat $D/answer.txt)" = "$(jq -r '.choices[0].message.content' $D/step2-response.json 2>/dev/null)" ] && echo "✅ answer.txt holds exactly the reply in step2-response.json" || echo "❌ extract .choices[0].message.content from step2-response.json into answer.txt"
grep -qi 'degraded' $D/answer.txt 2>/dev/null && echo "✅ the final answer reports checkout as degraded" || echo "❌ the final answer should say checkout is degraded"
jq -se 'any(.[]; .ok and .finish_reason == "tool_calls" and (.tool_calls | index("get_service_status")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged the tool call" || echo "❌ the gateway has no tool call to get_service_status yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Tool calling lets the model ask your code for data or actions; it never runs anything itself.
- The loop is: tool call, you run it, a `tool` message with the matching id, then the answer.
- `arguments` is a JSON string - parse it, and validate it before running anything.
