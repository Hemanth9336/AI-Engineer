---
type: lesson
title: "Read vs write vs irreversible"
minutes: 6
---

Not all tools are equal. Reading a config file and deleting a database share the same mechanism - the model proposes, the harness runs - but the consequences of a mistake are completely different. The first step in making tools safe is to **classify** them.

## Three classes

| Class | Examples | If the model gets it wrong |
|---|---|---|
| **Read** | `list_dir`, `read_file`, `search_logs`, `get_customer` | A wasted step. Nothing changes |
| **Write (reversible)** | `write_file` in a git repo, `create_draft`, `add_label` | Something changed, but you can undo it |
| **Irreversible** | `delete_file`, `drop_table`, `send_email`, `git push --force`, `charge_card`, `deploy_to_prod` | It happened. You can't take it back |

The class is a property of the **action in its environment**, not of the tool's name. `write_file` is reversible in a git working tree and irreversible on a production server's config directory with no backups. `send_email` is irreversible everywhere - you can't unsend.

## Why classification matters

Each class gets a different policy:

| Class | Typical policy |
|---|---|
| Read | Run automatically. Still subject to limits and sandboxing (topic 22) |
| Write | Run automatically inside a safe boundary (a branch, a scratch folder), or with lightweight review |
| Irreversible | **Never** without an explicit approval from a human (or a very narrow, pre-approved rule) |

## Unknown means irreversible

When you add a tool and forget to classify it, what happens? A safe harness treats **unclassified tools as the most dangerous class**. "Default deny" means a forgotten entry costs an extra approval prompt, not a deleted directory.

```python
RISK = {"list_dir": "read", "read_file": "read",
        "write_file": "write", "delete_file": "irreversible"}

risk = RISK.get(name, "irreversible")     # unknown tools are treated as dangerous
```

## Make the risk visible to the model too

Say it in the description: "Delete a file. This cannot be undone and needs the user's approval." The model then uses the tool more carefully - but the **harness** still enforces the rule. The description is advice; the gate is the guarantee.
