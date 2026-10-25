---
type: lesson
title: "Plugin anatomy"
minutes: 14
---

A **plugin** packages skills, commands, subagents, hooks, and MCP servers into one installable, versioned unit. Standalone `.claude/` files are fine for one project; a plugin is how you share the same setup across many repos and teammates.

```text
team-tools/                       # the plugin root
├── .claude-plugin/
│   └── plugin.json               # the manifest - and ONLY the manifest
├── skills/
│   └── release-check/SKILL.md
├── commands/                     # older flat-file form of skills
├── agents/
│   └── release-reviewer.md
├── hooks/hooks.json              # {"hooks": { ...same shape as settings... }}
├── .mcp.json                     # MCP servers
├── README.md
└── LICENSE
```

## The manifest

```json
{
  "name": "team-tools",
  "description": "Release helpers for the platform team",
  "version": "1.0.0",
  "author": { "name": "Platform team" },
  "license": "MIT"
}
```

`name` is required, has no spaces, and becomes the **namespace** of everything inside: the skill above runs as `/team-tools:release-check`. That is why two plugins can each ship a `review` skill without colliding.

## The two classic layout mistakes

- Putting `skills/` or `agents/` **inside** `.claude-plugin/` - components there do not load. Only `plugin.json` goes in that folder.
- Pointing `--plugin-dir` at the wrong level. It takes the plugin root - the folder that *contains* `.claude-plugin/`.

## Validate and try it

```bash
claude plugin validate ./team-tools          # checks manifest + every skill/agent/command frontmatter
claude --plugin-dir ./team-tools             # load for one session, no install
claude -p "/team-tools:release-check 2.4.0" --plugin-dir ./team-tools
```

`validate` exits 0 on `✔ Validation passed`; `--strict` also fails on warnings. It also lists what the public plugin directory would require (a README, a license, an icon), without failing the run.

## Commands this node introduces

`claude plugin validate <path>`, `claude --plugin-dir <path>`, and `claude plugin init` (scaffolds a skills-directory plugin).
