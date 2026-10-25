---
type: lesson
title: "The official GitHub Action"
minutes: 12
---

`anthropics/claude-code-action@v1` runs Claude Code inside a GitHub Actions job. Most of the security work is in the workflow around it, not in the action itself.

## Two modes

- **Interactive**: no `prompt` input. Claude waits for `@claude` in an issue or PR comment, a review, or a new issue, and replies in a comment that it updates as it works.
- **Automation**: a `prompt` input (plain text, or a skill such as `/code-review:code-review`). It runs on any event, including `pull_request` and `schedule`, and results go to the run log unless the prompt and tools post a comment.

```yaml
name: Claude
on:
  issue_comment:
    types: [created]
jobs:
  claude:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    timeout-minutes: 20
    permissions:
      contents: write
      pull-requests: write
      issues: write
      id-token: write
      actions: read
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 1
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          claude_args: "--max-turns 10"
```

## Inputs you will use

| Input | Purpose |
|---|---|
| `anthropic_api_key` / `claude_code_oauth_token` | Claude API key (billed to the Console) or a subscription token from `claude setup-token`. Always `${{ secrets.* }}` |
| `anthropic_federation_rule_id` + `anthropic_organization_id` | Workload identity federation: the job's OIDC token is exchanged for API access, so there is no stored secret. Needs `id-token: write` |
| `prompt` | Switches to automation mode |
| `claude_args` | Any CLI flags: `--max-turns`, `--model`, `--allowedTools`, `--mcp-config` |
| `settings` | Settings JSON (or a path), for example `permissions.allow` rules |
| `plugin_marketplaces`, `plugins` | Install plugins before the run (`code-review@claude-code-plugins`) |
| `github_token` | Override the default Claude GitHub App token. Commits made with `GITHUB_TOKEN` don't trigger other workflows |
| `trigger_phrase`, `allowed_bots`, `allowed_non_write_users` | Who and what can start a run |
| `use_bedrock`, `use_vertex`, `use_foundry` | Route inference through your cloud account with OIDC |

## Who can trigger it

The action rejects actors without **write access** on issue and PR events (unless they are listed in `allowed_non_write_users`) and rejects **bots** (unless they are in `allowed_bots`). This protects you from strangers spending your budget and from bot loops.

## Hardening checklist

1. **Triggers**: prefer `pull_request` and `issue_comment`. `pull_request_target` runs with secrets and write tokens **on fork PRs**, so never combine it with checking out the PR's head.
2. **Permissions**: declare them per job, as small as the task allows. Never `write-all`.
3. **Secrets**: only through `${{ secrets.* }}` or OIDC federation. Never inline, never echoed.
4. **Untrusted text**: PR titles, bodies, branch names, and comments are attacker-controlled. Interpolating `${{ github.event.pull_request.title }}` into `run:` is **script injection**; putting it into `prompt` is **prompt injection**. Pass numbers and IDs, and let Claude read the text as data.
5. **Pin the action**: `@v1` (or a full commit sha), never `@main`.
6. **Bound it**: `timeout-minutes` on the job, `--max-turns` in `claude_args`, and a `concurrency` group so a burst of pushes doesn't start ten runs.
7. **No permission bypass**: grant tools with `--allowedTools` or `settings`. Never `--dangerously-skip-permissions` in CI.
8. **Fork PRs**: on public repos, GitHub withholds secrets from fork-triggered `pull_request` runs. Guard with `if: github.event.pull_request.head.repo.full_name == github.repository` so the job skips cleanly instead of failing.

## Upgrading from beta

Change `@beta` to `@v1`, delete `mode`, rename `direct_prompt` to `prompt`, and move `max_turns` and `model` into `claude_args`. `custom_instructions` becomes `--append-system-prompt`.

## Commands this node introduces

`anthropics/claude-code-action@v1`, interactive versus automation mode, `claude_args`, `allowed_bots`, `allowed_non_write_users`, OIDC federation inputs, and the hardening checklist.
