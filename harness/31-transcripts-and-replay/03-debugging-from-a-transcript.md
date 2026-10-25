---
type: lesson
title: "Debugging from a transcript"
minutes: 6
---

Reading transcripts is a skill. The goal is to find the **first wrong turn** - the earliest step where things went off track - because that's where the fix goes. The final wrong answer is usually just the consequence.

## Read it like a detective

1. **Start at the end.** What was wrong with the result? ("Answered 8080; the real port is 8081.")
2. **Walk back through the tool results.** At each step ask: *did the model have what it needed?* Look at what it **saw**, not what it said.
3. **Find the first step where the information or the decision went wrong.** Everything after it is downstream.
4. **Classify the cause**, because the category tells you where the fix lives.

## Where wrong turns come from

| Category | Looks like | Fix lives in |
|---|---|---|
| `prompt` | The rules told it to do the wrong thing, or contradicted each other | The system prompt (topic 16) |
| `tool_description` | It picked the wrong tool, or passed bad arguments, because the description misled it | The schema (topic 12) |
| `tool_result` | The tool returned too little, too much, a misleading error, or a truncated result | The tool's code (topic 13) |
| `model_reasoning` | It had the right information and still concluded wrongly | Verification (topic 27), a stronger model, or a clearer result format |
| `harness_loop` | The loop dropped messages, stopped early, or retried wrongly | The loop (topics 8-10) |

The most common surprise: a wrong answer that looks like `model_reasoning` is often a `tool_result` problem. If the port line was cut off before the model saw it, "8080" is a reasonable guess - the model didn't fail, the harness starved it.

## Questions to ask at each step

- Did the tool return what the model asked for? Complete? Truncated? An error disguised as data?
- Was the right file read, or a similar-looking one?
- Did the model's next action follow from what it just saw?
- Did anything important **disappear** between steps (compaction, budget drops)?

## Then close the loop

Write down the wrong step, the category, the evidence and the fix - and turn the failure into a **golden task** (topic 30), so the fix stays fixed.
