---
type: lesson
title: "Chunk size and overlap"
minutes: 6
---

Two numbers control chunking.

## Size

How long each chunk is - in characters here (production systems sometimes count tokens).

| Size | Good | Bad |
|---|---|---|
| Small (~200 chars) | Very precise matches | A fact may be cut off from its context ("it" - what is "it"?) |
| Medium (~500-1,000) | A paragraph or two: precise and self-contained | A good default |
| Large (2,000+) | Lots of context per hit | Blurry vectors, wasted prompt space, may exceed model limits |

For MiniLM, which reads about 256 tokens (roughly 1,000 characters), 500 characters is a safe default.

## Overlap

How many characters each chunk repeats from the end of the previous one.

```text
size=10, overlap=3

text:     abcdefghijklmnop
chunk 0:  abcdefghij
chunk 1:         hijklmnop
                 ^^^ repeated
```

Without overlap, a sentence that falls on a boundary is cut in two and **neither** chunk holds it whole. With overlap, the boundary region appears in both chunks, so a fact near the edge survives intact in at least one. A common choice is 10-20% of the size: 500 with 100.

## The windows

With size *s* and overlap *o*, chunks start at 0, *s - o*, 2(*s - o*), ... The **step** is *s - o*. Stop once a chunk reaches the end of the text.

```text
size=500, overlap=100, step=400, text of 1,710 characters

chunk 0:    0 -  500
chunk 1:  400 -  900
chunk 2:  800 - 1300
chunk 3: 1200 - 1700
chunk 4: 1600 - 1710   (the last one is shorter)
```

## Smarter splitters exist

Fixed character windows cut mid-word and mid-sentence. Better splitters cut at paragraph or sentence boundaries first - LangChain's `RecursiveCharacterTextSplitter`, which you'll use in topic 13, does exactly that. Building the simple version yourself first shows you what those tools are doing.
