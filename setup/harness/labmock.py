"""labmock - a scripted stand-in for a chat model, for testing harness code without a real model.

It speaks the OpenAI-compatible /v1/chat/completions API, so any harness that uses `OpenAI()` (and reads
OPENAI_BASE_URL / OPENAI_API_KEY from the environment) can run against it unchanged. Instead of thinking, it
replays a script you wrote, so you can make the "model" loop forever, call a tool with bad arguments, or answer
after exactly three steps - every time.

A script is a list of steps. Which step a request gets is decided by how many assistant messages are already in
that request's history: the first call gets step 0, the call after one assistant turn gets step 1, and so on. Past
the end, the last step repeats (so a script of one tool call is a model that never stops).

Steps:
    "some text"                                   a plain text reply
    {"text": "...", "usage": [120, 30]}           text, with prompt/completion token counts to report
    {"tool": "read_file", "args": {"path": "a"}}  one tool call
    {"calls": [{"tool": ..., "args": ...}, ...]}  several tool calls in one reply
    {"tool": "read_file", "raw_args": "{bad"}     a tool call whose arguments are not valid JSON
    any step may add "delay": seconds             wait before replying

Several conversations at once (subagents, parallel agents): pass rules instead of a script. Each rule's regex is
searched in the request's first user message (or "on": "system" / "all" / "tools" - the tool definitions as
JSON); the first match's steps are used.

    from labmock import MockModel
    with MockModel(["Hello!"]) as m:
        rc, out, err = m.run(["python", "agent.py", "hi"])
        print(m.requests[0]["messages"])

From the shell:  python /opt/harness/labmock.py script.json --port 4599
then run your harness with OPENAI_BASE_URL=http://127.0.0.1:4599/v1 OPENAI_API_KEY=mock.
"""
import json
import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import re


def _text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(p.get("text", "") for p in content if isinstance(p, dict))
    return ""


class MockModel:
    def __init__(self, script=None, rules=None, fail_first=0, delay=0.0, port=0):
        self.rules = list(rules or [])
        if script is not None:
            self.rules.append({"match": "", "steps": script})
        self.fail_first = fail_first
        self.delay = delay
        self.port = port
        self.requests = []
        self.events = []
        self._lock = threading.Lock()

    def _steps(self, msgs, tools=None):
        first_user = next((_text(m.get("content")) for m in msgs if m.get("role") == "user"), "")
        system = "\n".join(_text(m.get("content")) for m in msgs if m.get("role") == "system")
        everything = "\n".join(_text(m.get("content")) for m in msgs)
        for r in self.rules:
            hay = {"system": system, "all": everything, "tools": json.dumps(tools or [])}.get(r.get("on"), first_user)
            if re.search(r["match"], hay, re.S | re.I):
                return r["steps"]
        return ["(labmock) no scripted reply for this conversation"]

    def reply(self, body):
        msgs = body.get("messages") or []
        steps = self._steps(msgs, body.get("tools"))
        turn = sum(1 for m in msgs if m.get("role") == "assistant")
        step = steps[min(turn, len(steps) - 1)]
        if isinstance(step, str):
            step = {"text": step}
        time.sleep(step.get("delay", self.delay))
        msg, finish = {"role": "assistant", "content": None}, "stop"
        calls = step.get("calls") or ([{k: v for k, v in step.items() if k in ("tool", "args", "raw_args")}] if "tool" in step else [])
        if calls:
            finish = "tool_calls"
            msg["tool_calls"] = [{"id": f"call_{turn}_{i}", "type": "function",
                                  "function": {"name": c["tool"], "arguments": c.get("raw_args", json.dumps(c.get("args", {})))}}
                                 for i, c in enumerate(calls)]
        else:
            msg["content"] = step.get("text", "")
        prompt = sum(len(_text(m.get("content"))) for m in msgs) + len(json.dumps(body.get("tools") or []))
        p, c = step.get("usage") or [max(1, prompt // 4), max(1, len(msg["content"] or json.dumps(calls)) // 4)]
        return {"id": f"mock-{len(self.requests)}", "object": "chat.completion", "created": int(time.time()),
                "model": body.get("model", "mock"), "choices": [{"index": 0, "message": msg, "finish_reason": finish}],
                "usage": {"prompt_tokens": p, "completion_tokens": c, "total_tokens": p + c}}

    def __enter__(self):
        mock = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _send(self, code, obj):
                data = json.dumps(obj).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                self._send(200, {"object": "list", "data": [{"id": "mock", "object": "model"}]})

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                start = time.time()
                with mock._lock:
                    mock.requests.append(body)
                    failing = mock.fail_first > 0
                    mock.fail_first -= failing
                if failing:
                    return self._send(503, {"error": {"message": "labmock: scripted outage", "type": "overloaded"}})
                resp = mock.reply(body)
                with mock._lock:
                    mock.events.append({"start": start, "end": time.time()})
                self._send(200, resp)

        self.server = ThreadingHTTPServer(("127.0.0.1", self.port), H)
        self.port = self.server.server_address[1]
        self.url = f"http://127.0.0.1:{self.port}/v1"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()

    @property
    def env(self):
        return dict(os.environ, OPENAI_BASE_URL=self.url, OPENAI_API_KEY="mock-key")

    def run(self, args, cwd=None, timeout=60, input=None, env=None):
        if args and args[0] == "python":
            args = [sys.executable, *args[1:]]
        try:
            r = subprocess.run(args, cwd=cwd, env=dict(self.env, **(env or {})), capture_output=True, text=True, timeout=timeout, input=input)
            return r.returncode, r.stdout.strip(), r.stderr.strip()
        except subprocess.TimeoutExpired as e:
            out = e.stdout.decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
            return None, out.strip(), "timed out"

    def max_concurrency(self):
        ev = sorted((e["start"], 1) for e in self.events) + sorted((e["end"], -1) for e in self.events)
        best = cur = 0
        for _, d in sorted(ev, key=lambda x: (x[0], x[1])):
            cur += d
            best = max(best, cur)
        return best


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Serve a scripted chat model on 127.0.0.1.")
    ap.add_argument("script", help="JSON file: a list of steps, or {\"rules\": [...]}")
    ap.add_argument("--port", type=int, default=4599)
    a = ap.parse_args()
    spec = json.load(open(a.script))
    m = MockModel(script=spec if isinstance(spec, list) else None, rules=None if isinstance(spec, list) else spec["rules"], port=a.port)
    with m:
        print(f"labmock serving {a.script} on {m.url}  (Ctrl+C to stop)", flush=True)
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass
