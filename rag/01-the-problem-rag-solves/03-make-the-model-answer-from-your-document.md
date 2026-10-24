---
type: task
title: "Make the model answer from your document"
minutes: 11
---

## Set up

```bash
ailab status
mkdir -p /root/rag-start
cd /root/rag-start
```

## What to build

Prove the difference yourself, using this document:

> Full database backups are taken every Wednesday at 01:00. Incremental backups run on all other days.

The question: **"Which day are full database backups taken?"**

Do this:

1. Ask the question with `claude -p` **WITHOUT** giving the document, and save the reply to `/root/rag-start/cold-answer.txt`. Read it and notice it cannot name the real day - it either says it does not know, or talks about backups in general.
2. Ask again **with the document included** in the prompt, the way the previous lesson shows, and save the reply to `/root/rag-start/grounded-answer.txt`.
3. Compare the two files.

Press **Submit** when both files are in place.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Redirect the reply into a file: `claude -p "..." > cold-answer.txt`.
- For the second run, put the instruction, then `Document: ...`, then `Question: ...` in one quoted prompt.
- `diff cold-answer.txt grounded-answer.txt` shows the difference side by side.

</details>

<details><summary>Solution</summary>

```bash
cd /root/rag-start
claude -p "Which day are full database backups taken?" > cold-answer.txt
claude -p "Answer the question using only the document below.

Document: Full database backups are taken every Wednesday at 01:00. Incremental backups run on all other days.

Question: Which day are full database backups taken?" > grounded-answer.txt
cat cold-answer.txt
echo ---
cat grounded-answer.txt
```

</details>

## Check your work

```bash
D=/root/rag-start
[ "$(wc -w < $D/cold-answer.txt 2>/dev/null || echo 0)" -ge 3 ] && echo "✅ cold-answer.txt holds the reply without the document" || echo "❌ save the reply without the document to $D/cold-answer.txt"
[ "$(wc -w < $D/grounded-answer.txt 2>/dev/null || echo 0)" -ge 2 ] && echo "✅ grounded-answer.txt holds the reply with the document" || echo "❌ save the reply with the document to $D/grounded-answer.txt"
grep -qi 'wednesday' $D/grounded-answer.txt 2>/dev/null && echo "✅ with the document, the model names Wednesday" || echo "❌ grounded-answer.txt should name Wednesday - include the document in the prompt"
[ -s $D/cold-answer.txt ] && ! cmp -s $D/cold-answer.txt $D/grounded-answer.txt && echo "✅ the two replies differ" || echo "❌ the two files should hold two different replies"
[ "$(jq -s '[.[] | select(.ok and (.client | startswith("claude-cli")))] | length' /var/log/ailab/requests.jsonl 2>/dev/null || echo 0)" -ge 2 ] && echo "✅ the gateway served claude at least two requests" || echo "❌ run claude -p twice - the gateway has not seen both requests"
```

## What you learned

- A model cannot answer from facts it never saw - no wording of the question changes that.
- Put the document in the prompt and the same model answers exactly.
- That move - document first, then question - is the core of RAG.
