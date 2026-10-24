---
type: lesson
title: "When similar is not relevant"
minutes: 5
---

Semantic search returns the most **similar** text. That's not always the text that **answers the question**. Knowing the failure patterns lets you spot them in a customer's data in minutes.

## Common failures

| Pattern | Example | Why it happens |
|---|---|---|
| **Same topic, wrong fact** | "What's the pallet weight limit?" retrieves "Pallets must be shrink-wrapped" | Both are about pallets; the weight sentence lives in another chunk |
| **Exact terms and codes** | "Can we get DDP?" misses the customs article that mentions DDP once | Embeddings capture meaning, and abbreviations or codes carry little of it |
| **Negation** | "Which items are *not* accepted?" matches accepted-items text | Embeddings barely register "not" |
| **Outdated version** | Last year's price list scores as high as this year's | Similarity knows nothing about dates |
| **Generic boilerplate** | Every chunk with the same legal footer looks alike | Repeated text dominates the vector |
| **Question vs statement style** | A FAQ written as questions matches other questions better than answers | Phrasing affects the vector too |
| **Nothing answers it** | "Do you sell coffee?" still returns a "best" match | Search always returns k results |

## What fixes what

- **Codes, names, abbreviations** -> hybrid search: add keyword matching (topic 17).
- **Same topic, wrong fact** -> better chunking (topic 16) and reranking (topic 17).
- **Outdated versions** -> metadata (dates, status) and filtering; remove superseded documents from the index.
- **Boilerplate** -> clean documents before embedding (topic 16).
- **Nothing answers it** -> score thresholds and an explicit "I don't know" in the prompt (topic 18).

## The FDE habit

Before tuning anything, collect **20-30 real questions** and look at what retrieval returns for each. You'll see which of these patterns dominate this customer's data, and fix those first.
