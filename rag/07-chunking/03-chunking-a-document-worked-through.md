---
type: lesson
title: "Chunking a document, worked through"
minutes: 6
---

Here is a complete chunker in a few lines.

```python
def chunk_text(text, size=500, overlap=100):
    chunks, start = [], 0
    while True:
        chunks.append(text[start:start + size])
        if start + size >= len(text):
            return chunks
        start += size - overlap
```

Test it where you can see every character:

```python
chunk_text("abcdefghij", size=4, overlap=1)
# ['abcd', 'defg', 'ghij']
chunk_text("short", size=500, overlap=100)
# ['short']                    - shorter than one chunk: one chunk
```

`d` and `g` each appear twice: that's the overlap.

## On the real handbook

```python
text = open("handbook.md").read()
chunks = chunk_text(text, 500, 100)
print(len(text), len(chunks), [len(c) for c in chunks])
```

```text
1710 5 [500, 500, 500, 500, 110]
```

Look at a boundary:

```text
end of chunk 2:    "...If your laptop is lost or stolen, report it to th"
start of chunk 3:  "ryption and lock after five minutes of inactivity. If your laptop is l..."
```

Chunk 2 cuts the key sentence mid-word, but thanks to the 100-character overlap, chunk 3 contains the whole sentence. Without overlap, the laptop rule would be split across two chunks and neither would match well.

## Give every chunk an ID

Later steps need to refer to chunks - to store them, show sources, and update them. Use the document name plus a zero-padded position:

```python
records = [{"id": f"handbook-{i:03d}", "index": i, "text": c} for i, c in enumerate(chunks)]
```

```json
[
  { "id": "handbook-000", "index": 0, "text": "# Northwind Employee Handbook\n\n## Working hours\n..." },
  { "id": "handbook-001", "index": 1, "text": "head for anything longer than three days..." }
]
```

Zero padding (`000`, `001` ... `010`) keeps IDs sorting in the right order.
