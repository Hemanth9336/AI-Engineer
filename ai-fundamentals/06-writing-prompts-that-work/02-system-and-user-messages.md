---
type: lesson
title: "System and user messages"
minutes: 7
---

Over the API, a prompt is not one block of text. It is a list of **messages**, and each has a **role**. Two roles matter most.

## The system message

The **system** message sets the ground rules for the whole conversation: who the model is, how it should behave, what it must never do, and the format you always want.

```json
{"role": "system", "content": "You are a concise assistant for a DevOps team. Answer in plain English, under 100 words. If you are not sure, say so."}
```

It is written once, by the developer, and the end user usually never sees it.

## The user message

The **user** message is the actual request - the question, the task, the text to process:

```json
{"role": "user", "content": "Why would a pod be stuck in CrashLoopBackOff?"}
```

In a chat app, what you type is the user message. In your own tool, your code builds it, often by inserting data (a ticket, a log, a document) into a template.

## A third role you will meet

The **assistant** role holds the model's own earlier replies. You add those when you continue a conversation (topic 12) or show the model worked examples (topic 07).

## What goes where

| Put it in the system message | Put it in the user message |
|---|---|
| The model's role and audience | This specific question or task |
| Rules that apply to every request | The data to work on: ticket text, logs, a document |
| The output format your code expects | Details that change from request to request |
| Safety limits ("never reveal ...") | |

A simple test: if it would be the same for the next 1,000 requests, it belongs in the system message.

## The request

```json
{
  "model": "lab-fast",
  "messages": [
    {"role": "system", "content": "You are a concise assistant for a DevOps team."},
    {"role": "user", "content": "Why would a pod be stuck in CrashLoopBackOff?"}
  ]
}
```

Order matters: the system message comes first, then the conversation. With the Anthropic Messages API the system text is a separate top-level `system` field rather than a message - same idea, different place. Next: getting specific.
