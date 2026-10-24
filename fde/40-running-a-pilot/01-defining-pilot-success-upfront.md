---
type: lesson
title: "Defining pilot success upfront"
minutes: 6
---

A **pilot** puts the system in front of real users, on real work, for a fixed time - to decide whether to roll it out. The single most important thing about a pilot is agreed **before** it starts: what success means.

## Why upfront

After the pilot, everyone has an opinion. The champion remembers the great answers; the sceptic remembers the bad one. Without criteria agreed in advance, the decision becomes political. With them, it's a reading of numbers you all signed up to.

## What to define

| Item | Example |
|---|---|
| **Use case and users** | Reply drafts for 6 supplier desk agents |
| **Duration** | 6 weeks - long enough for habits to form, short enough to keep focus |
| **Metrics with targets** | Quality, adoption, safety, efficiency - each with a number |
| **How each is measured** | The eval run, Zendesk reports, call logs - not "we'll see" |
| **Decision date and owner** | 15 June, Head of Supplier Operations |
| **Go criteria** | What must be true to roll out |
| **Stop criteria** | What ends the pilot early |

## Four kinds of metric

- **Quality** - is it right? Golden-set correctness, edit rate, faithfulness.
- **Adoption** - do people use it? Weekly active users, share of tickets with a draft used.
- **Safety** - does it stay inside the lines? Trap refusal, PII leaks, policy violations.
- **Efficiency** - does it move the business metric? Reply time, tickets per agent, cost per ticket.

A pilot with only quality metrics can "succeed" while nobody uses it. One with only adoption can succeed while it's quietly wrong. You need all four.

## Store it as data

Put the criteria in a file - `pilot.json` - in the repository. Weekly reports can then be generated against it, and nobody can quietly move the goalposts.
