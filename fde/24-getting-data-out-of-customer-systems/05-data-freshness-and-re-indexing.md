---
type: lesson
title: "Data freshness and re-indexing"
minutes: 5
---

An index is a **copy** of the customer's data, and copies go stale. Freshness is a requirement you agree with the customer - and then have to prove you meet.

## How fresh is fresh enough?

| Content | Typical requirement |
|---|---|
| Policies, help articles | Within a day of publishing |
| Product catalogue, prices | Hourly, or at publish time |
| Order status, stock levels | Real time - **don't index it; call the API as a tool** |
| Archived reports | One-off |

That last row matters: data that changes constantly belongs behind a **tool** (topic 23), not in a vector index.

## The incremental sync loop

Each run:

1. Read the current eligible rows from the source (not deleted, not blank).
2. Compare with the index by **id** and **updated_at**.
3. **Added** - new ids: embed and insert.
4. **Updated** - newer `updated_at`: re-embed and replace.
5. **Removed** - ids no longer eligible (deleted, archived, gone): delete from the index.
6. **Unchanged** - keep, without calling the embedding API.
7. Report the counts.

The report is your monitoring: a run that suddenly removes 90% of the index probably means a broken export, not a mass deletion - stop and check before you apply it. Production pipelines often refuse to apply changes above a threshold without a human.

## Re-index everything sometimes

Some changes affect **every** record: a new chunking strategy, a better cleaning rule, a new embedding model. These need a full rebuild - ideally into a new index that you switch to once it's complete and tested, so the assistant never serves a half-built index.

## Prove freshness

Log each sync with its timestamp and counts. "When was this article last indexed?" should be answerable in seconds - it's one of the first questions in any "why did the assistant say that?" investigation.
