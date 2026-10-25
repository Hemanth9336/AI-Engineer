---
type: scenario
title: "Scenario: guardrails that must hold"
minutes: 7
---

Security asks for three guarantees on the billing repo, whichever agent a developer uses: **the agent never pushes**, **the agent never reads `secrets/`**, and **every agent edit is logged**. You already have the Claude Code side in `.claude/settings.json`. Now you are writing the Codex side.

### Q1. Which Codex setup best matches `"deny": ["Bash(git push *)"]`?

- A. A forbidden prefix_rule for git push, with workspace-write keeping network off
- B. A sentence in AGENTS.md saying never push
- C. approval_policy = "never"
- D. A subagent that has no shell

<details><summary>Answer</summary>

**Answer: A** - The rule rejects the command and the sandbox blocks the network; a sentence in AGENTS.md is only a request.

</details>

### Q2. A developer runs `codex exec --sandbox danger-full-access` in CI to 'make it work'. What did they give up?

- A. Nothing, rules still sandbox commands
- B. AGENTS.md loading
- C. Only web search
- D. The OS sandbox: commands run with full disk and network access

<details><summary>Answer</summary>

**Answer: D** - danger-full-access removes the sandbox. Use it only on an isolated runner.

</details>

### Q3. You add a PostToolUse logging hook in `.codex/hooks.json`. The first run prints a warning and the hook does not run. Why?

- A. Codex has no PostToolUse event
- B. The matcher must be Bash
- C. Hooks only run in codex exec
- D. Codex requires reviewing and trusting each hook (by hash) in /hooks first

<details><summary>Answer</summary>

**Answer: D** - Non-managed hooks need trust. Editing the script changes the hash, so it needs trust again.

</details>

### Q4. You define a Codex custom agent `auditor` with `sandbox_mode = "danger-full-access"` in its TOML. What sandbox does it run in?

- A. danger-full-access
- B. read-only, always
- C. The parent session's sandbox - custom agents can't override it
- D. None

<details><summary>Answer</summary>

**Answer: C** - Custom agents inherit the parent's sandbox, approvals, and MCP servers.

</details>
