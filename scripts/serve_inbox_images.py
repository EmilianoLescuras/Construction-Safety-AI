"""Static file server with permissive CORS, rooted at the project root.

Label Studio annotates images on a <canvas>, so its frontend loads them
with crossOrigin="anonymous". A plain ``python -m http.server`` does NOT
send ``Access-Control-Allow-Origin``, so the browser blocks the
cross-origin image (LS on :8081 fetching from this server on :8082) and
shows "There was an issue loading URL from $image value".

This server adds ``Access-Control-Allow-Origin: *`` (plus a no-store
cache header so re-exports show fresh pixels), which is exactly what LS's
error hint asks for. Pair it with::

    .venv/bin/python scripts/yolo_to_labelstudio.py --http-base http://localhost:8082
"""
from __future__ import annotations

import argparse
import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self) -> None:  # noqa: N802 (http.server naming)
        self.send_response(200)
        self.end_headers()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=int(os.environ.get("IMG_PORT", 8082)))
    parser.add_argument("--bind", default="127.0.0.1")
    args = parser.parse_args()

    handler = partial(CORSRequestHandler, directory=str(PROJECT_ROOT))
    httpd = ThreadingHTTPServer((args.bind, args.port), handler)
    print(f"[serve-images] root={PROJECT_ROOT}")
    print(f"[serve-images] CORS-enabled → http://localhost:{args.port}/"
          f"datasets/v2_inbox/images/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[serve-images] stopped")


if __name__ == "__main__":
    main()
