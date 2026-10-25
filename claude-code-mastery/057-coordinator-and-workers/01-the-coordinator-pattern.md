---
type: lesson
title: "The coordinator pattern"
minutes: 19
---

In a fan-out, every worker does the same job. In a **coordinator** pipeline, one agent (the coordinator, which is your main `claude -p` session) breaks a deliverable into stages, hands each stage to the worker built for it, and assembles the results into one validated output.

```text
relnotes.sh v2.3.0 HEAD 2.4.0
  └─ git log → commits.txt (numbered)
  └─ claude -p (coordinator, --json-schema)
        ├─ Agent(commit-classifier): numbered commits → {"1": "feature", "2": "fix", ...}
        ├─ Agent(notes-writer): only the user-facing commits → one line each
        └─ structured_output: {version, breaking[], features[], fixes[], internal_count}
  └─ render.py → RELEASE_NOTES.md
```

## Workers inline with `--agents`

When the workers exist only for this pipeline, define them in the script instead of `.claude/agents/`:

```bash
AGENTS='{
  "commit-classifier": {"description": "Classifies numbered commit subjects as breaking, feature, fix, or internal.",
                        "prompt": "Reply with only a JSON object mapping each commit number to its category.",
                        "tools": [], "model": "haiku"},
  "notes-writer": {"description": "Rewrites commit subjects as one-line, user-facing release notes.",
                   "prompt": "Reply with only lines of the form <number>: <note>.", "tools": [], "model": "haiku"}
}'
claude -p "$PROMPT" --agents "$AGENTS" --json-schema "$(cat notes.schema.json)" --output-format json < /dev/null > run.json
```

`"tools": []` is deliberate: the coordinator puts everything a worker needs **in the Agent prompt**, so workers have nothing to read and nothing to break.

## Keep worker output small

The coordinator's context fills with every worker reply. A worker that returns a 3,000-word essay per call costs you twice: tokens, and a coordinator that loses track. So:

- Specify the reply format exactly (JSON, or `<n>: <line>`) and say "only".
- Send each worker the **minimum input**: the writer gets only the user-facing commits, not all of them.
- Ask for **identifiers**, not copies: workers refer to commits by number and the coordinator joins on it.
- Put the final shape in `--json-schema`, so the deliverable is validated, not parsed out of prose.
- Render with code. `render.py` turns the structured output into Markdown, so formatting never depends on a model.

## Guard the inputs

Validate the range before spending anything: `git rev-parse --verify -q "$from^{commit}"` fails fast on a typo. Exit with a distinct code, and don't call Claude.

## Commands this node introduces

Inline `--agents` workers with `"tools": []`, a coordinator constrained by `--json-schema`, number-keyed joins between stages, and a deterministic renderer.
