---
type: lesson
title: "Asking for a format"
minutes: 8
---

When a person reads the answer, format is about comfort. When **code** reads the answer, format is everything. A model that returns a checklist one time and a paragraph the next will break your script.

## Name the format exactly

Common formats and how to ask for them:

| Want | Say |
|---|---|
| A bullet list | "Exactly 5 bullet points, each starting with '- '" |
| A checklist | "One item per line, each starting with '- [ ] '" |
| A numbered procedure | "Numbered steps, '1.', '2.', ..., one action per step" |
| A table | "A Markdown table with columns: Service, Owner, Status" |
| One value | "Reply with only the number, nothing else" |
| Data | "Valid JSON with keys host, port, status" (topic 15) |

## Control the length too

Length is part of format. Be precise:

- Count of items: "4 to 6 items".
- Words: "under 50 words", "one sentence".
- Per item: "each item under 12 words".

## Say what to leave out

Models like to be polite: "Sure! Here is your checklist:" at the top, "Let me know if you need anything else!" at the bottom. For a human that is harmless; for a script it is noise. Rule it out:

```text
Output only the checklist lines. No heading, no introduction, no closing sentence.
```

## Show the shape

A tiny template removes all doubt:

```text
Use exactly this format:
- [ ] <action>
- [ ] <action>
```

## Verify the shape in code

Even with a good prompt, check the output before you use it:

```bash
grep -c '^- \[ \] ' reply.txt        # how many checklist lines?
grep -vc '^- \[ \] ' reply.txt       # how many lines are something else?
```

If the check fails, your program can retry or flag the result instead of passing garbage along. Next: keeping the instructions and the text you want processed apart.
