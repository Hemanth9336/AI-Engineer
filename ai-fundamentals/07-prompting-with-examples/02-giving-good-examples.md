---
type: lesson
title: "Giving good examples"
minutes: 8
---

A model copies your examples very literally - including their mistakes. A few careful examples beat many sloppy ones.

## Rules for good examples

1. **Match the output exactly.** If your code expects `outage`, every example answer is exactly `outage` - not `Outage.` or `Category: outage`.
2. **Cover each label at least once.** If one category never appears, the model is less likely to use it.
3. **Include a tricky case.** Show the judgement call you care about: "My card expired so I can't log in" - is that billing or access? Decide, and show it.
4. **Vary the inputs.** Different lengths, wording, and tone, so the model learns the task rather than the surface pattern.
5. **Keep them realistic.** Examples that look like real data teach real behaviour.

## Watch for accidental patterns

Models notice patterns you did not intend:

- If every example answer is `billing`, the model leans toward `billing`.
- If examples always get longer, so might the answers.
- If the last example is always the same label, the next answer may repeat it.

Mix the order of labels and keep lengths similar.

## Examples in a single message

You can also put examples inside one user message, clearly separated:

```text
Classify each message as billing, outage, or access. Answer with one word.

Message: I was charged twice this month.
Category: billing

Message: I reset my password and still can't sign in.
Category: access

Message: The dashboard has been blank for everyone since 9am.
Category:
```

Ending on `Category:` invites the model to complete the pattern. This style works anywhere, including chat apps. The message-pair style from the last lesson is cleaner over the API, because each example is a separate turn.

## Test with inputs you did not show

Examples prove nothing about themselves. Always try the prompt on new inputs - especially awkward ones - before you trust it in a script. That is the next task.
