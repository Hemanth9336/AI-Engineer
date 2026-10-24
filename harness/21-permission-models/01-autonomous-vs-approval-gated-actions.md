---
type: lesson
title: "Autonomous vs approval-gated actions"
minutes: 7
---

Topic 15 put a gate in front of risky **tools**. A shell tool is harder: one tool, `run_shell(command)`, can do anything from `ls` to `rm -rf ~`. The decision has to be made per **command**, by a **permission policy** in the harness.

## Three answers, not two

| Decision | When | What the harness does |
|---|---|---|
| **allow** | Known read-only commands: `ls`, `cat`, `grep`, `git status` | Run it immediately |
| **ask** | Anything not known to be safe: `mkdir`, `python script.py`, `git push` | Show the exact command, wait for y/N |
| **deny** | Known dangerous, or impossible to judge: `rm`, `sudo`, `curl`, pipes and `;` | Refuse, with a reason the model can act on |

The default matters most. A **denylist** ("block rm and sudo, allow the rest") fails open: the model finds `find . -delete`, `python -c "import shutil..."`, or `/bin/rm`. An **allowlist** fails closed: anything you didn't think of is asked about, not run.

## Check the command, not the string

Commands are parsed, not pattern-matched:

```python
if any(op in command for op in (";", "|", "&", ">", "<", "`", "$(")):
    return "deny", "shell operators are not allowed - run one command at a time"
argv = shlex.split(command)          # 'grep -n "a b" f' -> ['grep', '-n', 'a b', 'f']
prog = argv[0]
```

- **Operators first.** `cat README.md; rm -rf services` starts with an allowed program. Refuse chaining, pipes, redirects and substitution outright - the agent can make several calls instead.
- **Then the program** - by name only (`/bin/rm` is refused).
- **Then the arguments** where they change the meaning: `find` is read-only until `-delete` or `-exec`; `git` is read-only for `status`/`log`/`diff`, not `push`.
- **Run without a shell.** `subprocess.run(argv, shell=False)` means no second interpretation of the string.

## Make every decision visible

- Log each decision with the command: `allow  ls services`, `deny  rm -rf services`, `refused  git push`.
- Return denials as tool results the model can learn from: `error: denied - rm is never allowed`.
- Show the **exact** command in the approval prompt - not the model's description of it.

This is how coding agents work: Claude Code, for example, has allow / ask / deny permission rules per tool and per command pattern (topic 36).
