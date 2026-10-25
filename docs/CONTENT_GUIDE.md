# Content Guide

Every item is one Markdown file in `<skill>/<NN-step>/`. The website and README generator read these files directly, so this format is a contract. The reference example is `ai-fundamentals/01-introduction-to-generative-ai/` (topic 01) - match its voice: short sentences, second person, plain English, no hype, "you'll meet that later" teasers.

## Front matter (required, never change it)

```yaml
---
type: lesson | task | quiz | scenario | challenge
title: "Exact title from the manifest"
minutes: 7
---
```

No H1 (`# ...`) in item files - the site renders the title. Use `##` sections. Titles, order and minutes come from `scripts/manifest.py` (via `scripts/ai_fundamentals_skill.py`); `python3 scripts/build_index.py` validates them and regenerates every README and `data/ai-engineer.json`.

## Practice machine conventions (AI Fundamentals skill)

Ubuntu 24.04 root machine with the tools from `setup/ai-fundamentals/install-tools.sh`: the LiteLLM gateway (`ailab`), a venv at `/root/ai-lab/.venv` (first on `PATH`) with `openai`, `anthropic`, `langchain` and `langchain-openai`, and Claude Code. See `setup/README.md`.

- **Models**: only the five aliases `lab-mini`, `lab-fast`, `lab-smart`, `lab-reasoning`, `lab-open`. Never a provider model ID in a task - profiles change. Default to `lab-fast`.
- **Endpoints and keys** come from the environment: `$LAB_AI_URL` and `$LAB_AI_KEY` for curl; `OpenAI()`, `Anthropic()` and `ChatOpenAI(base_url=os.environ["OPENAI_BASE_URL"], api_key=os.environ["OPENAI_API_KEY"])` in Python; Claude Code is pre-pointed at the gateway. Code never contains a key or `localhost:4000`.
- **Folders**: each topic works in `/root/ai-lab/NN-<short>` (for example `05-api`, `16-tools`); graded answer files go in `/root/answers/NN-*.txt`.
- **Set up** starts with `ailab status` (when the task calls a model), creates the folder, and writes fixtures with `cat > file <<'EOF'` heredocs.
- **Requests** are built with `jq -n --arg ...` (never hand-written JSON with pasted data) and sent with `curl -sS "$LAB_AI_URL/v1/chat/completions" -H "Authorization: Bearer $LAB_AI_KEY" -H "Content-Type: application/json" -d @file.json -o response.json`. Replies are extracted with `jq -r '.choices[0].message.content'`.
- **Solutions** write whole files with heredocs and must pass against any provider profile.
- **Checkers are read-only** and may not depend on exact wording of a reply. They check:
  - the request files the learner wrote (`jq -e` on model, messages, temperature, tools, response_format);
  - the saved responses and the extracted reply (`reply.txt` equals `.choices[0].message.content`);
  - shape rules the prompt demanded (line counts, prefixes, JSON keys and enums, exact one-line answers only where the task makes the answer deterministic);
  - the gateway log: `jq -se 'any(.[]; ...)' /var/log/ailab/requests.jsonl`. Fields: `ts, epoch, ok, api, model, client, stream, max_tokens, temperature, json_mode, system, roles, tools, tool_calls, finish_reason, prompt_tokens, completion_tokens, total_tokens`. Prompt text is never logged;
  - scripts by **running them** on a fresh fixture the learner has not seen, plus exit codes for bad input;
  - key hygiene: every task ends with `! grep -rqF "$LAB_AI_KEY" $D`.
- Tasks with Python or Claude Code use `python` (the venv) and `claude -p "..." --tools ""` when code must be printed rather than written by the agent.
- Topics 24-26 are `type: task` projects with a Scenario, a requirements list, Hints and a full Solution.

## Practice machine conventions (RAG skill)

Everything above applies, plus the tools from `setup/rag/install-tools.sh` (`scripts/rag_skill.py` holds titles and minutes).

