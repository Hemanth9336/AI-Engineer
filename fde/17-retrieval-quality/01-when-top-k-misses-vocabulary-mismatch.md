---
type: lesson
title: "When top-k misses: vocabulary mismatch"
minutes: 5
---

Embeddings are good at meaning and weak at **exact strings**. Customers are full of exact strings: product codes, error codes, abbreviations, internal project names, people's names.

Meridian's customs article says: *"Import duties are paid by the receiver unless the sender booked DDP (Delivered Duty Paid)."* A customer asks:

```text
Can we get DDP?
```

To a small embedding model, "DDP" is three letters with little meaning of its own. The question vector lands near generic "can we..." questions - support hours, address changes - and the customs article, the **only** one containing "DDP", ranks below them.

## Where this bites at customers

| Query contains | Example |
|---|---|
| Abbreviations | DDP, POD, SLA, KYC |
| Codes | Error E-4417, service XR7, policy P-114 |
| Names | A product line, a depot, a person |
| Rare jargon | Customer-specific terms that no public text uses |

Sometimes the embedding model does fine - a code that appears with a clear description often retrieves well. Sometimes it doesn't. **You find out by testing real queries**, not by assuming.

## How to reproduce it

1. Take the query and the term you expect to match.
2. List the documents that literally contain the term.
3. Check whether any of them is the vector top-1 (or in the top-k).

If the only document containing the term isn't near the top, that's a **keyword miss** - and adding keyword search (next lesson) is the fix. Reproducing it first matters: it gives you a failing case to prove the fix works, and a concrete example to show the customer.
