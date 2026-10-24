---
type: task
title: "Fix a tool the model keeps misusing"
minutes: 10
---

## Set up

`metrics.json` holds one week of hourly values (oldest first) for each service and metric. `misuse.log` shows what the model sent to the old `get(q, t)` tool.

```bash
mkdir -p /root/harness-lab/12-tool-prompts
cd /root/harness-lab/12-tool-prompts
python - <<'EOF'
import json
data = {}
for s, (base_err, base_p95, every) in {"billing": (0.004, 180, 29), "search": (0.012, 240, 13)}.items():
    data[s] = {"error_rate": [round(base_err + (h % 7) * 0.001, 4) for h in range(168)],
               "p95_ms": [base_p95 + (h * 37) % 90 for h in range(168)],
               "restarts": [1 if h % every == 0 else 0 for h in range(168)]}
json.dump(data, open("metrics.json", "w"))
EOF
cat > misuse.log <<'EOF'
get(q="billing errors", t="logs")                -> error: invalid input
get(q="search", t="latency yesterday")            -> error: invalid input
get(q="restarts", t="billing")                    -> error: invalid input
get(q="p95 for search last 3 days", t="metric")   -> error: invalid input
get(q="error rate", t="search 2h")                -> error: invalid input
EOF
```

## What to build

Replace the old `get(q, t)` with a tool the model can't easily misuse. Write `/root/harness-lab/12-tool-prompts/metric_tool.py` with:

1. `GET_METRIC` - a tool definition named `get_service_metric`:
   - a description of at least 60 characters saying when to use it;
   - `service`: string `enum` of exactly `billing`, `search`;
   - `metric`: string `enum` of exactly `error_rate`, `p95_ms`, `restarts`;
   - `window_hours`: `integer` with `minimum` 1 and `maximum` 168;
   - a description on every property; `required` is `service` and `metric`.
2. `get_service_metric(service, metric, window_hours=24)` using the last `window_hours` values in `metrics.json`:
   - `error_rate`: the mean, rounded to 4 decimals; `p95_ms`: the maximum; `restarts`: the sum;
   - returns `{"service", "metric", "window_hours", "value"}`.
3. Errors that teach - returned as strings, not raised:
   - unknown service: `error: unknown service '<x>'. Valid services: billing, search`
   - unknown metric: `error: unknown metric '<x>'. Valid metrics: error_rate, p95_ms, restarts`
   - `window_hours` not a whole number from 1 to 168: `error: window_hours must be a whole number from 1 to 168`

```bash
cd /root/harness-lab/12-tool-prompts
python -c "from metric_tool import get_service_metric as g; print(g('search', 'p95_ms', 6)); print(g('search', 'latency'))"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `values = METRICS[service][metric][-window_hours:]` - the newest values are at the end.
- `{{service!r}}` puts quotes around the bad value, like `'payments'`.
- `isinstance(True, int)` is `True` in Python - reject booleans explicitly if you're thorough.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/12-tool-prompts
cat > metric_tool.py <<'EOF'
import json
from pathlib import Path

METRICS = json.loads((Path(__file__).parent / "metrics.json").read_text())
SERVICES = ["billing", "search"]
NAMES = ["error_rate", "p95_ms", "restarts"]

GET_METRIC = {
    "type": "function",
    "function": {
        "name": "get_service_metric",
        "description": "Get one health metric for one Stackline service over the last N hours. Use it for questions about error rates, latency or restarts. For log lines, use search_logs instead.",
        "parameters": {
            "type": "object",
            "properties": {
                "service": {"type": "string", "enum": SERVICES, "description": "The service to measure"},
                "metric": {"type": "string", "enum": NAMES,
                           "description": "error_rate = share of failed requests, p95_ms = 95th percentile latency in ms, restarts = number of restarts"},
                "window_hours": {"type": "integer", "minimum": 1, "maximum": 168,
                                 "description": "How many hours back to look, 1 to 168 (one week). Default 24."},
            },
            "required": ["service", "metric"],
        },
    },
}


def get_service_metric(service, metric, window_hours=24):
    if service not in SERVICES:
        return f"error: unknown service {service!r}. Valid services: {', '.join(SERVICES)}"
    if metric not in NAMES:
        return f"error: unknown metric {metric!r}. Valid metrics: {', '.join(NAMES)}"
    if not isinstance(window_hours, int) or isinstance(window_hours, bool) or not 1 <= window_hours <= 168:
        return "error: window_hours must be a whole number from 1 to 168"
    values = METRICS[service][metric][-window_hours:]
    if metric == "error_rate":
        value = round(sum(values) / len(values), 4)
    elif metric == "p95_ms":
        value = max(values)
    else:
        value = sum(values)
    return {"service": service, "metric": metric, "window_hours": window_hours, "value": value}

EOF
python -c "from metric_tool import get_service_metric as g; print(g('search', 'p95_ms', 6)); print(g('search', 'latency'))"
```

