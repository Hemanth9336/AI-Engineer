---
type: lesson
title: "A local release API with systemd-run"
minutes: 23
---

Other tools want to ask "can we release?" without running anything: a deploy script, a chat bot, a dashboard. Serve the verdict over HTTP.

## The endpoint

| Request | Answer |
|---|---|
| `GET /verdict` | `200` with the contents of `release/out/verdict.json` |
| `GET /verdict` with no verdict yet, or an unreadable file | `503` with an error. "Unknown" must not look like an answer |
| `GET /health` | `200 {"ok": true}` |
| Anything else | `404` |

- **Read the file on every request.** No caching, so a new `check.py` run is visible immediately (and the atomic write from step 083 means you never serve half a file).
- **Bind `127.0.0.1`.** It's an internal tool. Exposing it means an auth decision, and that's out of scope.
- Python's `http.server.ThreadingHTTPServer` is enough. There are no dependencies.

## Running it as a transient systemd unit

`systemd-run` starts a command as a **transient unit**: supervised, logged to the journal, stoppable by name, and with no unit file to write.

```bash
systemd-run --user --unit release-api --collect -p WorkingDirectory="$PWD" python3 release/serve.py 8787
systemctl --user status release-api --no-pager
journalctl --user -u release-api -n 50
systemctl --user stop release-api          # --collect cleans the unit up after it stops
```

| Option | Effect |
|---|---|
| `--user` | Runs in your user manager, with no root needed |
| `--unit release-api` | A stable name to stop and inspect |
| `--collect` | Garbage-collects the unit even if it failed |
| `-p WorkingDirectory=...` | Any unit property (`-p MemoryMax=200M`, `-p Restart=on-failure` with `--service-type`) |

## When there's no systemd

macOS, most containers and some CI runners have no user systemd. Wrap start, stop and status in one script that uses systemd when `systemd-run` exists *and* `systemctl --user` works, and otherwise falls back to a background process with a **pid file** (`release/out/api.pid`). Both paths wait for `/health` before reporting success.

## Commands this node introduces

`GET /verdict` and `/health`, the 503 for unknown, binding 127.0.0.1, `ThreadingHTTPServer`, `systemd-run --user --unit --collect -p`, `systemctl --user status/stop`, `journalctl --user -u`, and a pid-file fallback.
