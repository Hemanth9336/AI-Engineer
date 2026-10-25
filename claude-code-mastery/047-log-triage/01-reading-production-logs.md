---
type: lesson
title: "Reading production logs"
minutes: 19
---

During an incident the log is loud: retries, timeouts, and errors from every service at once. Triage means finding the one line that started it.

## Anatomy of a line

```text
2026-10-25T09:58:13.022Z payments ERROR req=c3 charge failed
└─ timestamp (UTC)       └─ service └─ level └─ request id
```

The **request id** is the thread to pull: follow `req=c3` from the gateway through orders to payments and you have the whole path of one failed request.

## The rules of triage

1. **Find the first error in the failing chain, not the loudest one.** The gateway's 502s are the symptom users see. The first error on the same request path, upstream and earlier, is the cause.
2. **Separate the red herrings.** An error that started before the incident, or on an unrelated path (an email worker's SMTP reset), is noise. Note it, then set it aside.
3. **Read tracebacks bottom-up.** The last line is the exception (`KeyError: 'currency'`). The frame just above it is where it was raised (`payments/client.py`, line 88). Then open that line in the source.
4. **Look for what changed.** Deploys, config pushes, and feature flags right before the first error (`deploy finished version=v2.3.0`) are the usual trigger.
5. **Quantify the impact.** How many requests failed, and which services did the failure propagate to?

## With the agent

Don't paste a 2 GB log into the prompt. Give Claude `Grep` and `Read`, and it can search for `ERROR`, follow request ids, and open the source file at the traceback line. Ask for a **structured answer with evidence**: start time, service, exception, `file:line`, trigger, consequences, failed requests, red herrings, and a fix plan. Every field can then be checked against the log and the code.

## The fix plan

A good plan has an immediate mitigation (roll back v2.3.0, or default the currency) and a durable fix (validate the request at the API boundary, add a contract test between orders and payments). Name both.

## Commands this node introduces

`grep -n ERROR`, following a request id across services, bottom-up traceback reading, and a structured triage report.