- **Models**: `lab-embed` for every embedding (all-MiniLM-L6-v2, 384 dimensions, normalised, local and free); `lab-fast` at `temperature=0` for grounded answers. Lessons quote real `lab-embed` scores, so recompute them if a fixture changes.
- **Python only**: tasks use the `openai` SDK, `chromadb` (`OpenAIEmbeddingFunction(api_key_env_var="OPENAI_API_KEY", api_base=os.environ["OPENAI_BASE_URL"], model_name="lab-embed")`), and LangChain (`OpenAIEmbeddings(model="lab-embed", check_embedding_ctx_length=False)`, `ChatOpenAI(model="lab-fast", temperature=0)`). Chroma collections use `configuration={"hnsw": {"space": "cosine"}}` (`collection_configuration=` in `langchain-chroma`); names need at least 3 characters; similarity = 1 - distance.
- **Folders**: topic 01 works in `/root/rag-start`; other topics in `/root/rag-lab/NN-<short>`; graded answers in `/root/answers/NN-*`. Set up re-creates every fixture a task needs (documents, chunks, vectors) so tasks don't depend on earlier ones, except where a task continues the previous task in the same topic.
- **Fixtures**: the Northwind handbook, ops docs, support KB and inventory runbook. Questions must retrieve the right chunk with MiniLM; verify the ranking before using a new question.
- **Refusals**: each tool has one exact sentence (`I don't know based on the document.`, `...the documents.`, `...the handbook.`, `...the docs.`, `...the runbook.`). Code compares loosely and prints the exact sentence; refusals carry no sources.
- **Checkers** embed with `lab-embed` themselves, import the learner's module or run the script on unseen questions, compare rankings and scores (tolerance 0.001-0.01), count embedding and chat calls in the log (`api`, `inputs`), and check that re-indexing is idempotent. They never depend on reply wording beyond a distinctive fact (`35 days`, `7070`).
- Topics 14-16 are projects; topic 01 uses `claude -p`.

## Practice machine conventions (AI Forward Deployed Engineer skill)

Everything above applies, plus the tools from `setup/fde/install-tools.sh` (`scripts/fde_skill.py` holds titles and minutes). Topic 01 is the reference example for this skill.

- **Story**: tasks are set at fictional customers - Meridian Logistics (help articles `a1`-`a12`, orders like `MER-55120`), Kestrel Bank and Foods, Harbor Foods, Dockside Retail. Reuse their facts; don't invent conflicting ones.
- **Models**: the five aliases, `lab-embed`, and `lab-tiny` (`lab-mini` with a 2,048-token input window) for context-limit tasks. Judges use `lab-smart` at `temperature=0` in JSON mode; cheap paths use `lab-mini`.
- **Folders**: `/root/fde-lab/NN-<short>`. Set up writes every fixture with heredocs and, where a task continues the previous one, writes the earlier file only if it's missing (`[ -f x.py ] || cat > x.py ...`).
- **Local services**: mock customer APIs and a slow model endpoint are started by Set up with `nohup` on `127.0.0.1` (4555 slow `lab-smart`, 4560 orders API with a bearer token, 4570 capstone orders API), after a `/health` probe so re-running Set up is safe.
- **Refusals**: one exact sentence, `I don't know based on the provided sources.`, shared by every grounded task, judge rubric and golden set.
- **Checkers** import the learner's module and drive it with fakes (a scripted `ask`, a stub client, a flaky tool), run scripts on unseen fixtures (hidden ticket dumps, logs, golden sets), count chat and embedding calls in the gateway log, and recompute numbers themselves (hit rates, costs, p95). Evals and judges are graded on their verdicts on known cases, never on reply wording.
- **Document deliverables** (scoping documents, pilot criteria, runbooks) are checked for required `##` sections, bullet counts, numbers in metrics and names from the brief - not for prose quality.
- Topics 42-44 are single-task capstones with a Scenario; topic 22 registers an MCP server with `claude mcp add --scope user`.

## Practice machine conventions (Harness Engineering skill)

Everything above applies, plus the tools from `setup/harness/install-tools.sh` (`scripts/harness_skill.py` holds titles and minutes). Topic 01 is the reference example for this skill.

