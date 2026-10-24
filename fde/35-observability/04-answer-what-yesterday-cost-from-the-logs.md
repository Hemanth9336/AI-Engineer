---
type: task
title: "Answer what yesterday cost from the logs"
minutes: 7
---

## Set up

`pilot-calls.jsonl` is three days of logs from Meridian's pilot, in the format from the previous task. `prices.json` has dollars per million tokens.

```bash
mkdir -p /root/fde-lab/35-observability
cd /root/fde-lab/35-observability
cat > pilot-calls.jsonl <<'EOF'
{"ts": "2026-03-12T07:04:52+00:00", "request_id": "70000", "model": "lab-mini", "ok": true, "error": null, "prompt_tokens": 2494, "completion_tokens": 68, "latency_ms": 1797}
{"ts": "2026-03-12T08:07:32+00:00", "request_id": "70009", "model": "lab-fast", "ok": true, "error": null, "prompt_tokens": 2012, "completion_tokens": 104, "latency_ms": 3401}
{"ts": "2026-03-12T10:34:07+00:00", "request_id": "70004", "model": "lab-mini", "ok": true, "error": null, "prompt_tokens": 2638, "completion_tokens": 177, "latency_ms": 2594}
{"ts": "2026-03-12T12:02:05+00:00", "request_id": "70001", "model": "lab-smart", "ok": false, "error": "RateLimitError: 429", "prompt_tokens": 0, "completion_tokens": 0, "latency_ms": 2003}
{"ts": "2026-03-12T12:23:06+00:00", "request_id": "70005", "model": "lab-mini", "ok": false, "error": "APITimeoutError: Request timed out.", "prompt_tokens": 0, "completion_tokens": 0, "latency_ms": 150}
{"ts": "2026-03-12T15:33:31+00:00", "request_id": "70008", "model": "lab-mini", "ok": false, "error": "RateLimitError: 429", "prompt_tokens": 0, "completion_tokens": 0, "latency_ms": 150}
{"ts": "2026-03-12T17:19:15+00:00", "request_id": "70007", "model": "lab-smart", "ok": true, "error": null, "prompt_tokens": 1036, "completion_tokens": 377, "latency_ms": 3494}
{"ts": "2026-03-12T17:38:31+00:00", "request_id": "70011", "model": "lab-fast", "ok": true, "error": null, "prompt_tokens": 2675, "completion_tokens": 253, "latency_ms": 581}
{"ts": "2026-03-12T18:03:14+00:00", "request_id": "70003", "model": "lab-smart", "ok": true, "error": null, "prompt_tokens": 490, "completion_tokens": 305, "latency_ms": 3816}
{"ts": "2026-03-12T19:03:52+00:00", "request_id": "70002", "model": "lab-mini", "ok": true, "error": null, "prompt_tokens": 2616, "completion_tokens": 83, "latency_ms": 1214}
{"ts": "2026-03-12T20:18:45+00:00", "request_id": "70013", "model": "lab-fast", "ok": true, "error": null, "prompt_tokens": 1880, "completion_tokens": 362, "latency_ms": 1721}
{"ts": "2026-03-12T21:26:02+00:00", "request_id": "70010", "model": "lab-fast", "ok": true, "error": null, "prompt_tokens": 617, "completion_tokens": 305, "latency_ms": 2647}
{"ts": "2026-03-12T21:43:34+00:00", "request_id": "70006", "model": "lab-mini", "ok": true, "error": null, "prompt_tokens": 2051, "completion_tokens": 180, "latency_ms": 2207}
{"ts": "2026-03-12T21:44:42+00:00", "request_id": "70012", "model": "lab-mini", "ok": true, "error": null, "prompt_tokens": 566, "completion_tokens": 51, "latency_ms": 3294}
{"ts": "2026-03-13T06:31:53+00:00", "request_id": "70018", "model": "lab-mini", "ok": true, "error": null, "prompt_tokens": 2713, "completion_tokens": 113, "latency_ms": 1376}
{"ts": "2026-03-13T07:29:57+00:00", "request_id": "70020", "model": "lab-smart", "ok": true, "error": null, "prompt_tokens": 2590, "completion_tokens": 220, "latency_ms": 1930}
{"ts": "2026-03-13T09:21:38+00:00", "request_id": "70022", "model": "lab-mini", "ok": true, "error": null, "prompt_tokens": 515, "completion_tokens": 72, "latency_ms": 300}
{"ts": "2026-03-13T09:23:39+00:00", "request_id": "70023", "model": "lab-smart", "ok": true, "error": null, "prompt_tokens": 404, "completion_tokens": 56, "latency_ms": 3881}
{"ts": "2026-03-13T09:31:03+00:00", "request_id": "70014", "model": "lab-fast", "ok": true, "error": null, "prompt_tokens": 1193, "completion_tokens": 167, "latency_ms": 829}
{"ts": "2026-03-13T10:40:16+00:00", "request_id": "70024", "model": "lab-mini", "ok": true, "error": null, "prompt_tokens": 1722, "completion_tokens": 328, "latency_ms": 1791}
{"ts": "2026-03-13T18:14:09+00:00", "request_id": "70017", "model": "lab-fast", "ok": true, "error": null, "prompt_tokens": 639, "completion_tokens": 110, "latency_ms": 919}
{"ts": "2026-03-13T19:34:23+00:00", "request_id": "70019", "model": "lab-fast", "ok": false, "error": "RateLimitError: 429", "prompt_tokens": 0, "completion_tokens": 0, "latency_ms": 2001}
{"ts": "2026-03-13T19:55:35+00:00", "request_id": "70016", "model": "lab-fast", "ok": true, "error": null, "prompt_tokens": 1440, "completion_tokens": 381, "latency_ms": 2001}
{"ts": "2026-03-13T21:05:10+00:00", "request_id": "70015", "model": "lab-mini", "ok": true, "error": null, "prompt_tokens": 2139, "completion_tokens": 225, "latency_ms": 2550}
{"ts": "2026-03-13T21:29:30+00:00", "request_id": "70025", "model": "lab-fast", "ok": true, "error": null, "prompt_tokens": 2281, "completion_tokens": 179, "latency_ms": 651}
{"ts": "2026-03-13T21:40:25+00:00", "request_id": "70021", "model": "lab-fast", "ok": true, "error": null, "prompt_tokens": 554, "completion_tokens": 117, "latency_ms": 575}
{"ts": "2026-03-14T08:44:54+00:00", "request_id": "70028", "model": "lab-smart", "ok": true, "error": null, "prompt_tokens": 1369, "completion_tokens": 285, "latency_ms": 1802}
{"ts": "2026-03-14T08:46:10+00:00", "request_id": "70037", "model": "lab-fast", "ok": true, "error": null, "prompt_tokens": 996, "completion_tokens": 85, "latency_ms": 412}
{"ts": "2026-03-14T08:53:42+00:00", "request_id": "70035", "model": "lab-fast", "ok": true, "error": null, "prompt_tokens": 791, "completion_tokens": 218, "latency_ms": 3504}
{"ts": "2026-03-14T11:27:50+00:00", "request_id": "70036", "model": "lab-mini", "ok": true, "error": null, "prompt_tokens": 2904, "completion_tokens": 190, "latency_ms": 655}
{"ts": "2026-03-14T12:44:38+00:00", "request_id": "70032", "model": "lab-fast", "ok": true, "error": null, "prompt_tokens": 1710, "completion_tokens": 248, "latency_ms": 3611}
{"ts": "2026-03-14T12:51:15+00:00", "request_id": "70030", "model": "lab-mini", "ok": true, "error": null, "prompt_tokens": 1941, "completion_tokens": 398, "latency_ms": 3590}
{"ts": "2026-03-14T13:34:34+00:00", "request_id": "70029", "model": "lab-mini", "ok": true, "error": null, "prompt_tokens": 2359, "completion_tokens": 188, "latency_ms": 2906}
{"ts": "2026-03-14T14:30:53+00:00", "request_id": "70026", "model": "lab-mini", "ok": true, "error": null, "prompt_tokens": 961, "completion_tokens": 284, "latency_ms": 394}
{"ts": "2026-03-14T17:05:14+00:00", "request_id": "70033", "model": "lab-fast", "ok": true, "error": null, "prompt_tokens": 718, "completion_tokens": 136, "latency_ms": 2225}
{"ts": "2026-03-14T17:09:44+00:00", "request_id": "70027", "model": "lab-mini", "ok": true, "error": null, "prompt_tokens": 2524, "completion_tokens": 33, "latency_ms": 3405}
{"ts": "2026-03-14T20:51:41+00:00", "request_id": "70038", "model": "lab-mini", "ok": true, "error": null, "prompt_tokens": 898, "completion_tokens": 333, "latency_ms": 3685}
{"ts": "2026-03-14T21:22:46+00:00", "request_id": "70031", "model": "lab-mini", "ok": true, "error": null, "prompt_tokens": 418, "completion_tokens": 34, "latency_ms": 3536}
{"ts": "2026-03-14T21:39:57+00:00", "request_id": "70034", "model": "lab-mini", "ok": true, "error": null, "prompt_tokens": 2799, "completion_tokens": 20, "latency_ms": 2263}
EOF
cat > prices.json <<'EOF'
{
  "lab-mini": {
    "input": 0.1,
    "output": 0.4
  },
  "lab-fast": {
    "input": 0.4,
    "output": 1.6
  },
  "lab-smart": {
    "input": 3.0,
    "output": 15.0
  }
}
EOF
```

