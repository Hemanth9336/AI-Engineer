---
type: lesson
title: "Storing vectors in sqlite, worked through"
minutes: 7
---

SQLite comes with Python (`import sqlite3`) and stores a whole database in one file. A vector is a list of floats; the simplest way to store it is as **JSON text**.

## Create the table

```python
import json
import sqlite3

db = sqlite3.connect("store.db")
db.execute("CREATE TABLE IF NOT EXISTS chunks (id TEXT PRIMARY KEY, text TEXT, embedding TEXT)")
```

- `id TEXT PRIMARY KEY` - every ID can exist only once.
- `IF NOT EXISTS` - safe to run again.

## Upsert the chunks

```python
records = json.load(open("vectors.json"))
db.executemany(
    "INSERT OR REPLACE INTO chunks (id, text, embedding) VALUES (?, ?, ?)",
    [(r["id"], r["text"], json.dumps(r["embedding"])) for r in records],
)
db.commit()
print(db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0], "chunks stored")
```

```text
5 chunks stored
```

`INSERT OR REPLACE` is SQLite's upsert: a new ID is inserted, an existing ID is overwritten. Run the script twice and you still have 5 rows - no duplicates. That property is called **idempotent**: running it again gives the same result. Indexing jobs should always be idempotent, because they get re-run whenever documents change.

The `?` placeholders let SQLite insert the values safely - never build SQL by pasting strings together.

## Look inside

```bash
sqlite3 store.db "SELECT id, substr(text, 1, 40), length(embedding) FROM chunks"
```

```text
handbook-000|# Northwind Employee Handbook  ## Wor|8312
handbook-001|head for anything longer than three day|8297
...
```

Each embedding is stored as a few kilobytes of JSON text. A production store would use a compact binary format, but JSON is easy to read and good enough for thousands of chunks.
