---
type: lesson
title: "Custom keybindings in keybindings.json"
minutes: 10
---

Every shortcut is an **action** bound to a key in a **context**. You can rebind, add, or remove them in `~/.claude/keybindings.json` - run `/keybindings` to create and open it. Changes apply live, without a restart.

```json
{
  "$schema": "https://www.schemastore.org/claude-code-keybindings.json",
  "bindings": [
    {
      "context": "Chat",
      "bindings": {
        "ctrl+e": "chat:externalEditor",
        "meta+k": "command:compact",
        "ctrl+s": null
      }
    }
  ]
}
```

- `context` says where the binding applies: `Global`, `Chat` (the prompt), `Autocomplete`, `Confirmation` (permission dialogs), `Transcript`, `HistorySearch`, and others.
- Values are action names such as `chat:externalEditor`, `chat:cycleMode`, `chat:newline` - or `command:<name>`, which runs `/<name>`.
- `null` **unbinds** a default.

## Choosing keys

- Use `ctrl+` or `meta+` (Alt/Option). A bare letter in the Chat context is just typing.
- Avoid keys your terminal or tmux already owns (`ctrl+a` in tmux, `ctrl+z` for suspend).
- The `$schema` line gives you autocompletion and validation in editors that support JSON Schema.

## Commands this node introduces

`/keybindings` creates or opens `~/.claude/keybindings.json`; `command:<name>` binds a key to any slash command.