- **Story**: Stackline's project workspace (`services/billing.yaml` on port 8081, `services/search.yaml` on 9200), its helpdesk tickets, the ledger-api project (topics 34-37) and the support triage queue (topic 41). Reuse their facts.
- **Harness code** is plain Python on the `openai` SDK (`OpenAI()` reads the gateway from the environment), on `lab-fast`; cheap side calls (summaries, verifiers) use `lab-mini`. Topics 07-11 build one loop (`harness_loop` in the build scripts) that later topics extend; Set up writes the starting `agent.py` only if it's missing.
- **Folders**: `/root/harness-lab/NN-<short>`, with the agent's files in a `workspace/` subfolder.
- **labmock** (`/opt/harness/labmock.py`) is the test model. Checkers drive the learner's harness with scripted steps - tool calls, bad JSON, endless loops, usage numbers, outages, rules per conversation for subagents and verifiers - and assert on exit codes, the exact requests the harness sent, tool results, logs and transcripts. A solution's run against the real gateway is checked in the request log only (`tool_calls`, `model`), never by reply wording.
- **Attacks are tested, not described**: injection, path escapes, symlinks, shell operators and secret leaks are each run against the learner's code, with fake keys like `sk-fake-leakcheck-0000` only.
- **Claude Code topics (34-37)** run `claude -p ... --max-turns N --output-format stream-json --verbose` and grade the event stream (`init`, `tool_use`, `tool_result`, `result` with `permission_denials`). Checkers start `claude` with stdin closed. MCP servers use the project scope (`.mcp.json`) or `--mcp-config --strict-mcp-config`; hooks live in `.claude/settings.json`; skills in `.claude/skills/<name>/SKILL.md`. Template fences inside files written by a solution use `~~~`, never triple backticks.
- Topics 39-41 are single-task capstones with a Scenario.

## Practice machine conventions (Claude Code Fundamentals skill)

The tools come from `setup/claude-code/install-tools.sh`, and `scripts/claude_code_skill.py` holds the titles and minutes. Topic 01 is the reference example for this skill: the user supplied its lesson and task word for word.

- **Folders**: `/root/cc-lab/NN-<short>`. Set up writes small, self-contained projects with heredocs, such as the tasklog CLI, the billing-svc service, the shop package, shipping rates and notes-api. A folder becomes a git repo with `git init -q && git symbolic-ref HEAD refs/heads/main` when a task needs one. Python projects ship a `.gitignore` with `__pycache__/` so test runs don't dirty the tree.
- **The learner drives Claude Code, and checkers grade evidence.** That evidence comes in three forms:
  - Claude Code's session transcripts in `~/.claude/projects/<encoded realpath>/*.jsonl`. Match on `cwd` with `os.path.realpath`, because on macOS `/tmp` is `/private/tmp`.
  - Saved `claude -p ... --output-format stream-json --verbose` runs, using `init`, `tool_use`, `result` and `permission_denials`.
  - The files the work produced, run on hidden fixtures.

  Never grade the wording of a model reply.
- **Commands in transcripts**: a slash command shows up as `<command-name>/name</command-name>` in the user prompt. Use that to prove `/init` or a custom command ran. A subagent hand-off is a `tool_use` named `Agent` with a `subagent_type`.
- **Trust**: a folder's `allow` rules are ignored until the folder is trusted (`projects[<realpath>].hasTrustDialogAccepted` in `~/.claude.json`), but `deny` rules always apply. Instructions tell the learner to open `claude` once and accept the prompt. Solutions set the flag with `jq`.
- **Models**: tasks pick `haiku`, or `lab-mini` on the gateway via `ANTHROPIC_DEFAULT_HAIKU_MODEL`. Tasks that test the `model` setting run `env -u ANTHROPIC_MODEL`, because the environment variable outranks settings.
- **Safety**: fake secrets only (`pk_live_fake_5521`). Deny rules cover `.env` and `curl`. Hooks and automation scripts are unit-tested with stub `claude` scripts, so success, failure and `is_error` paths are all checked without a model.
- Topics 18-20 are single-task capstones with a Scenario.

## Practice machine conventions (Claude Code Mastery skill)

