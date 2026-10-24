---
type: lesson
title: "The leak: search ignores permissions"
minutes: 5
---

At most customers, not everyone may read everything. Drivers see driver documents. HR sees salary bands. Finance sees margins. Their intranet, SharePoint or Confluence enforces that with access control lists.

Then someone builds an assistant: export every document, embed it all into **one index**, and let everyone ask questions. Vector search has no idea who's asking. A driver asks:

```text
What do D2 drivers earn?
```

The most similar chunk is the HR salary-band document. Retrieval returns it, the model answers from it, and a driver has just read confidential pay data - through a chatbot that "only answers questions".

## Why this is the worst bug you can ship

- **It's invisible in demos.** The demo user is an admin who can see everything anyway.
- **It doesn't look like a hack.** No injection, no exploit - a normal question.
- **It's a data breach.** Salary data, customer credit limits, disciplinary records, financial results before publication. At a bank or hospital, a regulatory incident.
- **The answer can hide the source.** Even without citations, the model paraphrases the confidential fact.

## The rule

> The assistant must never retrieve a document the asking user couldn't open themselves.

Permissions must be enforced **in retrieval**, before anything reaches the model. Asking the model "don't reveal confidential documents" doesn't work: once the text is in the prompt, it can come out - by accident or through prompt injection.

## Reproduce it first

As with any bug, prove it exists: a toy index with group-tagged documents, a user who shouldn't see some of them, and a question that pulls one out. That's the next task - and the failing case becomes your regression test.
