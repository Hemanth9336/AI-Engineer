---
type: lesson
title: "Giving good instructions"
minutes: 6
---

Claude Code is fast, tireless and literal. Give it a vague request and it fills the gaps with guesses - reasonable ones, but not necessarily yours. Most "the agent got it wrong" stories are really "the request left it guessing".

## Vague vs clear

> add a low stock thing to the inventory code

Which file? What counts as low? What should it return - names, SKUs, whole rows? Sorted how? Tested? Claude will decide all of that for you.

> In inventory.py, add `low_stock(rows, threshold=5)` that returns the SKUs with qty below threshold, lowest qty first. Add a test to test_inventory.py. Done when `python3 -m unittest -q` passes.

Same feature, no guessing.

## The four parts of a brief

| Part | Answers | Example |
|---|---|---|
| **Goal** | What should exist when you're done? | "Add `low_stock(rows, threshold=5)` to inventory.py" |
| **Context** | What does it need to know that isn't obvious from the code? | "qty is already an int; tests run with `python3 -m unittest`" |
| **Constraints** | What must it not do? | "Standard library only. Don't touch data/." |
| **Done when** | How will you both know it worked? | "The tests pass and it returns these four SKUs for stock.csv" |

You won't write all four headings for a one-line fix. But run through them in your head before you press Enter, and say whichever ones Claude couldn't guess.

## Habits that pay off

- **Name files and functions.** "In `billing/invoice.py`, `total_cents()`" beats "the invoice code". In the console, `@billing/invoice.py` attaches the file.
- **Give an example.** One input with its expected output removes a whole class of misunderstandings.
- **Give it a way to check itself.** A test command or an expected output in "Done when" lets Claude verify its own work before reporting back - and it will.
- **Say what not to do.** Agents are eager. "Don't refactor anything else" saves you a surprise diff.
- **Ask for the shape of the answer.** "List the files only, one per line" when you want to pipe the result somewhere.

## Long briefs belong in files

For anything over a few lines, write the brief in a file and pass it in:

```bash
claude -p "$(cat brief.md)" --permission-mode acceptEdits
```

You can reread it, fix it, version it, and reuse it - and the checker for the next task reads it too.
