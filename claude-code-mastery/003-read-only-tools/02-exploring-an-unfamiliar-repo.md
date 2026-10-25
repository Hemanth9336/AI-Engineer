---
type: lesson
title: "Exploring an unfamiliar repo"
minutes: 14
---

Dropped into a codebase you have never seen, an agent (and you) should map before reading. Opening files at random burns context; a few targeted searches answer most first questions.

## A mapping order that works

1. **Shape** - Glob the top level and the main source tree: `*`, `src/**/*.py`, `**/*.toml`. Count test files.
2. **Entry points** - Grep for `def main`, `if __name__ == "__main__"`, console-script entries in `pyproject.toml`.
3. **Configuration** - Glob `config/*`, `*.toml`, `*.env.example`; Read the one that matters.
4. **Environment** - Grep for `os.environ` and `getenv` to list every variable the code needs.
5. **The thing you were asked about** - Grep for its name, then Read just that file.

## Ask for facts, not impressions

"Tell me about this repo" gets a paragraph you cannot check. "Report the entry point file, the configured port, and the environment variable the database layer reads, as `key: value` lines" gets facts you can verify in seconds - and a format a script can parse.

```bash
claude -p "Map this repo. Reply with exactly these lines and nothing else:
entrypoint: <path of the file that defines main()>
port: <the port in the config>
..." --allowedTools "Read Grep Glob" > NOTES.md
```

## Check the agent's claims

Every fact in a notes file should be something you can confirm with one command:

```bash
grep -rn "def main" src/
grep -n port config/*.toml
ls tests/test_*.py | wc -l
```

If a claim fails that check, the notes are wrong - however confident they sound. The checker in this task does exactly that against the source.

## Commands this node introduces

`claude -p ... > NOTES.md` saves a structured answer; plain `grep` and `ls` confirm each fact.
