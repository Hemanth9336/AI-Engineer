---
type: lesson
title: "Truncation, pagination, and pointers to files"
minutes: 6
---

Filtering isn't always possible. Sometimes the model genuinely needs to walk a long list - every build artifact, every row of a table. Three patterns keep that from flooding the context.

## 1. Truncate - with a marker

Cut the result at a fixed size and **say so**:

```text
<first 4,000 characters>
[truncated: 38,412 more characters. Use search_log to find specific lines.]
```

Never truncate silently. A model that sees half a file without knowing it will reason confidently about the half it saw.

## 2. Paginate - let the model ask for more

Return one page and tell the model exactly how to get the next:

```text
build-0001.tar.gz
...
build-0050.tar.gz
page 1 of 5 (230 files). Call again with page=2 for more.
```

| Design choice | Recommendation |
|---|---|
| Page size | A sensible default (50) with a hard cap (100) |
| Order | Stable and documented - sorted, so page 2 never repeats page 1 |
| Footer | Current page, total pages, total items, and the exact next call |
| Last page | Say "End of listing." so the model stops |
| Bad page number | `error: page must be from 1 to 5` |

Pagination puts the model in control of cost: it reads page 1, often finds what it needs, and stops.

## 3. Pointers - write it to a file, return the path

For results that are big **and** needed in full - a 2 MB query export, a full test report - don't put them in context at all:

```text
Wrote 18,240 rows to /tmp/agent/export-7f3a.csv (2.1 MB).
Columns: id, service, status, latency_ms. Use read_file with offset/limit, or search_file, to inspect it.
```

The context gets a path and a summary; the data stays on disk where other tools (or a subagent, topic 25) can work through it piece by piece.

## Choosing between them

| Situation | Pattern |
|---|---|
| The model needs a few relevant items | Filter (previous lesson) |
| The model might need to browse | Paginate |
| One big blob, rarely read in full | Truncate with a marker |
| Big, needed in full, or for other tools | Pointer to a file |
