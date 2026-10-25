---
type: lesson
title: "The plugin lifecycle on the command line"
minutes: 10
---

Every lifecycle step has a `claude plugin` subcommand, so you can script it, test it, and run it in CI. Add `--json` and the last line of stdout is one JSON object, which is much easier to check than prose.

| Step | Command | Notes |
|---|---|---|
| Scaffold | `claude plugin init my-kit --with skills hooks` | Writes `~/.claude/skills/my-kit/`, which loads as `my-kit@skills-dir` |
| Check | `claude plugin validate ./team-kit --strict --json` | Run in CI on every change |
| Try for one session | `claude --plugin-dir ./team-kit` | Loads as `team-kit@inline`; nothing is installed |
| Measure | `claude plugin eval ./team-kit --trust-plugin --json eval.json` | Graded runs in isolated sessions |
| Catalog | `claude plugin marketplace add <dir or owner/repo> --scope project` | Topic 051 covers writing the catalog |
| Install | `claude plugin install team-kit@team-local --scope project --config ticket_prefix=OPS --json` | `project` writes `.claude/settings.json`, so teammates get it too |
| Inspect | `claude plugin list --json` | `id`, `version`, `scope`, `enabled`, `installPath`, `hasUserConfig`, `errors` |
| Pause | `claude plugin disable team-kit@team-local --json` | Doing it twice fails with `failureCode: "already_in_goal_state"`, which a script can treat as success |
| Resume | `claude plugin enable team-kit@team-local --json` | |
| Ship a change | bump `version`, `claude plugin marketplace update team-local`, then `claude plugin update team-kit@team-local --json` | `updateOutcome` is `updated` or `up_to_date`. Running sessions pick it up after `/reload-plugins` |
| Remove | `claude plugin uninstall team-kit@team-local --scope project --json` | Deletes stored options, secrets, and the data dir from the last scope; `--keep-data` keeps the data |
| Release | `claude plugin tag ./team-kit --dry-run` | Creates the `team-kit--v1.1.0` git tag once `plugin.json` and the marketplace agree on the version |

## Scopes

`user` (default, just you, everywhere), `project` (the repo's `.claude/settings.json`, shared through git), and `local` (`.claude/settings.local.json`, just you in this repo). Enable and disable auto-detect the scope by checking local, then project, then user.

## Exit codes

Every subcommand exits `0` on success and `1` on failure. `validate` adds `2` for "the validator crashed". Don't forget that "already disabled" is a failure (exit 1) unless you read `alreadyInGoalState` from the JSON.

## Commands this node introduces

`claude plugin install / list / enable / disable / update / uninstall` with `--json` and `--scope`, `--config KEY=VALUE`, `claude plugin marketplace update`, `/reload-plugins`, and `claude plugin tag`.
