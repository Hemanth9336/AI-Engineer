---
type: lesson
title: "Asking for reasoning"
minutes: 8
---

The simplest version is one line added to your prompt: **"Think step by step."** It works. But when a script needs the answer, you also want the reasoning and the result to be easy to separate.

## Three ways to ask

**1. A plain request for steps**

```text
How many servers do we need? Work through it step by step before you answer.
```

Good for a human reader.

**2. Steps, then a marked final line**

```text
Work through the problem step by step, one step per line.
Then finish with a final line in exactly this form:
ANSWER: <number>
```

Now your code can ignore the steps and read only the last line:

```bash
sed -n 's/^ANSWER: *//p' reply.txt
```

**3. Tagged sections**

```text
Put your reasoning inside <thinking> tags, then the final answer inside <answer> tags.
```

Tags are easy to pull out with a script and make it obvious which part is which.

## Give it the facts in a clean form

Step-by-step reasoning only helps if the inputs are clear. List the facts, give units, and say exactly what is being asked:

```text
Facts:
- Peak traffic today: 5,000 requests per minute
- Expected growth next quarter: 20%
- One server handles 1,200 requests per minute
- We always keep 1 spare server
Question: how many servers do we need next quarter?
```

## Check the steps, not just the answer

When the answer matters, read the steps. If step 2 multiplies when it should divide, you have caught the error before it reached a capacity plan. Better still, re-do the arithmetic in code - models reason well, real code calculates exactly.

## Keep it proportionate

Reasoning costs output tokens and time. For a quick label or a one-line rewrite, skip it. For a multi-step estimate, an incident diagnosis, or a trade-off decision, it is worth every token. Now try it on a real capacity question.
