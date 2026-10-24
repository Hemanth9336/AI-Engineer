---
type: lesson
title: "What belongs in the system prompt"
minutes: 6
---

The system prompt is the one piece of text the harness sends at the top of **every** call. It's the agent's job description, rulebook and style guide - and the only instructions guaranteed to survive any amount of history and compaction.

## The sections that earn their place

| Section | What it says | Example |
|---|---|---|
| **Role** | Who the agent is, for whom, where | "You are Stackline's support agent, in a customer chat window." |
| **Tools** | When to use each tool - the policy, not the schema | "Use lookup_account for questions about their own account." |
| **Rules** | Hard constraints, each with a reason | "Never promise a refund; the billing team decides." |
| **When stuck** | What to do instead of guessing or looping | "After two failed tries, open a ticket." |
| **Answer format** | Length, structure, what to include | "At most four sentences. Include the ticket number." |

## What does not belong

| Don't put in the system prompt | Put it here instead |
|---|---|
| API keys, passwords, internal URLs with tokens | Nowhere near the model (topic 24) |
| The whole help center | Retrieval, per task (topic 20) |
| Data about this particular user | The conversation or a tool result |
| Tool parameter details | The tool's own schema and descriptions |
| Long histories of "also, never..." patches | A cleaned-up rules section, tested with evals |

## The system prompt in the harness

Keep it in a **file**, not a string buried in code:

```python
SYSTEM = (Path(__file__).parent / "system_prompt.md").read_text()
```

- You can review prompt changes in pull requests like code.
- You can version it and run evals before and after a change (topic 33).
- Non-engineers can read and improve it.

## Size

Every token in the system prompt is paid on every step. A focused 300-600 word prompt beats a 3,000-word one that tries to anticipate everything - the model follows a short, well-ordered set of rules more reliably than a long one, and the tools, retrieval and gates handle the rest.
