"""LiteLLM callback for the AI Engineer lab gateway.

Appends one JSON line per request to $AILAB_LOG (default /var/log/ailab/requests.jsonl) so task checkers can
see that a real call happened: when, through which API, which lab model, which client, the max_tokens and tool
settings, the finish reason and the token usage. Prompt and reply text are never written - only their shape.
"""
import json
import os
import time

from litellm.integrations.custom_logger import CustomLogger

LOG = os.environ.get("AILAB_LOG", "/var/log/ailab/requests.jsonl")


def _api(call_type, route):
    if "anthropic" in (call_type or "") or route.endswith("/messages"):
        return "messages"
    if "responses" in (call_type or ""):
        return "responses"
    return "chat.completions"


def _finish(resp):
    if isinstance(resp, dict):
        if resp.get("stop_reason"):
            return resp["stop_reason"]
        choices = resp.get("choices") or []
        if choices and isinstance(choices[0], dict):
            return choices[0].get("finish_reason")
    return None


def _tool_calls(resp):
    if not isinstance(resp, dict):
        return []
    names = []
    for c in resp.get("choices") or []:
        for tc in ((c or {}).get("message") or {}).get("tool_calls") or []:
            names.append(((tc or {}).get("function") or {}).get("name"))
    for block in resp.get("content") or []:
        if isinstance(block, dict) and block.get("type") == "tool_use":
            names.append(block.get("name"))
    return [n for n in names if n]


class AILabLogger(CustomLogger):
    def _write(self, kwargs, ok):
        p = kwargs.get("standard_logging_object") or {}
        params = p.get("model_parameters") or {}
        msgs = p.get("messages") or []
        roles = [m.get("role") for m in msgs if isinstance(m, dict)] if isinstance(msgs, list) else []
        meta = p.get("metadata") or {}
        route = str(meta.get("user_api_key_request_route") or "")
        tools = params.get("tools") or kwargs.get("tools") or []
        system = "system" in roles or bool(params.get("system") or kwargs.get("system"))
        row = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "epoch": round(time.time(), 3),
            "ok": ok,
            "api": _api(p.get("call_type"), route),
            "model": p.get("model_group") or kwargs.get("model"),
            "client": (p.get("user_agent") or "")[:80],
            "stream": bool(p.get("stream")),
            "max_tokens": params.get("max_tokens") or params.get("max_completion_tokens"),
            "temperature": params.get("temperature"),
            "json_mode": bool(params.get("response_format")),
            "system": system,
            "roles": roles,
            "tools": [((t.get("function") or t).get("name")) for t in tools if isinstance(t, dict)],
            "tool_calls": _tool_calls(p.get("response")),
            "finish_reason": _finish(p.get("response")),
            "prompt_tokens": p.get("prompt_tokens"),
            "completion_tokens": p.get("completion_tokens"),
            "total_tokens": p.get("total_tokens"),
        }
        if not ok:
            row["error"] = (p.get("error_str") or "")[:200]
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a") as f:
            f.write(json.dumps(row) + "\n")

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        self._write(kwargs, True)

    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        self._write(kwargs, False)


proxy_handler_instance = AILabLogger()
