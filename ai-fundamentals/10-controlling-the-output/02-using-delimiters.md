---
type: lesson
title: "Using delimiters"
minutes: 8
---

Most real prompts combine **your instructions** with **someone else's text**: release notes, a customer email, a log, a web page. If the two run together, the model can lose track of which is which.

## The problem

```text
Turn these release notes into a checklist. Release notes: Version 4.2 adds SSO.
Please make the checklist short. Run the migration before deploying...
```

Is "Please make the checklist short" your instruction, or a line from the notes? The model has to guess.

## The fix: wrap the data

**Delimiters** are clear markers around the text to process. Anything distinctive works; XML-style tags are the most popular because they are unambiguous and you can name them:

```text
Turn the release notes inside <notes> tags into a deployment checklist.

<notes>
Version 4.2 adds single sign-on.
Run the database migration before deploying.
</notes>
```

Other common delimiters:

```text
Triple quotes:  """ ... """
Triple backticks: ``` ... ```
Headings:       ### NOTES ### ... ### END NOTES ###
```

## Why it matters

1. **Clarity.** The model knows exactly where the data starts and stops.
2. **Several inputs.** `<ticket>`, `<customer_history>`, and `<policy>` can each be referred to by name: "Answer the ticket using only the policy."
3. **Safety.** Text inside the delimiters is data, not orders. If a customer email contains "ignore your instructions", the delimiters - plus a line telling the model to treat tagged content as data - make it much less likely to obey. Topic 22 goes deeper on this, called **prompt injection**.

## Building delimited prompts in code

Never paste the data in by hand. Build the message from the file, so it is exact:

```bash
jq -n --arg notes "$(cat notes.txt)" \
  '{model: "lab-fast", messages: [{role: "user",
    content: ("Turn the notes inside <notes> tags into a checklist.\n\n<notes>\n" + $notes + "\n</notes>")}]}'
```

`--arg` handles quotes and newlines in the data safely - something hand-written JSON gets wrong all the time. Now put both ideas together.
