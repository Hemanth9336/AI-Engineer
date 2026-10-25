---
type: lesson
title: "Agent-driven defensive review"
minutes: 19
---

An agent is a fast first reviewer of your own code: it can read every handler, follow data from input to sink, and flag patterns a tired human skims past. Treat it as **defensive review of code you own**, with findings you can verify and fixes you test.

## Make the review checkable

A review in prose can't be tracked or verified. Ask for a schema instead:

```json
{"findings": [{"id": "F1", "file": "shop/db.py", "line": 12, "cwe": "CWE-89", "severity": "high",
               "title": "SQL injection in find_products", "fix": "Use a parameterized query"}]}
```

| Field | Why |
|---|---|
| `file` and `line` | You can jump to it, and a checker can confirm it |
| `cwe` | A shared vocabulary: CWE-89 SQL injection, CWE-22 path traversal, CWE-798 hard-coded credentials, CWE-78 OS command injection |
| `severity` | Triage order |
| `fix` | Turns the finding into a task |

Run it read-only (`--tools Read,Grep,Glob` and `--allowedTools Read,Grep,Glob`) with `--json-schema`. The reviewer can't change code, and its result is validated.

## The three classics in this lab

| Issue | Vulnerable | Fixed |
|---|---|---|
| SQL injection (CWE-89) | `f"SELECT ... WHERE name LIKE '%{name}%'"` | `cur.execute("... LIKE ?", (f"%{name}%",))`. The driver quotes, you don't |
| Path traversal (CWE-22) | `open(f"invoices/{invoice_id}.txt")` | Validate the id against a strict pattern, resolve the path, and check it stays inside the invoices directory |
| Hard-coded credential (CWE-798) | `DB_PASSWORD = "..."` in source | Read it from the environment and fail loudly when it's missing. **Rotate** the leaked value: it's in git history and every clone |

## Fix with proof

For each finding, write a test that **exploits** the bug first: the injection payload `' OR '1'='1`, the path `../config`, or the missing environment variable. Watch it fail, fix, watch it pass. That's how you know the fix addresses the finding and not just the line.

## Boundaries

Review and harden code you own or are authorized to test. Keep real secrets out of prompts and reports: cite the location, not the value. A clean agent review lowers risk, but it doesn't certify anything. Keep `/security-review`, dependency scanning, and human review in the pipeline.

## Commands this node introduces

A read-only review with `--json-schema` findings (`file`, `line`, `cwe`, `severity`, `fix`), CWE-89, CWE-22, and CWE-798, parameterized queries, path containment checks, environment-sourced secrets, and exploit-first regression tests.
