---
type: lesson
title: "Descriptions that trigger"
minutes: 12
---

Topic 014 built a skill. This topic is about the part that decides whether anyone ever benefits from it: **selection**. Claude chooses a skill from one line of text, and most "my skill doesn't work" reports are really "my skill never fired".

## What Claude actually sees

At session start Claude Code puts a **listing** into context, one line per skill:

```text
The following skills are available for use with the Skill tool:

- changelog-entry: Adds a changelog entry or release note to CHANGELOG.md under Unreleased...
- team-kit:review-checklist: Reviews a diff against the team checklist...
```

That line is all Claude knows until it calls the `Skill` tool with `{"skill": "changelog-entry"}`. The body of `SKILL.md`, its reference files, and its scripts are invisible at decision time. So the description has one job: let Claude match a request to the skill.

| Field | What it does in the listing |
|---|---|
| `description` | The main text. If omitted, Claude Code uses the first non-empty line of the body, which is rarely a good trigger |
| `when_to_use` | Appended to `description`. Good for trigger phrases and example requests |
| `name` | Defaults to the directory name. Plugin skills appear as `plugin:skill` |
| `disable-model-invocation: true` | Claude never picks it; only `/name` runs it. Use for side-effecting workflows such as deploys |
| `user-invocable: false` | Hidden from the `/` menu; only Claude picks it. Use for background knowledge |
| `paths` | Glob list. The skill activates automatically only when Claude works on matching files |

## Limits that silently remove your keywords

- **1,536 characters**: `description` plus `when_to_use` is cut at 1,536 characters in the listing. Words after the cut are never seen, so put the main use case first. (`skillListingMaxDescChars` changes the cap.)
- **Listing budget**: the whole listing gets about 1% of the context window. With many skills, Claude Code drops descriptions, starting with the skills you use least. The name survives and the keywords don't. `/doctor` estimates the listing's cost, and `skillListingBudgetFraction` raises the budget.
- **Broken YAML**: if the frontmatter doesn't parse, the skill loads with **empty metadata**. `/name` still works, but Claude can't match on a description that no longer exists. `claude plugin validate .` reports the parse error.
- **Frontmatter must start on line 1.** A blank line or a title before `---` turns the whole block into plain content.

## A description that triggers

Write it for the matcher, not for a catalog:

1. **Lead with the action and the object**: "Adds a changelog entry or release note to CHANGELOG.md under Unreleased."
2. **Name the phrases people actually say**: "changelog entry", "release note", "what changed", "under Unreleased". Users don't say "documentation helper".
3. **State the boundary**: "Not for general questions about changelogs or git history." Without a boundary, a broad description over-triggers on anything nearby.
4. **Stay well under the cap.** Two or three sentences is usually right.

| Before | After |
|---|---|
| `Helps with docs.` | `Adds a changelog entry or release note to CHANGELOG.md under the Unreleased section (Added, Changed, Fixed, Removed). Use when asked to add a changelog entry, write a release note, or record a change under Unreleased. Not for general questions about changelogs or git history.` |
| Matches nothing a user would type | Matches three phrasings, and leaves a related question alone |

## Commands this node introduces

The `description`, `when_to_use`, `disable-model-invocation`, `user-invocable`, and `paths` fields, the 1,536-character cap, `skillListingBudgetFraction`, and `/doctor` for the listing's cost.
