---
type: lesson
title: "Packaging, validating, and evaluating a skill"
minutes: 12
---

A skill in `.claude/skills/` serves one repository. To share it, package it, check it statically, and measure it.

## Three ways to package

| Form | Where | Loads as | Use when |
|---|---|---|---|
| Project skill | `.claude/skills/<name>/SKILL.md` | `<name>` | Only this repo needs it; it travels with the code |
| Skills-directory plugin | `~/.claude/skills/<name>/` with `.claude-plugin/plugin.json`, scaffolded by `claude plugin init <name>` | `<name>@skills-dir` | You want plugin features (version, hooks, evals) without a marketplace |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | `<plugin>:<name>` | Several repos or a team need it; install it from a marketplace (topics 050 and 051) |

A plugin with a `SKILL.md` at its root and no `skills/` folder loads as a single skill. Inside a plugin, refer to bundled files with `${CLAUDE_SKILL_DIR}` (the skill's own folder) or `${CLAUDE_PLUGIN_ROOT}`.

## Validate before anyone loads it

```bash
claude plugin validate .            # a project: checks .claude/skills, agents, commands
claude plugin validate ./my-plugin  # a plugin: manifest, paths, every SKILL.md
claude plugin validate ./my-plugin --strict --json   # warnings fail too; machine-readable report
```

Exit `0` means it loads (possibly with warnings), `1` means errors (or warnings under `--strict`), and `2` means the validator itself failed. Validation catches unparsable frontmatter, bad paths, and unknown manifest keys. It cannot tell you whether the skill **fires**.

## Measure triggering with `claude plugin eval`

Plugin evals run realistic prompts in isolated `claude -p` sessions, with only the plugin loaded, and grade each run:

```text
my-plugin/evals/
├── fires-on-release-note/
│   ├── prompt.md            # frontmatter: max_turns, allowed_tools: [Read, Skill]; body: the user's words
│   └── graders/skill-fired.md
└── ignores-git-question/
    ├── prompt.md
    └── graders/no-skill.md
```

```markdown
---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?changelog-entry"'
---
```

A "must not fire" grader sets `min: 0`, `max: 0`, and `arm: both`. By default each case runs 3 times with the plugin and 3 times without, and the report shows `WITH`, `W/OUT`, and `Δ`. A Skill grader can't pass without the plugin, so it is reported but not scored across the two arms. Useful flags:

| Flag | Effect |
|---|---|
| `--runs <n>` | Runs per case and arm (default 3). One run is noise |
| `--ablation none` | Skip the no-plugin arm while iterating |
| `--threshold <0..1>` | Exit 1 if any case scores below it (default 1.0) |
| `--trust-plugin` | Required in CI or under `--json`, where the trust prompt can't be shown |
| `--json out.json` | The result document: `aggregates.casesPassed`, `cases[].aggregates.score`, ... |
| `--max-cost-usd` | Stop at a spend ceiling (exit 2, partial results) |

`claude plugin eval init` interviews you and writes cases. `--bare <case>` writes a blank template. Add `evals/results/` to `.gitignore`.

## Commands this node introduces

`claude plugin init`, `claude plugin validate [--strict] [--json]`, `claude plugin eval` with `tool_used` graders, and `claude plugin eval init --bare`.