## What to build

Write `/root/fde-lab/35-observability/report.py`, used as `python report.py LOG DATE PRICES`. For calls whose `ts` starts with `DATE`, print JSON:

```json
{"date": "2026-03-13", "calls": 15, "errors": 2, "cost_usd": 0.0213,
 "by_model": {"lab-fast": {"calls": 6, "cost_usd": 0.0041}, "...": {}},
 "p95_latency_ms": 3610}
```

- `cost_usd` from the token counts and prices, rounded to 4 decimals (per model too). Failed calls have 0 tokens.
- `by_model` keys sorted by name.
- `p95_latency_ms` by nearest rank over **all** that day's calls: sort, then take item `ceil(0.95 x n) - 1`.

```bash
cd /root/fde-lab/35-observability
python report.py pilot-calls.jsonl 2026-03-13 prices.json
```

What did the pilot cost on the 13th, and which model drove it?

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Sum the unrounded costs and round once at the end - rounding each call first gives a slightly different total.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/35-observability
cat > report.py <<'EOF'
import json
import math
import sys


def cost(row, prices):
    p = prices[row["model"]]
    return (row["prompt_tokens"] * p["input"] + row["completion_tokens"] * p["output"]) / 1_000_000


def report(rows, day, prices):
    rows = [r for r in rows if r["ts"].startswith(day)]
    by_model = {}
    for r in rows:
        m = by_model.setdefault(r["model"], {"calls": 0, "cost_usd": 0.0})
        m["calls"] += 1
        m["cost_usd"] += cost(r, prices)
    latencies = sorted(r["latency_ms"] for r in rows)
    return {
        "date": day,
        "calls": len(rows),
        "errors": sum(not r["ok"] for r in rows),
        "cost_usd": round(sum(cost(r, prices) for r in rows), 4),
        "by_model": {k: {"calls": v["calls"], "cost_usd": round(v["cost_usd"], 4)} for k, v in sorted(by_model.items())},
        "p95_latency_ms": latencies[math.ceil(0.95 * len(latencies)) - 1] if latencies else None,
    }


