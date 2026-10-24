---
type: lesson
title: "Sourcing real questions"
minutes: 5
---

The questions you invent are the ones you already know the answer to. Real users ask differently - shorter, messier, with typos, with context you didn't expect:

| You write | Customers write |
|---|---|
| "What is the procedure for reporting damage?" | "box came smashed what now" |
| "What are the support hours?" | "is anyone there on saturday??" |
| "How do I change the delivery address?" | "moved house last week, parcel still going to old flat" |

## Where real questions live

- **Support tickets** - the richest source. Months of real questions, often with the resolution attached.
- **Chat and email logs** - shorter, more casual.
- **Search logs** on the help centre - what people typed before giving up.
- **Agents' saved replies** - each one exists because the question comes up a lot.
- **The pilot itself** - once users try the assistant, every question is a candidate.

## From a ticket dump to eval cases

1. **Filter**: keep tickets that contain an actual question and were resolved with a known article.
2. **Extract**: take the question, not the greeting and backstory.
3. **De-duplicate**: fifty copies of "where is my parcel" are one case (plus a count telling you it matters).
4. **Count**: the frequency per topic tells you where the volume is - weight your eval set toward it.
5. **Review**: a human checks each candidate and writes the expected answer.

Steps 1-4 are code. Step 5 is a person. Never skip it - and strip personal data before tickets leave the customer's systems (topic 36).