The tools come from `setup/claude-code-mastery/install-tools.sh`, and `scripts/claude_code_mastery_skill.py` holds the titles and minutes for all 88 topics. Topic 001 is the reference example for this skill: the user supplied its lesson and task word for word. Everything in the Claude Code Fundamentals section above also applies here.

- **Folders**: `/root/mastery/NNN-<short>`, with three-digit topic numbers. The capstone steps (081-088) each get their own `/root/mastery/NNN-release-manager`. Set up rebuilds the pricing app with its git history, plus the reference solution of every earlier capstone step, so one mistake never blocks the rest.
- **Headless evidence**: `--output-format json` envelopes (`subtype`, `is_error`, `num_turns`, `total_cost_usd`, `session_id`, `structured_output`) and `stream-json` events. An expanded skill or slash command is recorded as a user row with `isMeta: true` ("Base directory for this skill: ..."), so search those rows rather than `prompts()`.
- **Stub `claude`**: scripts that wrap `claude -p` (retries, fan-out, coordinators, release checks) are tested by putting a fake `claude` first on `PATH` that prints a chosen envelope or exits non-zero. Every wrapper must be shown failing as well as passing.
- **Agents as workers**: `claude -p ... --agent <name>` runs a session as a project agent. Its body is the system prompt and its `tools:` list is enforced. Parallel workers are started with `&` and checked by exit code, envelope and artifact.
- **Hooks**: hook scripts are unit-tested by piping event JSON into them (`tool_name`, `tool_input`, `session_id`). Guards must deny the dangerous variants and allow the innocent look-alikes, and observability hooks must exit 0 on bad input.
- **Surfaces that need a claude.ai plan** (Remote Control, cloud sessions, Chrome, Desktop, artifacts, `/design`) are taught with lessons, scenarios and quizzes only, written strictly from the official documentation. Never invent flags. Verify them against `claude --help` or the docs first.
- **Ports**: 14318 (the OpenTelemetry collector, topic 068) and 18787 (the verdict API, topic 087). Servers started by a checker are always stopped in a `finally` block.

## Lesson (250-600 words)

Open with one or two sentences on why it matters. Then `##` sections, each with a short explanation and an example: a ```bash block for commands, ```json for requests and responses, ```python for SDK code, ```text for prompts and output. Tables for comparisons. Optional mermaid diagram (quote labels containing parentheses or slashes; no semicolons). End with a one-line teaser of what comes next.

## Task (graded by a checker script)

```markdown
## Scenario            (optional, 1-3 sentences of on-the-job context)

## Set up
What state to start from / what to create first.

## What to build
Exact paths and exact expected contents - a table works well. Be precise enough that a script can check it.
End with: When everything is in place, press **Submit**.

<details><summary>Hints</summary>
- 2-4 nudges, no full answers
</details>

<details><summary>Solution</summary>
```bash
full working commands
```
</details>

## Check your work
One ```bash block that prints a ✅ or ❌ line per requirement (pattern: `test && echo "✅ x" || echo "❌ x"`).
It must be correct and read-only, and print at least one ❌ when nothing has been done.

## What you learned
- 2-3 bullets
```

## Quiz and Scenario (multiple choice - the site makes these interactive)

Quizzes: 3-5 questions. Scenarios: a realistic on-the-job situation paragraph first, then 2-4 questions. Exactly four options, one correct, each option on ONE line starting `- A. ` .. `- D. `. Vary the correct letter.

```markdown
### Q1. Question?

- A. option
- B. option
- C. option
- D. option

<details><summary>Answer</summary>

**Answer: C** - why C is right and why the tempting wrong answer is wrong.

</details>
```

## Accuracy and safety

- Real APIs, parameters and SDK calls only - check them against the pinned versions in `install-tools.sh`.
- Prices are examples ("a typical mid-tier model might cost..."), never quoted as current facts.
- Never show a real-looking secret. Placeholders look like `sk-lab-...` or `${GITHUB_PAT}`.
- Anything that lets a model act (tools, agents, MCP) comes with least-privilege and human-approval guidance.
