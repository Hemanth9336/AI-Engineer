---
type: lesson
title: "A proof of concept in days"
minutes: 8
---

A **proof of concept (PoC)** answers one question: *can this work on the customer's data?* Not "is it production-ready", not "does it scale" - just: is the core idea sound enough to invest in?

## What a good PoC looks like

- **Days, not weeks.** Two to five days of work. Speed is the point: it lets the customer decide quickly and cheaply.
- **Real data.** A sample of the customer's actual documents and questions. A PoC on public data proves nothing about their problem.
- **The core loop only.** For a RAG assistant: retrieve, generate, cite, refuse. Nothing else.
- **A few honest results.** Ten real questions, with the failures shown next to the successes.
- **Written-down shortcuts.** A short note listing everything you cut - so nobody mistakes it for a product.

## What to keep, even in a PoC

| Keep | Because |
|---|---|
| **Citations** | They're how the customer will judge whether to trust it |
| **Refusal on out-of-scope** | Otherwise the demo invents answers - and someone will try a trap question |
| **Keys out of code** | A leaked key in a shared PoC repo is still a leaked key |
| **A tiny eval** | 10-20 questions with expected answers; the start of the golden set |

## What to cut

UI polish, authentication, integrations, scaling, persistence, monitoring, edge cases in ingestion. Each one can come later - **if** the PoC earns it.

## The PoC is a sales and learning tool

It's how the customer sees what's possible, and how you learn what their data is really like - messy exports, contradicting documents, questions nobody expected. Both are worth more than the code, which you should expect to throw away.
