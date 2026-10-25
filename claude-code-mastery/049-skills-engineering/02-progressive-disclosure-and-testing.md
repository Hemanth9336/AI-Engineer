---
type: lesson
title: "Progressive disclosure and testing"
minutes: 12
---

A skill loads in three stages, and good skills put each kind of content in the right stage.

| Stage | When it loads | What belongs there |
|---|---|---|
| 1. Listing | Every session, always | `name` and `description` only: one line, trigger words |
| 2. `SKILL.md` body | When the skill is invoked | The procedure: short numbered steps, decisions, which file or script to use next |
| 3. Supporting files | Only when the body sends Claude there | Long reference (style guides, API tables), examples, and scripts |

Keeping `SKILL.md` short is not just tidiness. The body is added to the conversation on invocation and **isn't re-read** on later turns, and after compaction only the start of it may survive. Put the must-follow steps at the top, keep the body well under the documented 500-line ceiling, and move bulk into files:

```text
.claude/skills/changelog-entry/
├── SKILL.md            # 10-30 lines: when, steps, pointers
├── style.md            # the full style guide, read on demand
└── scripts/
    └── add_entry.py    # deterministic work, executed rather than read
```

## Scripts beat instructions for deterministic work

Inserting a line under the right heading is easy to get subtly wrong in prose. A script does it the same way every time, and only its **output** enters context. Point at it with `${CLAUDE_SKILL_DIR}`, which expands to the skill's folder in the body and in `allowed-tools`. Using the same path in both places means the script runs without a permission prompt:

```yaml
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/add_entry.py *)
```

```markdown
Insert the entry with `python3 ${CLAUDE_SKILL_DIR}/scripts/add_entry.py <Type> "<text>"`.
```

## Testing selection

Treat triggering as behavior and test it like behavior:

1. **Write cases**: several prompts that *should* fire the skill, phrased the way users talk without naming the skill, and at least one nearby prompt that *should not*.
2. **Run each headless** with `--output-format stream-json --verbose`, which streams every tool call.
3. **Extract the decision**: the first `tool_use` named `Skill`, and its `input.skill`.

```bash
claude -p "Write a release note for the upload fix" --output-format stream-json --verbose < /dev/null > run.jsonl
jq -r 'select(.type == "assistant") | .message.content[]? | select(.type == "tool_use" and .name == "Skill") | .input.skill' run.jsonl
```

4. **Compare to expectations** and fail loudly on any mismatch, so a description edit that breaks triggering is caught like a failing test.

Quick manual checks: ask "What skills are available?" in a session, invoke `/changelog-entry` directly to separate "doesn't trigger" from "doesn't work", and use `--debug` for parse errors. `claude plugin validate .` checks every `SKILL.md` under `.claude/` without starting a session.

## Commands this node introduces

`${CLAUDE_SKILL_DIR}`, `allowed-tools` Bash rules for bundled scripts, `--output-format stream-json --verbose` to observe Skill calls, and `claude plugin validate .` for project skills.
