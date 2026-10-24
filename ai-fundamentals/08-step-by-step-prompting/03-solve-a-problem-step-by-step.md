---
type: task
title: "Solve a problem step by step"
minutes: 13
---

## Scenario

Your manager asks how many API servers to budget for next quarter. You want the model's working, not just a number, and you want a script to be able to read the final answer.

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/08-steps
cd /root/ai-lab/08-steps
cat > problem.txt <<'EOF'
Facts:
- Peak traffic today: 5,000 requests per minute
- Expected traffic growth next quarter: 20%
- One server handles 1,200 requests per minute at peak
- We always keep 1 extra server as spare capacity
Question: how many servers do we need next quarter?
EOF
```

## What to build

1. Write `/root/ai-lab/08-steps/steps.json` for `lab-fast`. Its user message must contain the full text of `problem.txt` and ask the model to work **step by step, one step per line**, and to end with a final line in exactly this form: `ANSWER: <number>`.
2. Send it, save the response to `steps-response.json` and the reply text to `steps.txt`.
3. Extract the number from the `ANSWER:` line into `/root/answers/08-servers.txt` (just the number).

Work it out yourself too. Does the model's working match yours?

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `jq -n --arg p "$(cat problem.txt)" '{model: "lab-fast", messages: [{role: "user", content: ($p + "\n\n...")}]}'` builds the request from the file.
- `sed -n 's/^ANSWER: *//p' steps.txt` prints what follows `ANSWER:`.
- Expected: 5,000 x 1.2 = 6,000; 6,000 / 1,200 = 5; plus 1 spare = 6.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/08-steps
jq -n --arg p "$(cat problem.txt)" '{
  model: "lab-fast",
  temperature: 0,
  messages: [{role: "user", content: ($p + "\n\nWork through this step by step, one step per line. Then finish with a final line in exactly this form:\nANSWER: <number>")}]
}' > steps.json
curl -sS "$LAB_AI_URL/v1/chat/completions" -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" -d @steps.json -o steps-response.json
jq -r '.choices[0].message.content' steps-response.json > steps.txt
cat steps.txt
sed -n 's/^ANSWER: *//p' steps.txt | tr -d ' .' > /root/answers/08-servers.txt
cat /root/answers/08-servers.txt
```

</details>

## Check your work

```bash
D=/root/ai-lab/08-steps; R=$D/steps.json
jq -e --arg p "$(cat $D/problem.txt)" '.model == "lab-fast" and (.messages[-1].content | contains($p))' $R >/dev/null 2>&1 && echo "✅ the request contains the whole problem" || echo "❌ steps.json needs model lab-fast and a user message containing all of problem.txt"
jq -e '.messages[-1].content | test("step by step"; "i") and test("ANSWER: <number>")' $R >/dev/null 2>&1 && echo "✅ the prompt asks for steps and an ANSWER: line" || echo "❌ ask for step-by-step working and a final line ANSWER: <number>"
[ -s $D/steps.txt ] && [ "$(cat $D/steps.txt)" = "$(jq -r '.choices[0].message.content' $D/steps-response.json 2>/dev/null)" ] && echo "✅ steps.txt holds exactly the reply in steps-response.json" || echo "❌ extract .choices[0].message.content from steps-response.json into steps.txt"
[ "$(grep -c . $D/steps.txt 2>/dev/null)" -ge 3 ] && echo "✅ the reply shows its working over several lines" || echo "❌ the reply should show several lines of working"
tail -n 1 $D/steps.txt 2>/dev/null | grep -Eq '^ANSWER: *6\.?$' && echo "✅ the last line is ANSWER: 6" || echo "❌ the last line should be ANSWER: 6 - got '$(tail -n 1 $D/steps.txt 2>/dev/null)'"
[ "$(tr -d '[:space:]' < /root/answers/08-servers.txt 2>/dev/null)" = "6" ] && echo "✅ 08-servers.txt says 6" || echo "❌ write the number from the ANSWER: line to /root/answers/08-servers.txt"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Asking for step-by-step working makes multi-step answers more accurate and checkable.
- A marked final line (`ANSWER: ...`) lets a script read the result and skip the working.
- Check the steps yourself - visible reasoning is only useful if someone reads it.
