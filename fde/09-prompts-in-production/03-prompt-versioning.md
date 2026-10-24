---
type: lesson
title: "Prompt versioning"
minutes: 5
---

Six weeks into a pilot, someone edits the system prompt to fix one complaint. Quality drops on three other kinds of question. Nobody can say what changed, when, or what the old prompt was.

The fix is the same discipline you apply to code: **every prompt change is a new version you can name, diff and roll back.**

## A simple layout

```text
prompts/
  support/
    v1.txt
    v2.txt
    current        <- contains one line: v2
```

- **Never edit a released version.** Copy it to `v3.txt`, change the copy.
- **`current`** says which version production uses. Rolling back is changing one word.
- **Commit everything to git.** The history shows who changed what and why.
- **Log the version with every request.** When a bad answer comes in, you know exactly which prompt produced it.

## Load by name and version

```python
from pathlib import Path

PROMPTS = Path(__file__).parent / "prompts"

def load_prompt(name, version=None):
    folder = PROMPTS / name
    version = version or (folder / "current").read_text().strip()
    return version, (folder / f"{version}.txt").read_text()
```

Returning the version along with the text makes it hard to forget to log it.

## Changelog in the commit, or in a file

```text
v2  2026-03-12  Add escalation for injury and legal threats (ticket SUP-331).
v1  2026-02-27  First pilot prompt.
```

## What counts as a change

Anything that could change behaviour: wording, examples, the model name, temperature, the retrieved-document format. Many teams store the model and settings next to the prompt, so a "version" means the whole configuration.

Later, in the evals section, you'll run the test suite against a new version **before** switching `current`. That's what makes prompt changes safe.
