---
type: lesson
title: "The system prompt is a product surface"
minutes: 5
---

At a customer, the system prompt is not a technical detail. It decides what the assistant says to thousands of people: its tone, what it will and won't do, what it says when it doesn't know, and when it hands off to a human. Treat it like product copy and code at the same time.

## What a production system prompt covers

| Section | Example for Meridian's support bot |
|---|---|
| **Identity and audience** | "You are the support assistant for Meridian Logistics customers." |
| **Scope** | "Help only with deliveries, tracking, damage claims, invoices and addresses." |
| **Out of scope** | "For anything else, reply: `Sorry, I can only help with Meridian deliveries, invoices and claims.`" |
| **Facts and sources** | "Use only the information below / in the provided documents." |
| **Unknowns** | "If the answer isn't in the information, say you don't know and offer a human." |
| **Escalation** | "If the customer mentions injury, legal action or is very upset, tell them a human agent will contact them." |
| **Style and format** | "Plain sentences, at most 80 words, no markdown." |

## Fixed phrases are a feature

Exact, fixed wording for refusals and escalations ("Sorry, I can only help with...") lets your code and your evals **detect** those cases reliably. The UI can show a "Talk to a person" button whenever the escalation sentence appears; your test suite can check refusals with a simple string match.

## Who should review it

Not only you. The customer's support lead checks tone and policy. Legal or compliance checks claims and promises. The prompt is where the customer's rules get encoded, so they need to sign it off - and they'll want to change it later, which is why the next lesson puts it under version control.

## Keep it in a file

Don't bury the prompt as a string in Python. Put it in a text file that non-engineers can read, review and diff. The code loads it at startup.
