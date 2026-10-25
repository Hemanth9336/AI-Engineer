# 🛠️ Harness Engineering

Build the machinery around AI models - from zero. Learn how LLMs and tool calling work, build agent loops by hand, design tools and context, add permissions and injection defenses, orchestrate subagents, prove behavior with evals, and dissect a production harness.

**41 topics · 65 hands-on tasks · 49 quizzes · ~1505 min**

[▶ Open the interactive Harness Engineering path](https://hemanth9336.github.io/AI-Engineer/#/harness) · [Set up your practice machine](../setup/README.md)

## Roadmap

### Phase 1 · Foundations

_What a harness is, how LLMs behave, just enough Python, API calls, tokens, and tool calling._

| Step | Topic | Time | 🛠️ Tasks | ❓ Quizzes |
|---|---|---|---|---|
| 01 | [What a harness is](01-what-a-harness-is/) | ~30m | 0 | 2 |
| 02 | [How LLMs work for harness builders](02-how-llms-work-for-harness-builders/) | ~30m | 2 | 1 |
| 03 | [Just enough Python](03-just-enough-python/) | ~40m | 3 | 1 |
| 04 | [Calling LLMs over an API](04-calling-llms-over-an-api/) | ~40m | 3 | 1 |
| 05 | [Tokens, context, and cost](05-tokens-context-and-cost/) | ~40m | 3 | 1 |
| 06 | [Tool calling](06-tool-calling/) | ~40m | 2 | 1 |

### Phase 2 · The Agent Loop

_Build the loop by hand: stop conditions, errors, history, and asking the human._

| Step | Topic | Time | 🛠️ Tasks | ❓ Quizzes |
|---|---|---|---|---|
| 07 | [Your first agent loop](07-your-first-agent-loop/) | ~40m | 2 | 1 |
| 08 | [Stop conditions](08-stop-conditions/) | ~35m | 2 | 2 |
| 09 | [Error handling in the loop](09-error-handling-in-the-loop/) | ~35m | 2 | 1 |
| 10 | [Loop state and history](10-loop-state-and-history/) | ~35m | 2 | 1 |
| 11 | [Making the agent ask for help](11-making-the-agent-ask-for-help/) | ~25m | 1 | 2 |

### Phase 3 · Tool Design

_Tools are prompts: descriptions, result shapes, tool sets, and dangerous actions._

| Step | Topic | Time | 🛠️ Tasks | ❓ Quizzes |
|---|---|---|---|---|
| 12 | [Tools are prompts](12-tools-are-prompts/) | ~35m | 2 | 1 |
| 13 | [Designing tool results](13-designing-tool-results/) | ~35m | 2 | 1 |
| 14 | [Tool sets and selection](14-tool-sets-and-selection/) | ~30m | 1 | 2 |
| 15 | [Dangerous tools](15-dangerous-tools/) | ~30m | 1 | 2 |

### Phase 4 · Context Engineering

_System prompts, budgets, compaction, file memory, and retrieval into context._

| Step | Topic | Time | 🛠️ Tasks | ❓ Quizzes |
|---|---|---|---|---|
| 16 | [The system prompt](16-the-system-prompt/) | ~35m | 2 | 1 |
| 17 | [Context budgeting](17-context-budgeting/) | ~35m | 2 | 1 |
| 18 | [Compaction and summarization](18-compaction-and-summarization/) | ~35m | 2 | 1 |
| 19 | [File-based memory](19-file-based-memory/) | ~35m | 2 | 1 |
| 20 | [Retrieval into context](20-retrieval-into-context/) | ~30m | 1 | 1 |

### Phase 5 · Permissions and Safety

_Permission models, sandboxes, prompt injection through tools, and secrets hygiene._

| Step | Topic | Time | 🛠️ Tasks | ❓ Quizzes |
|---|---|---|---|---|
| 21 | [Permission models](21-permission-models/) | ~35m | 1 | 2 |
| 22 | [Sandboxing](22-sandboxing/) | ~30m | 1 | 1 |
| 23 | [Prompt injection through tools](23-prompt-injection-through-tools/) | ~35m | 2 | 1 |
| 24 | [Secrets hygiene](24-secrets-hygiene/) | ~30m | 2 | 2 |

### Phase 6 · Orchestration

_Subagents, parallel agents, verifiers, and the ways multi-agent systems fail._

| Step | Topic | Time | 🛠️ Tasks | ❓ Quizzes |
|---|---|---|---|---|
| 25 | [Subagents](25-subagents/) | ~30m | 1 | 1 |
| 26 | [Parallel agents](26-parallel-agents/) | ~30m | 1 | 1 |
| 27 | [Verification patterns](27-verification-patterns/) | ~35m | 2 | 1 |
| 28 | [Orchestration failure modes](28-orchestration-failure-modes/) | ~30m | 1 | 2 |

### Phase 7 · Evals and Observability

_Grading trajectories, eval suites, transcripts, cost caps, and regression gates._

| Step | Topic | Time | 🛠️ Tasks | ❓ Quizzes |
|---|---|---|---|---|
| 29 | [Evals for agents](29-evals-for-agents/) | ~25m | 0 | 2 |
| 30 | [Building an agent eval suite](30-building-an-agent-eval-suite/) | ~40m | 2 | 1 |
| 31 | [Transcripts and replay](31-transcripts-and-replay/) | ~35m | 2 | 1 |
| 32 | [Cost and latency of agents](32-cost-and-latency-of-agents/) | ~35m | 2 | 1 |
| 33 | [Regression testing a harness](33-regression-testing-a-harness/) | ~30m | 2 | 1 |

### Phase 8 · Production Harnesses

_Dissect and extend Claude Code: MCP, hooks, instruction files, skills, and choosing your layer._

| Step | Topic | Time | 🛠️ Tasks | ❓ Quizzes |
|---|---|---|---|---|
| 34 | [Claude Code as a harness](34-claude-code-as-a-harness/) | ~35m | 1 | 1 |
| 35 | [Extending a harness with MCP](35-extending-a-harness-with-mcp/) | ~35m | 2 | 1 |
| 36 | [Hooks and instruction files](36-hooks-and-instruction-files/) | ~35m | 2 | 1 |
| 37 | [Packaging behavior as skills](37-packaging-behavior-as-skills/) | ~25m | 1 | 1 |
| 38 | [Choosing your layer](38-choosing-your-layer/) | ~25m | 0 | 3 |

### Phase 9 · Capstone Projects

_Three end-to-end builds: a coding agent, a hardened harness, and a production triage harness._

| Step | Topic | Time | 🛠️ Tasks | ❓ Quizzes |
|---|---|---|---|---|
| 39 | [Project: Build a coding agent](39-project-build-a-coding-agent/) | ~75m | 1 | 0 |
| 40 | [Project: Harden the harness](40-project-harden-the-harness/) | ~75m | 1 | 0 |
| 41 | [Project: Production harness](41-project-production-harness/) | ~90m | 1 | 0 |

[⬅️ Back to AI Engineer](../README.md)
