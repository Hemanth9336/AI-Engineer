---
type: lesson
title: "Contain the agent: directories and limits"
minutes: 7
---

Permissions decide **which** actions run. A sandbox decides **what an action can reach** once it runs. Your topic 21 agent allows `cat` - so `cat ../../etc/passwd` and `read_file("../secret.txt")` are allowed too. The fix isn't a longer allowlist; it's a boundary.

## The boundary: one working directory

```text
/root/harness-lab/22-sandbox/
  agent.py, secret.txt         <- outside: the agent must never see these
  workspace/                   <- inside: everything the agent may read, list, write or run in
    README.md, services/, ...
```

Every path the agent supplies is resolved and checked:

```python
WORK = (Path(__file__).parent / "workspace").resolve()

def inside(path):
    p = (WORK / path).resolve()          # follows .. and symlinks
    if p != WORK and WORK not in p.parents:
        raise Escape(f"{path} is outside the workspace")
    return p
```

- **Resolve, then compare.** `services/../../secret.txt` looks like it starts inside; resolved, it doesn't.
- **Symlinks too.** A `workspace/etc-link -> /etc` committed to a repo turns `etc-link/passwd` into `/etc/passwd`. `resolve()` follows it, so the check catches it.
- **Absolute paths** - `WORK / "/etc/passwd"` is `/etc/passwd` in Python. The same check refuses it.

## Limits for processes

A command that's allowed can still hurt by running too long, printing too much, or seeing too much:

| Limit | Why | How |
|---|---|---|
| **cwd** = the workspace | Relative paths land inside | `subprocess.run(..., cwd=WORK)` |
| **Clean environment** | Your API key is in the harness's env - and `env` would print it | `env={"PATH": ..., "HOME": str(WORK)}` |
| **Timeout** | `sleep 99999`, an infinite loop, a hung network call | `timeout=10` |
| **Output cap** | A 2 GB log into the context | `[:4000]` |
| **Path arguments** | `cat /etc/hosts` | Refuse arguments that start with `/` or `~`, or contain `..` |

The argument check is a rough filter, not a guarantee: a program can open any path it likes internally (`python -c "open('/etc/passwd')"`). That's why real sandboxes are enforced by the operating system - the next lesson.
