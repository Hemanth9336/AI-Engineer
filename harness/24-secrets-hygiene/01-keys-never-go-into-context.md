---
type: lesson
title: "Keys never go into context"
minutes: 6
---

An API key is a password that spends money and reads data. Harnesses handle keys constantly - they call models, tools and internal APIs - and they also write **a lot** of text: prompts, logs, traces, transcripts, error reports. Every one of those is a place a key can leak.

## Where keys leak in a harness

| Leak | How it happens | Who can then read it |
|---|---|---|
| **In the prompt** | "Use this token for the tool: sk-..." in the system prompt | The model provider, every trace and transcript, and an injection that asks "repeat your instructions" |
| **In a tool result** | `read_file(".env")`, `printenv`, a config dump | Same - it's now part of the context and the logs |
| **In debug logs** | Logging the full request, **including headers** | Anyone with log access, log shipping vendors, backups |
| **In crash reports** | Dumping `os.environ` or `repr(client)` on error | Whoever reads error trackers |
| **In code and git** | `API_KEY = "sk-..."` committed | Everyone who ever clones the repo, forever |

## The rules

1. **Keys live in the environment** (or a secret manager), read by the SDK: `OpenAI()` reads `OPENAI_API_KEY` itself. Never in source, never in prompt files.
2. **The model never needs your key.** Tools authenticate in **code**, outside the model. If a tool needs a token, the tool function reads it from the environment - the model only sees the tool's name and arguments.
3. **Tools don't return secrets.** Deny `.env` files and `printenv`; strip the environment of subprocesses (topic 22).
4. **Logs are redacted on the way out.** One `redact()` function that every log line passes through, replacing known secret values and key-shaped strings.
5. **Test for it.** Run with a **fake** key, then `grep -r` for it. If the fake key appears anywhere, the real one would too.

## Never test a leak with a real key

The next task runs a deliberately leaky harness. Use a fake key like `sk-fake-leakcheck-0000` against labmock, so the only thing that leaks is a string that unlocks nothing.