</details>

## Check your work

```bash
D=/root/harness-lab/12-tool-prompts; cd $D 2>/dev/null || echo "❌ create $D"
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
sys.path.insert(0, '/opt/harness')
from labmock import MockModel
sys.path.insert(0, ".")
M = load("metrics.json")
try:
    import metric_tool as mt
    f = mt.GET_METRIC["function"]
    p = f["parameters"]
    pr = p["properties"]
    good = (f.get("name") == "get_service_metric" and len(f.get("description", "")) >= 60 and pr["service"].get("enum") == ["billing", "search"]
            and pr["metric"].get("enum") == ["error_rate", "p95_ms", "restarts"] and pr["window_hours"].get("type") == "integer"
            and pr["window_hours"].get("minimum") == 1 and pr["window_hours"].get("maximum") == 168
            and all(len(x.get("description", "")) >= 5 for x in pr.values()) and sorted(p.get("required", [])) == ["metric", "service"])
except Exception as e:
    mt, good, f = None, False, {"error": f"{type(e).__name__}: {e}"}
ok(good, "GET_METRIC: specific name, enums, a bounded integer window, every parameter described", f"GET_METRIC doesn't match the spec - got {str(f)[:300]}")
def want(s, m, w=24):
    v = M[s][m][-w:]
    return {"service": s, "metric": m, "window_hours": w, "value": round(sum(v) / len(v), 4) if m == "error_rate" else max(v) if m == "p95_ms" else sum(v)}
if mt:
    cases = [("search", "p95_ms", 6), ("billing", "error_rate", 48), ("search", "restarts", 168), ("billing", "restarts", 1)]
    got = [mt.get_service_metric(*c) for c in cases] + [mt.get_service_metric("search", "error_rate")]
    exp = [want(*c) for c in cases] + [want("search", "error_rate")]
    ok(got == exp, "values aggregate the newest window_hours values correctly (default 24)", f"expected {exp[:2]}... - got {got[:2]}...")
    e1 = mt.get_service_metric("payments", "p95_ms")
    ok(isinstance(e1, str) and e1 == "error: unknown service 'payments'. Valid services: billing, search", "an unknown service gets an error listing the valid services", f"got {e1!r}")
    e2 = mt.get_service_metric("search", "latency")
    ok(isinstance(e2, str) and e2 == "error: unknown metric 'latency'. Valid metrics: error_rate, p95_ms, restarts", "an unknown metric gets an error listing the valid metrics", f"got {e2!r}")
    bad = [mt.get_service_metric("search", "p95_ms", w) for w in (0, 169, "72", 2.5)]
    ok(all(b == "error: window_hours must be a whole number from 1 to 168" for b in bad), "out-of-range or non-integer windows are rejected with the range in the message", f"window_hours 0, 169, '72' and 2.5 should all be rejected - got {bad}")
PYEOF
```

## What you learned

- Name tools verb + specific noun, give each one job, and use descriptive parameter names.
- Enums and bounded integers make most wrong calls impossible.
- Error messages that list the valid choices turn a failed call into a correct retry.
