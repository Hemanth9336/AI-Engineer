"""Local embedding service for the AI Engineer lab: an OpenAI-compatible POST /v1/embeddings endpoint.

The lab gateway routes the `lab-embed` model here, so embeddings work the same with every provider profile and
cost nothing. It runs all-MiniLM-L6-v2 (384 dimensions) on the CPU through Chroma's bundled ONNX build.

  python embed_server.py [--host 127.0.0.1] [--port 4001]
"""
import argparse
import base64
import json
import struct
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

MODEL = "all-minilm-l6-v2"
MAX_INPUTS = 2048
EMBED = DefaultEmbeddingFunction()


def vectors(texts):
    return [[float(x) for x in v] for v in EMBED(texts)]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _json(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _error(self, code, message):
        self._json(code, {"error": {"message": message, "type": "invalid_request_error"}})

    def do_GET(self):
        if self.path.rstrip("/").endswith("/models"):
            return self._json(200, {"object": "list", "data": [{"id": MODEL, "object": "model"}]})
        self._json(200, {"ok": True, "model": MODEL})

    def do_POST(self):
        if not self.path.rstrip("/").endswith("/embeddings"):
            return self._error(404, "only /v1/embeddings is served here")
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except json.JSONDecodeError:
            return self._error(400, "the request body is not valid JSON")
        texts = body.get("input")
        if isinstance(texts, str):
            texts = [texts]
        if not isinstance(texts, list) or not texts or not all(isinstance(t, str) for t in texts):
            return self._error(400, "input must be a string or a list of strings (with LangChain's OpenAIEmbeddings, "
                                    "set check_embedding_ctx_length=False)")
        if len(texts) > MAX_INPUTS:
            return self._error(400, f"at most {MAX_INPUTS} inputs per request")
        if any(not t.strip() for t in texts):
            return self._error(400, "input strings must not be empty")
        vecs = vectors(texts)
        b64 = body.get("encoding_format") == "base64"
        data = [{"object": "embedding", "index": i,
                 "embedding": base64.b64encode(struct.pack(f"<{len(v)}f", *v)).decode() if b64 else v}
                for i, v in enumerate(vecs)]
        tokens = sum(max(1, round(len(t.split()) * 1.3)) for t in texts)
        self._json(200, {"object": "list", "data": data, "model": MODEL,
                         "usage": {"prompt_tokens": tokens, "total_tokens": tokens}})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=4001)
    args = ap.parse_args()
    vectors(["warm up"])
    print(f"embedding service ({MODEL}) on http://{args.host}:{args.port}/v1/embeddings", file=sys.stderr, flush=True)
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
