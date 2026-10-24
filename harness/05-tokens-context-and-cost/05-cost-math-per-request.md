---
type: lesson
title: "Cost math per request"
minutes: 5
---

Every harness design decision - how many steps, how big the tool results, which model - shows up on one number: **cost per task**. The math is simple once you think in tokens.

## One request

Providers price input and output tokens separately, per million tokens:

```text
cost per request = input_tokens  / 1,000,000 x input_price
                 + output_tokens / 1,000,000 x output_price
```

Output tokens usually cost **3-5x** more than input tokens.

## One agent task = many requests

An agent re-sends its growing history on every step, so a task's cost is a **sum over steps**, and input tokens dominate:

```text
step   input   output
  1      800      60
  2    1,400      50
  3    2,900      80     <- a file was read
  4    3,100      40
total  8,200     230
```

With a mid-size model at **$0.40** input and **$1.60** output per million:

```text
input:  8,200 / 1,000,000 x 0.40 = $0.00328
output:   230 / 1,000,000 x 1.60 = $0.00037
per task                         = $0.00365
```

Run it 5,000 times a day for 30 days: **150,000 tasks, about $547 a month**. Let the same agent take 12 steps instead of 4 and the history grows on each one - the bill roughly triples, with the same model and the same prices.

## Where the tokens hide

| Source | Why it grows |
|---|---|
| System prompt and tool definitions | Sent on **every** step |
| History | Every step adds to it, and every later step re-sends it |
| Tool results | One large result is paid for again on each later step |
| Steps | A runaway loop multiplies everything |
| Retries | A failed call that retries is paid twice |

## Measure, then multiply

Record `usage` on each step of 20-50 realistic tasks, sum per task, average, then multiply by volume. Keep the assumptions next to the total so anyone can see which lever - steps, result size or model - moves the bill.