if __name__ == "__main__":
    log, day, prices = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
    rows = [json.loads(l) for l in open(log) if l.strip()]
    print(json.dumps(report(rows, day, prices), indent=2))

EOF
python report.py pilot-calls.jsonl 2026-03-13 prices.json
```

</details>

## Check your work

```bash
D=/root/fde-lab/35-observability; cd $D 2>/dev/null || echo "❌ create $D"
python - <<'PYEOF'
import json, math, os, subprocess, sys
from pathlib import Path
from openai import OpenAI
_C = OpenAI()
sys.excepthook = lambda t, e, tb: print(f"❌ check stopped: {t.__name__}: {e}")
def E(xs):
    return [d.embedding for d in _C.embeddings.create(model="lab-embed", input=xs).data]
def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))
def ok(cond, good, bad):
    print(("✅ " + good) if cond else ("❌ " + bad))
def load(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None
def run(*args, cwd=None):
    r = subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=cwd)
    return r.returncode, r.stdout.strip(), r.stderr.strip()
rows = [{'ts': '2026-04-01T06:13:11+00:00', 'request_id': '110014', 'model': 'lab-fast', 'ok': True, 'error': None, 'prompt_tokens': 1914, 'completion_tokens': 328, 'latency_ms': 2928}, {'ts': '2026-04-01T06:13:13+00:00', 'request_id': '110008', 'model': 'lab-mini', 'ok': True, 'error': None, 'prompt_tokens': 514, 'completion_tokens': 260, 'latency_ms': 1837}, {'ts': '2026-04-01T06:49:29+00:00', 'request_id': '110004', 'model': 'lab-mini', 'ok': True, 'error': None, 'prompt_tokens': 1636, 'completion_tokens': 245, 'latency_ms': 2720}, {'ts': '2026-04-01T06:53:33+00:00', 'request_id': '110003', 'model': 'lab-smart', 'ok': True, 'error': None, 'prompt_tokens': 558, 'completion_tokens': 50, 'latency_ms': 446}, {'ts': '2026-04-01T07:38:25+00:00', 'request_id': '110002', 'model': 'lab-smart', 'ok': True, 'error': None, 'prompt_tokens': 2155, 'completion_tokens': 354, 'latency_ms': 3326}, {'ts': '2026-04-01T08:45:16+00:00', 'request_id': '110006', 'model': 'lab-fast', 'ok': True, 'error': None, 'prompt_tokens': 1591, 'completion_tokens': 137, 'latency_ms': 2400}, {'ts': '2026-04-01T09:25:06+00:00', 'request_id': '110007', 'model': 'lab-fast', 'ok': False, 'error': 'RateLimitError: 429', 'prompt_tokens': 0, 'completion_tokens': 0, 'latency_ms': 2003}, {'ts': '2026-04-01T11:06:28+00:00', 'request_id': '110001', 'model': 'lab-smart', 'ok': True, 'error': None, 'prompt_tokens': 1542, 'completion_tokens': 92, 'latency_ms': 671}, {'ts': '2026-04-01T12:46:49+00:00', 'request_id': '110012', 'model': 'lab-smart', 'ok': True, 'error': None, 'prompt_tokens': 836, 'completion_tokens': 234, 'latency_ms': 2936}, {'ts': '2026-04-01T12:49:43+00:00', 'request_id': '110009', 'model': 'lab-fast', 'ok': True, 'error': None, 'prompt_tokens': 1405, 'completion_tokens': 192, 'latency_ms': 656}, {'ts': '2026-04-01T15:31:00+00:00', 'request_id': '110005', 'model': 'lab-mini', 'ok': True, 'error': None, 'prompt_tokens': 648, 'completion_tokens': 254, 'latency_ms': 2982}, {'ts': '2026-04-01T19:13:00+00:00', 'request_id': '110013', 'model': 'lab-fast', 'ok': False, 'error': 'RateLimitError: 429', 'prompt_tokens': 0, 'completion_tokens': 0, 'latency_ms': 150}, {'ts': '2026-04-01T19:48:59+00:00', 'request_id': '110010', 'model': 'lab-fast', 'ok': True, 'error': None, 'prompt_tokens': 783, 'completion_tokens': 88, 'latency_ms': 1309}, {'ts': '2026-04-01T20:28:32+00:00', 'request_id': '110000', 'model': 'lab-smart', 'ok': True, 'error': None, 'prompt_tokens': 2705, 'completion_tokens': 117, 'latency_ms': 1056}, {'ts': '2026-04-01T20:51:31+00:00', 'request_id': '110011', 'model': 'lab-mini', 'ok': False, 'error': 'APITimeoutError: Request timed out.', 'prompt_tokens': 0, 'completion_tokens': 0, 'latency_ms': 150}, {'ts': '2026-04-02T06:38:23+00:00', 'request_id': '110017', 'model': 'lab-smart', 'ok': True, 'error': None, 'prompt_tokens': 1822, 'completion_tokens': 338, 'latency_ms': 2156}, {'ts': '2026-04-02T06:38:40+00:00', 'request_id': '110027', 'model': 'lab-fast', 'ok': True, 'error': None, 'prompt_tokens': 606, 'completion_tokens': 266, 'latency_ms': 575}, {'ts': '2026-04-02T08:04:28+00:00', 'request_id': '110028', 'model': 'lab-fast', 'ok': True, 'error': None, 'prompt_tokens': 2536, 'completion_tokens': 208, 'latency_ms': 3318}, {'ts': '2026-04-02T08:17:13+00:00', 'request_id': '110023', 'model': 'lab-mini', 'ok': True, 'error': None, 'prompt_tokens': 1135, 'completion_tokens': 28, 'latency_ms': 583}, {'ts': '2026-04-02T09:02:32+00:00', 'request_id': '110021', 'model': 'lab-fast', 'ok': False, 'error': 'RateLimitError: 429', 'prompt_tokens': 0, 'completion_tokens': 0, 'latency_ms': 2001}, {'ts': '2026-04-02T10:05:23+00:00', 'request_id': '110025', 'model': 'lab-smart', 'ok': True, 'error': None, 'prompt_tokens': 866, 'completion_tokens': 250, 'latency_ms': 1655}, {'ts': '2026-04-02T10:13:28+00:00', 'request_id': '110015', 'model': 'lab-mini', 'ok': False, 'error': 'RateLimitError: 429', 'prompt_tokens': 0, 'completion_tokens': 0, 'latency_ms': 2001}, {'ts': '2026-04-02T10:37:02+00:00', 'request_id': '110026', 'model': 'lab-smart', 'ok': True, 'error': None, 'prompt_tokens': 373, 'completion_tokens': 263, 'latency_ms': 1764}, {'ts': '2026-04-02T10:50:58+00:00', 'request_id': '110029', 'model': 'lab-mini', 'ok': True, 'error': None, 'prompt_tokens': 1699, 'completion_tokens': 200, 'latency_ms': 647}, {'ts': '2026-04-02T12:43:24+00:00', 'request_id': '110020', 'model': 'lab-mini', 'ok': True, 'error': None, 'prompt_tokens': 2276, 'completion_tokens': 329, 'latency_ms': 621}, {'ts': '2026-04-02T13:03:02+00:00', 'request_id': '110024', 'model': 'lab-fast', 'ok': True, 'error': None, 'prompt_tokens': 1021, 'completion_tokens': 164, 'latency_ms': 1810}, {'ts': '2026-04-02T13:52:39+00:00', 'request_id': '110019', 'model': 'lab-mini', 'ok': True, 'error': None, 'prompt_tokens': 1321, 'completion_tokens': 391, 'latency_ms': 1077}, {'ts': '2026-04-02T15:24:04+00:00', 'request_id': '110016', 'model': 'lab-smart', 'ok': True, 'error': None, 'prompt_tokens': 604, 'completion_tokens': 66, 'latency_ms': 1154}, {'ts': '2026-04-02T19:50:01+00:00', 'request_id': '110030', 'model': 'lab-fast', 'ok': True, 'error': None, 'prompt_tokens': 2347, 'completion_tokens': 313, 'latency_ms': 359}, {'ts': '2026-04-02T21:18:33+00:00', 'request_id': '110022', 'model': 'lab-fast', 'ok': True, 'error': None, 'prompt_tokens': 1018, 'completion_tokens': 388, 'latency_ms': 581}, {'ts': '2026-04-02T21:53:36+00:00', 'request_id': '110018', 'model': 'lab-mini', 'ok': True, 'error': None, 'prompt_tokens': 855, 'completion_tokens': 217, 'latency_ms': 1048}]
want = {'date': '2026-04-02', 'calls': 16, 'errors': 2, 'cost_usd': 0.0311, 'by_model': {'lab-fast': {'calls': 6, 'cost_usd': 0.0052}, 'lab-mini': {'calls': 6, 'cost_usd': 0.0012}, 'lab-smart': {'calls': 4, 'cost_usd': 0.0247}}, 'p95_latency_ms': 3318}
Path("/tmp/log35.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
rc, out, err = run("report.py", "/tmp/log35.jsonl", "2026-04-02", "prices.json")
try:
    got = json.loads(out)
except ValueError:
    got = None
ok(got == want, "the report for an unseen day matches exactly", f"expected {want} - got {out[-400:]!r} {err[-200:]}")
rc, out, err = run("report.py", "/tmp/log35.jsonl", "2026-05-01", "prices.json")
try:
    got = json.loads(out)
except ValueError:
    got = None
ok(got == {"date": "2026-05-01", "calls": 0, "errors": 0, "cost_usd": 0, "by_model": {}, "p95_latency_ms": None}, "a day with no calls reports zeros and a null p95", f"a day with no calls should give calls 0, cost 0, by_model {{}} and p95 null - got {out[-300:]!r} {err[-200:]}")
PYEOF
```

## What you learned

- Cost is tokens times per-model prices - keep prices in a file.
- Report p95 latency, not the average - the tail is where users suffer.
- A short daily report answers most of a pilot's questions before they're asked.
