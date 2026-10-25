---
type: lesson
title: "Components and tool choices"
minutes: 23
---

Every component of an agentic system is either a **script** (deterministic code) or an **agent** (a model with tools). Picking wrong is the most common design mistake: agents doing arithmetic, or scripts trying to write prose.

## The decision rule

| Question | If yes |
|---|---|
| Is there exactly one right answer that code can compute (counts, sets, parsing, merging)? | **Script** |
| Must it be the same every run, or be audited? | **Script** |
| Does it need judgement over messy text (explain a failure, write for customers, choose a fix)? | **Agent** |
| Would a wrong answer be expensive and hard to notice? | Script, or an agent whose output a script verifies |

## The release manager split

| Component | Kind | Why |
|---|---|---|
| release check runner | script | Test counts and exit codes are facts |
| changelog generator | script | Grouping commit subjects is parsing |
| activity hook | script | Logging must never be skipped or summarised |
| triage worker | agent | Explaining *why* tests fail needs reading tracebacks |
| notes worker | agent | Customer language is a writing job |
| coordinator | script | Orchestration must be predictable. An agent coordinator adds cost and variance |
| guard | script | Security decisions must be deterministic |
| verdict endpoint | script | Serving a file |

**Two agents out of eight components** is typical of a well-designed system. The agents sit at the edges where text needs judgement, and scripts verify what they produce.

## A design doc that earns its keep

- **A components table** with name, kind, what it reads and what it writes. The reads/writes columns *are* the interfaces.
- **Tool choices:** why each agent is an agent, and what tools it gets (here, Read and Write only).
- **Data flow:** which file feeds which step.
- **Failure modes:** for each way it can break, what the system does. "The worker left no file: the coordinator exits 2 and writes no notes" is a design decision, not an afterthought.

## Commands this node introduces

The script-vs-agent decision rule, the components table, and the data-flow and failure-mode sections.
