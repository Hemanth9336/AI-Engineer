---
type: lesson
title: "What sandboxes cannot save you from"
minutes: 7
---

The Python checks you just wrote stop the agent's **own tools** from leaving the workspace. They don't stop a program the agent runs: `python -c "print(open('/root/.ssh/id_rsa').read())"` passes every argument check. Real containment is enforced **below** your code, by the operating system.

## Real sandboxes

| Layer | What it gives you | Examples |
|---|---|---|
| **OS sandbox for one process** | Filesystem and network rules the process can't bypass | Linux bubblewrap / Landlock / seccomp, macOS Seatbelt (`sandbox-exec`) - what Claude Code's sandbox mode uses |
| **Container** | Its own filesystem, user, process list; no host files unless mounted | `docker run --network none --read-only -v $PWD/workspace:/work` |
| **Micro-VM** | A separate kernel - the strongest isolation for untrusted code | Firecracker, gVisor; most hosted "code interpreter" products |
| **Separate machine / account** | No shared credentials at all | A throwaway cloud VM per task |

The usual combination: the agent runs in a container with **only the workspace mounted**, **no network** (or an allowlisted proxy), a non-root user, CPU / memory / time limits, and **no credentials** inside.

## What no sandbox fixes

A sandbox limits *where* the damage lands. It can't judge *what* the agent does with the access it legitimately has:

| Threat | Why the sandbox doesn't help | What does |
|---|---|---|
| **Misusing allowed tools** | Emailing customer data with the `send_email` tool you gave it | Least privilege, scoped tools, approval for outbound actions |
| **Prompt injection** | A poisoned file tells the agent to do bad things *inside* the box | Treat tool results as untrusted (topic 23) |
| **Damage inside the workspace** | `rm -rf` on the repo it's allowed to edit | Version control, backups, gates on deletes |
| **Secrets you put inside** | A `.env` in the workspace is readable by design | Keep secrets out (topic 24) |
| **Network egress** | If it can reach the internet, it can upload what it reads | `--network none`, or an egress allowlist |
| **Your own harness's credentials** | The loop that calls the model holds the API key | Run tools in a separate process or container from the loop |
| **Approved bad actions** | The user pressed `y` | Clear approval prompts, small blast radius (topic 21) |

## Defense in depth

No single layer is enough. Stack them so each covers the others' gaps:

```text
permission policy (allow/ask/deny)  ->  path & argument checks  ->  OS sandbox / container
   ->  least-privilege credentials  ->  logging and review
```

When something goes wrong, you want it to be stopped by the **first** layer and contained by the **last** one.
