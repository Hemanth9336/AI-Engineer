---
type: task
title: "Write a script with claude"
minutes: 13
---

## Scenario

On-call keeps grepping logs by hand to count errors. Ask Claude Code to write a small script for it - then check its work before trusting it.

## Set up

```bash
ailab status
mkdir -p /root/ai-lab/17-claude
cd /root/ai-lab/17-claude
cat > sample.log <<'EOF'
2026-10-24T10:00:01Z INFO  starting worker
2026-10-24T10:00:02Z ERROR could not reach redis
2026-10-24T10:00:05Z INFO  retrying
2026-10-24T10:00:07Z ERROR could not reach redis
2026-10-24T10:00:09Z WARN  slow response from api
2026-10-24T10:00:12Z ERROR giving up after 3 retries
EOF
```

## What to build

1. In `/root/ai-lab/17-claude`, use `claude -p "<your prompt>" --tools ""` to generate a bash script and save its output to `count_errors.sh`. Your prompt must specify:
   - usage `count_errors.sh LOGFILE`;
   - it prints the number of lines containing `ERROR`;
   - if the argument is missing or the file doesn't exist, it prints a usage message to stderr and exits with code 1;
   - reply with only the script, no explanation, no Markdown fences.
2. If the output still has Markdown fence lines, delete them. Make the script executable.
3. **Check it**: `bash -n count_errors.sh`, then run it on `sample.log` and save its output to `/root/ai-lab/17-claude/result.txt`.

The checker runs your script on its own log file and with no arguments.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `claude -p "Write a bash script ... Reply with only the script." --tools "" > count_errors.sh` - the prompt goes before `--tools`.
- Fence lines start with three backticks: `sed -i.bak '/^[`][`][`]/d' count_errors.sh` removes them.
- `./count_errors.sh; echo $?` should print a usage message and 1.

</details>

<details><summary>Solution</summary>

```bash
cd /root/ai-lab/17-claude
claude -p "Write a bash script count_errors.sh. Usage: count_errors.sh LOGFILE. It prints only the number of lines in LOGFILE that contain ERROR. If the argument is missing or the file does not exist, print a usage message to stderr and exit 1. Reply with only the script, starting with #!/usr/bin/env bash - no explanation and no Markdown fences." --tools "" > count_errors.sh
sed -i.bak '/^[`][`][`]/d' count_errors.sh && rm -f count_errors.sh.bak
chmod +x count_errors.sh
cat count_errors.sh
bash -n count_errors.sh
./count_errors.sh sample.log > result.txt
cat result.txt
```

</details>

## Check your work

```bash
D=/root/ai-lab/17-claude; S=$D/count_errors.sh; T=$(mktemp -d)
head -1 $S 2>/dev/null | grep -q '^#!.*\(bash\|sh\)' && echo "✅ count_errors.sh starts with a shebang" || echo "❌ count_errors.sh should start with #!/usr/bin/env bash"
[ -x $S ] && echo "✅ count_errors.sh is executable" || echo "❌ chmod +x count_errors.sh"
[ -s $S ] && ! grep -q '^[`][`][`]' $S && echo "✅ no Markdown fences left in the script" || echo "❌ remove the Markdown fence lines from count_errors.sh"
bash -n $S 2>/dev/null && echo "✅ the script has valid bash syntax" || echo "❌ bash -n count_errors.sh reports a syntax error"
[ "$(tr -d '[:space:]' < $D/result.txt 2>/dev/null)" = 3 ] && echo "✅ result.txt says sample.log has 3 errors" || echo "❌ run ./count_errors.sh sample.log > result.txt - it should print 3"
printf 'ERROR a\nINFO b\nERROR c\nERROR d\nERROR e\nok\n' > $T/x.log
[ "$(bash $S $T/x.log 2>/dev/null | tr -d '[:space:]')" = 4 ] && echo "✅ it counts 4 errors in the checker's log" || echo "❌ on a log with 4 ERROR lines the script printed '$(bash $S $T/x.log 2>&1 | head -1)'"
bash $S >/dev/null 2>$T/err; rc=$?; [ $rc = 1 ] && [ -s $T/err ] && echo "✅ no argument: usage on stderr and exit 1" || echo "❌ with no argument it should print usage to stderr and exit 1 (exit was $rc)"
bash $S $T/missing.log >/dev/null 2>&1; rc=$?; [ $rc = 1 ] && echo "✅ missing file: exit 1" || echo "❌ with a missing file it should exit 1 (exit was $rc)"
jq -se 'any(.[]; .ok and (.client | startswith("claude-cli")) and (.tools | length) == 0)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway saw claude run with no tools" || echo "❌ run claude -p --tools \"\" so it prints the script"
rm -rf $T
```

## What you learned

- `claude -p "..." --tools ""` prints code instead of letting the agent write files itself.
- A precise prompt - usage, output, edge cases - doubles as a test plan.
- Always read, syntax-check, and test AI-written code before you rely on it.
