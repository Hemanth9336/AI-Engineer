---
type: task
title: "Measure a request's token usage"
minutes: 10
---

## Scenario

Before you put a log-summary prompt into a nightly job, finance asks what one call costs. Your model is priced at **$0.80 per million input tokens** and **$4.00 per million output tokens**.

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/14-usage /root/answers
cd /root/ai-lab/14-usage
cat > errors.log <<'EOF'
2026-10-24T02:00:01Z ERROR disk /var/lib/postgresql is 97% full
2026-10-24T02:00:05Z WARN  autovacuum took 412s on table orders
2026-10-24T02:01:10Z ERROR could not extend file "base/16384/2619": No space left on device
EOF
```

## What to build

1. Write `/root/ai-lab/14-usage/request.json` for `lab-fast` with a user message that contains the full text of `errors.log` and asks for a one-sentence summary. Send it and save the response to `response.json`.
2. Write `/root/answers/14-usage.txt` with exactly these four lines, using the numbers from `response.json`:

```text
prompt_tokens=<n>
completion_tokens=<n>
total_tokens=<n>
cost_usd=<cost with exactly 6 decimals>
```

`cost_usd` = prompt_tokens x 0.80 / 1,000,000 + completion_tokens x 4.00 / 1,000,000. Compute it with a tool (`awk` or `python3`), not by hand.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `P=$(jq .usage.prompt_tokens response.json)` stores a number in a shell variable.
- `awk -v p=$P -v c=$C 'BEGIN {printf "%.6f", p*0.80/1e6 + c*4.00/1e6}'` prints six decimals.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/14-usage
jq -n --arg log "$(cat errors.log)" '{model: "lab-fast", messages: [{role: "user", content: ("Summarize these errors in one sentence:\n\n" + $log)}]}' > request.json
curl -sS "$LAB_AI_URL/v1/chat/completions" -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" -d @request.json -o response.json
P=$(jq .usage.prompt_tokens response.json)
C=$(jq .usage.completion_tokens response.json)
T=$(jq .usage.total_tokens response.json)
COST=$(awk -v p="$P" -v c="$C" 'BEGIN {printf "%.6f", p*0.80/1e6 + c*4.00/1e6}')
printf 'prompt_tokens=%s\ncompletion_tokens=%s\ntotal_tokens=%s\ncost_usd=%s\n' "$P" "$C" "$T" "$COST" > /root/answers/14-usage.txt
cat /root/answers/14-usage.txt
```

</details>

## Check your work

```bash
D=/root/ai-lab/14-usage; A=/root/answers/14-usage.txt; R=$D/response.json
jq -e --arg log "$(cat $D/errors.log)" '.model == "lab-fast" and (.messages[-1].content | contains($log))' $D/request.json >/dev/null 2>&1 && echo "✅ request.json sends the whole log to lab-fast" || echo "❌ request.json needs model lab-fast and the full text of errors.log"
jq -e '.usage.total_tokens > 0' $R >/dev/null 2>&1 && echo "✅ response.json has a usage block" || echo "❌ save the response to response.json"
[ "$(grep -c . $A 2>/dev/null)" = 4 ] && echo "✅ 14-usage.txt has four lines" || echo "❌ /root/answers/14-usage.txt needs exactly four lines"
for k in prompt_tokens completion_tokens total_tokens; do v=$(jq ".usage.$k" $R 2>/dev/null); [ -n "$v" ] && grep -qx "$k=$v" $A 2>/dev/null && echo "✅ $k=$v matches the response" || echo "❌ $k must equal .usage.$k in response.json"; done
WANT=$(jq -r '.usage | (.prompt_tokens * 0.80 + .completion_tokens * 4.00) / 1000000' $R 2>/dev/null | awk '{printf "%.6f", $1}')
[ -n "$WANT" ] && grep -qx "cost_usd=$WANT" $A 2>/dev/null && echo "✅ cost_usd=$WANT is right" || echo "❌ cost_usd should be prompt_tokens x 0.80/1e6 + completion_tokens x 4.00/1e6, with 6 decimals"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- `usage` gives prompt, completion, and total tokens for every call.
- Cost is input tokens x input price plus output tokens x output price, per million.
- Output tokens usually cost several times more than input tokens.
