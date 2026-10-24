---
type: lesson
title: "Evals as the contract with the customer"
minutes: 7
---

Customers don't buy a model. They buy an outcome: "answers our staff can trust", "fewer tickets", "faster claims". An eval set turns that vague promise into something both sides can check.

## The eval set is the spec

Traditional software has requirements documents. AI systems have **examples**. Writing the eval set *with* the customer forces the conversations you'd otherwise have too late:

- *"Should it answer questions about invoices, or send them to finance?"* - becomes an out-of-scope case.
- *"What counts as correct - the exact fee, or 'there is a fee'?"* - becomes the scoring rule.
- *"Is a refusal acceptable when the docs are unclear?"* - becomes an expected answer.

## What goes in the agreement

| Item | Example |
|---|---|
| The eval set | 120 questions: 80 common, 25 hard, 15 out of scope |
| The metrics | Answer correctness, refusal on out-of-scope, citation validity |
| The bar | 90% correct, 100% of out-of-scope refused, 0 invalid citations |
| Who grades | Customer's support leads review a sample of judge verdicts |
| When it runs | Before every release and every prompt change |

## Why this protects you

Without an agreed eval, "it doesn't work" can't be disproved and "it's done" can't be proved. With one, a complaint becomes a test case: add it to the set, fix it, show the score. Scope creep becomes visible too - new kinds of questions mean new eval cases and a conversation about the plan.

> An eval set the customer helped write is the closest thing an AI project has to a signed spec.
