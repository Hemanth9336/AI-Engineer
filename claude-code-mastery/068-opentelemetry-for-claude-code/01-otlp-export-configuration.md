---
type: lesson
title: "OTLP export configuration"
minutes: 12
---

Envelopes (topics 066-067) cover runs you start from scripts. **OpenTelemetry** covers every session on every machine, including interactive ones. Claude Code exports metrics, events (OTel logs) and, in beta, traces over OTLP to any collector you point it at.

## Turning it on

```bash
export CLAUDE_CODE_ENABLE_TELEMETRY=1                 # the master switch; nothing is sent without it
export OTEL_METRICS_EXPORTER=otlp                     # otlp, prometheus, console, or none
export OTEL_LOGS_EXPORTER=otlp                        # events: prompts, API requests, tool results
export OTEL_EXPORTER_OTLP_PROTOCOL=http/json          # or http/protobuf, grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer $COLLECTOR_TOKEN"   # if your collector needs auth
export OTEL_METRIC_EXPORT_INTERVAL=10000             # ms; the default is 60000. Lower it while testing
export OTEL_LOGS_EXPORT_INTERVAL=5000                # ms

# traces (beta): spans for each interaction, model request, and tool call
export CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1
export OTEL_TRACES_EXPORTER=otlp
```

With `http/json` or `http/protobuf`, the exporter POSTs to `<endpoint>/v1/metrics`, `/v1/logs` and `/v1/traces`. Per-signal overrides exist (`OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, `..._LOGS_...`, `..._TRACES_...`) when the signals go to different backends.

## Where to set it

| Scope | How |
|---|---|
| Just you, just now | Environment variables, as above |
| A project | The `env` block in `.claude/settings.json` |
| The whole organization | The `env` block in **managed settings** (topic 070), so users can't turn it off. Pair it with `otelHeadersHelper`, a script that prints auth headers, to keep tokens out of the file |

## A collector you control

For learning, or a single machine, a collector can be a 20-line HTTP server that saves each POST body. In production, run the OpenTelemetry Collector, and forward from there to Prometheus, Datadog, Honeycomb, Grafana or whatever you already use. Claude Code doesn't care which, as long as it speaks OTLP.

Exports are batched. A short `claude -p` run flushes on exit, but give the collector a moment before you stop it.

## Commands this node introduces

`CLAUDE_CODE_ENABLE_TELEMETRY`, `OTEL_METRICS_EXPORTER`, `OTEL_LOGS_EXPORTER`, `OTEL_TRACES_EXPORTER`, `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA`, `OTEL_EXPORTER_OTLP_PROTOCOL`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_HEADERS`, `OTEL_METRIC_EXPORT_INTERVAL`, `OTEL_LOGS_EXPORT_INTERVAL`, and `otelHeadersHelper`.
