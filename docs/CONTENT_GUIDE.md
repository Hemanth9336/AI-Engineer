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
