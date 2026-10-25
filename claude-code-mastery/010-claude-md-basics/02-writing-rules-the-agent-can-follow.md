---
type: lesson
title: "Writing rules the agent can follow"
minutes: 14
---

A rule is only useful if you can tell whether it was followed. Write every line of `CLAUDE.md` so a reviewer could check it.

| Vague | Checkable |
|---|---|
| Format code properly | Use 4-space indentation; run `ruff format` before finishing |
| Test your changes | Run `python3 -m unittest` and report the result before you finish |
| Keep files organized | HTTP handlers live in `src/api/handlers/` |
| Mark ownership | Every new Python file starts with the line `# owner: payments-team` |

## Keep it short and structured

- **Under about 200 lines.** Every line costs context in every session, and long files reduce adherence. Move rules that matter for one area into a nested `CLAUDE.md` or a path-scoped rule.
- **Headings and bullets**, not paragraphs.
- **No contradictions.** If two lines conflict, the model may pick either.
- **Commands, not descriptions.** `make test` beats "we have tests".
- Leave notes for humans in HTML comments (`<!-- why this rule exists -->`) - they are stripped before the model sees the file.

## Prove it loads, then prove it works

1. Ask a question only `CLAUDE.md` can answer, in a fresh session.
2. Give a task that should trigger a rule **without mentioning the rule** in the prompt, and inspect the result.

If the rule did not apply, check that the file is where you started `claude` (or a parent), that its name is exactly `CLAUDE.md`, and that the rule is specific enough to act on.

## Commands this node introduces

`/context` lists the memory files that loaded at launch.
