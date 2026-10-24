---
type: task
title: "Build a log explainer CLI"
minutes: 60
---

## Scenario

**Project.** At 3 a.m., nobody wants to read 2,000 log lines. Build `explain_log.py`: point it at a log file and it prints a two-line explanation - what happened and the likely cause - based on the **end** of the log, without sending the whole file.

This project combines the SDK (topic 19), output control (topic 10), lean requests (topic 14), and safe handling of input files.

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/25-logs
cd /root/ai-lab/25-logs
for i in $(seq 1 400); do echo "2026-10-24T03:$(printf '%02d' $((i % 60))):00Z INFO  api request ok path=/v1/orders id=$i duration_ms=$((20 + i % 30))"; done > app.log
cat >> app.log <<'EOF'
2026-10-24T03:59:01Z WARN  postgres: disk usage on /var/lib/postgresql at 96%
2026-10-24T03:59:30Z ERROR postgres: could not write to file "pg_wal/000000010000000A": No space left on device
2026-10-24T03:59:31Z ERROR api: insert into orders failed: database unavailable
2026-10-24T03:59:33Z ERROR api: insert into orders failed: database unavailable
EOF
wc -l app.log
```

## What to build

Write `/root/ai-lab/25-logs/explain_log.py`:

```bash
python explain_log.py app.log
```

**Output**: exactly two lines on stdout:

```text
Summary: <what happened, one sentence>
Likely cause: <the most likely cause, one sentence>
```

**Requirements**:

1. Send only the **last 50 lines** of the file to `lab-fast`, inside `<log>` tags - never the whole file.
2. Use the OpenAI SDK, `temperature: 0`, and a `max_tokens` cap.
3. Check the reply in code: if it doesn't contain a `Summary:` line and a `Likely cause:` line, print an error to stderr and exit 1. Otherwise print exactly those two lines.
4. If the argument is missing or the file doesn't exist, print an error to stderr and exit **2** - without calling the model.
5. No key or URL in the code.

Save its output for `app.log` to `/root/ai-lab/25-logs/explanation.txt`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `collections.deque(f, maxlen=50)` keeps only the last 50 lines while reading.
- Find the lines with `next((l for l in lines if l.lower().startswith("summary:")), None)`.
- Check `Path(arg).is_file()` before creating the client.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/25-logs
cat > explain_log.py <<'EOF'
import sys
from collections import deque
from pathlib import Path

from openai import OpenAI

MAX_LINES = 50
SYSTEM = """You explain server logs to an on-call engineer. Reply with exactly two lines and nothing else:
Summary: <what happened, one sentence>
Likely cause: <the most likely cause, one sentence>"""


def find(lines, prefix):
    return next((l for l in lines if l.lower().startswith(prefix.lower())), None)


def main():
    if len(sys.argv) != 2:
        print("usage: explain_log.py LOGFILE", file=sys.stderr)
        sys.exit(2)
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"explain_log: {path}: no such file", file=sys.stderr)
        sys.exit(2)
    with path.open(errors="replace") as f:
        tail = "".join(deque(f, maxlen=MAX_LINES))

    resp = OpenAI().chat.completions.create(
        model="lab-fast",
        temperature=0,
        max_tokens=200,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"<log>\n{tail}</log>"},
        ],
    )
    lines = [l.strip() for l in (resp.choices[0].message.content or "").splitlines() if l.strip()]
    summary, cause = find(lines, "Summary:"), find(lines, "Likely cause:")
    if not summary or not cause:
        print("explain_log: the model did not reply in the expected format", file=sys.stderr)
        sys.exit(1)
    print(summary)
    print(cause)


if __name__ == "__main__":
    main()
EOF
python explain_log.py app.log > explanation.txt
cat explanation.txt
```

</details>

## Check your work

```bash
D=/root/ai-lab/25-logs; P=$D/explain_log.py; E=$D/explanation.txt; LOG=/var/log/ailab/requests.jsonl
grep -q 'from openai import OpenAI' $P 2>/dev/null && grep -q '<log>' $P && echo "✅ explain_log.py uses the SDK and wraps the log in <log> tags" || echo "❌ use the OpenAI SDK and wrap the log lines in <log> tags"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $P 2>/dev/null && [ -s $P ] && echo "✅ $P reads the key from the environment" || echo "❌ $P must not contain a key - let the SDK read it from the environment"
[ "$(grep -c . $E 2>/dev/null)" = 2 ] && sed -n 1p $E | grep -q '^Summary: ' && sed -n 2p $E | grep -q '^Likely cause: ' && echo "✅ explanation.txt is a Summary line and a Likely cause line" || echo "❌ explanation.txt must be exactly two lines: 'Summary: ...' then 'Likely cause: ...'"
grep -qi 'disk\|space' $E 2>/dev/null && echo "✅ the explanation points at the full disk" || echo "❌ the explanation should mention the disk running out of space"
(cd $D && python $P $D/app.log > $D/.out 2>/dev/null); rc=$?; [ $rc = 0 ] && [ "$(grep -c . $D/.out)" = 2 ] && echo "✅ a fresh run prints two lines and exits 0" || echo "❌ python explain_log.py app.log should print two lines and exit 0 (exit was $rc)"
jq -se 'last | .ok and .model == "lab-fast" and .temperature == 0 and (.max_tokens | type == "number")' $LOG >/dev/null 2>&1 && echo "✅ it calls lab-fast at temperature 0 with a max_tokens cap" || echo "❌ call lab-fast with temperature 0 and max_tokens"
PT=$(jq -s 'last | .prompt_tokens' $LOG 2>/dev/null); [ -n "$PT" ] && [ "$PT" -lt 3000 ] && echo "✅ the request used $PT input tokens - only the end of the log was sent" || echo "❌ the request used ${PT:-?} input tokens - send only the last 50 lines"
N0=$(wc -l < $LOG); python $P $D/no-such.log >/dev/null 2>$D/.err; rc=$?; N1=$(wc -l < $LOG)
[ $rc = 2 ] && [ -s $D/.err ] && [ "$N0" = "$N1" ] && echo "✅ a missing file exits 2 without calling the model" || echo "❌ for a missing file print an error and exit 2 before calling the model (exit was $rc)"
python $P >/dev/null 2>/dev/null; [ $? = 2 ] && echo "✅ no argument exits 2" || echo "❌ with no argument exit 2"
rm -f $D/.out $D/.err
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Send the model the part of the data that matters - here the last 50 lines.
- Fix the output format in the prompt, then enforce it in code.
- Fail fast and cheaply on bad input, before spending tokens.
