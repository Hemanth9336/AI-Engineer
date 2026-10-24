---
type: task
title: "Talk to the AI"
minutes: 10
---

## Scenario

Your practice machine has **`claude`**, the terminal command for Claude Code, already pointed at the lab's AI gateway. Before any code, use it the simplest way: ask a question and read the answer.

## Set up

This needs the lab from [setup](../../setup/README.md): run `ailab status` and expect `gateway: up`. Then create the folder for this topic:

```bash
ailab status
mkdir -p /root/ai-lab/04-basics
cd /root/ai-lab/04-basics
```

## What to build

`claude -p "your question"` sends one prompt, prints the reply, and exits - no chat window. `--model` picks a lab model; without it you get the default, `lab-fast`.

1. Ask: **Explain what a token is in a large language model, in two sentences.** Save the reply to `/root/ai-lab/04-basics/token.txt`.
2. Ask the **same question** again with `--model lab-smart` and save that reply to `/root/ai-lab/04-basics/token-smart.txt`.
3. Count the words in each reply with `wc -w` and write them to `/root/answers/04-words.txt` as two lines:

```text
fast_words=<words in token.txt>
smart_words=<words in token-smart.txt>
```

Read both replies. Different models, different wording - same idea.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Redirect the output: `claude -p "..." > token.txt`.
- `wc -w < token.txt` prints just the number, with no file name.
- `ailab log` shows the requests the gateway served, including which model each used.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/04-basics
claude -p "Explain what a token is in a large language model, in two sentences." > token.txt
claude -p --model lab-smart "Explain what a token is in a large language model, in two sentences." > token-smart.txt
cat token.txt token-smart.txt
printf 'fast_words=%s\nsmart_words=%s\n' "$(wc -w < token.txt | tr -d ' ')" "$(wc -w < token-smart.txt | tr -d ' ')" > /root/answers/04-words.txt
cat /root/answers/04-words.txt
ailab log 5
```

</details>

## Check your work

```bash
D=/root/ai-lab/04-basics; LOG=/var/log/ailab/requests.jsonl
[ "$(wc -w < $D/token.txt 2>/dev/null || echo 0)" -ge 5 ] && echo "✅ token.txt holds a real reply" || echo "❌ save the reply from claude -p to $D/token.txt"
[ "$(wc -w < $D/token-smart.txt 2>/dev/null || echo 0)" -ge 5 ] && echo "✅ token-smart.txt holds a real reply" || echo "❌ ask again with --model lab-smart and save it to $D/token-smart.txt"
jq -se 'any(.[]; .ok and (.client | startswith("claude-cli")) and .model == "lab-fast")' $LOG >/dev/null 2>&1 && echo "✅ the gateway served claude a request on lab-fast" || echo "❌ run claude -p without --model so it uses lab-fast"
jq -se 'any(.[]; .ok and (.client | startswith("claude-cli")) and .model == "lab-smart")' $LOG >/dev/null 2>&1 && echo "✅ the gateway served claude a request on lab-smart" || echo "❌ run claude -p --model lab-smart ..."
F=/root/answers/04-words.txt
[ "$(sed -n 's/^fast_words=//p' $F 2>/dev/null)" = "$(wc -w < $D/token.txt 2>/dev/null | tr -d ' ')" ] && echo "✅ fast_words matches token.txt" || echo "❌ fast_words= must be the output of wc -w < token.txt"
[ "$(sed -n 's/^smart_words=//p' $F 2>/dev/null)" = "$(wc -w < $D/token-smart.txt 2>/dev/null | tr -d ' ')" ] && echo "✅ smart_words matches token-smart.txt" || echo "❌ smart_words= must be the output of wc -w < token-smart.txt"
```

## What you learned

- `claude -p "..."` sends one prompt to a model and prints the reply - handy in scripts.
- `--model` switches models; the same question gets a different answer from each.
- The gateway records every request, which is how the checker knew what you ran.
