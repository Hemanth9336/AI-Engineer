---
type: lesson
title: "Self hosted runners"
minutes: 10
---

Cloud sessions (`claude --cloud`, sessions started from claude.ai or mobile, and cloud scheduled tasks) run on Anthropic-hosted machines by default. A **self-hosted environment** runs those same sessions on runners inside your network. Choose it when sessions must reach internal services, use pre-installed tooling, or keep checkouts on your own disks. Most teams are better off with hosted environments, which need no fleet.

## The parts

| Part | What it is |
|---|---|
| **Environment** | A named destination, created in claude.ai admin settings, that groups runners. Sessions are routed to an environment, not to a specific runner |
| **Environment secret** | The one credential runners use to register. It's shown once, so store it in your secret manager |
| **Runner** | A long-lived process on your hosts. It polls for work, clones the repo, and spawns a Claude Code child process per session |
| **Session** | One task. Its conversation still streams to Anthropic. The checkout, build artefacts and secrets stay on your machine |

All connections are **outbound** HTTPS from your network. Anthropic never connects in. Corporate egress proxies work, but they must not buffer the streaming responses.

## Capacity

- A runner **locks to one owner** (the user who started its first session) and serves only that owner, up to `--capacity` concurrent sessions. That keeps one person's checked-out code from ever sharing a disk with another's.
- So the **minimum fleet size is the number of owners active at once**, not the number of sessions. Ten developers running one session each need ten runners, or an autoscaler.
- The **autoscaling orchestrator** starts runners as sessions queue. Kubernetes with a fresh disk per runner fits naturally.

## Drain and retirement

| Situation | Do |
|---|---|
| A normal shutdown (deploy, scale-down) | Send `SIGTERM`. The runner stops taking work and drains its sessions |
| The default `--drain-grace-sec 0` | The runner exits as soon as its sessions finish, so the orchestrator restarts it clean, ready for any owner |
| Hosts destroyed at a known time without a usable signal (spot reclamation, a lifetime cap) | Start the runner with `--retire-at <epoch>` a few minutes earlier. Sessions are released at turn boundaries and resume on a fresh runner |
| A crash or a lost host | The lease lapses after about 60 seconds. The session is requeued, but a turn in progress is lost |

Treat runners like CI runners. Use an immutable image with your toolchain, short-lived credentials for git (minted per session where possible), no long-lived cloud keys on disk, and logs and metrics for the runner process itself.

## Commands this node introduces

Self-hosted environment, environment secret, runner, `--capacity`, owner lock, `--drain-grace-sec`, `--retire-at`, `SIGTERM` drain, and the autoscaling orchestrator.
