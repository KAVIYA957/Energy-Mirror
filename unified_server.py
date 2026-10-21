"""
unified_server.py - Zero-Config Unified Server & Reverse Proxy for Energy Mirror

Runs a unified HTTP server on port 5000 that serves:
1. /api/*, /docs, /openapi.json -> proxies to backend at http://127.0.0.1:8000
2. Static assets -> serves from mobile/build/web
3. SPA routes (/history, /simulator, /diagnostics) -> serves mobile/build/web/index.html

Usage:
  python unified_server.py [port]
  Default port: 5000 (proxies to backend on 8000)
"""

import http.server
import os
import socketserver
import sys
import urllib.request
import urllib.error

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(PROJECT_ROOT, "mobile", "build", "web")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
DEFAULT_PROXY_PORT = 5000


class UnifiedHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/") or self.path in ("/docs", "/openapi.json"):
            self.proxy_to_backend()
        else:
            clean_path = self.path.split("?")[0].lstrip("/")
            local_file = os.path.join(WEB_DIR, clean_path)
            if clean_path and os.path.exists(local_file) and not os.path.isdir(local_file):
                super().do_GET()
            else:
                self.serve_index()

    def do_POST(self):
        self.proxy_to_backend()

    def do_PUT(self):
        self.proxy_to_backend()

    def do_PATCH(self):
        self.proxy_to_backend()

    def do_DELETE(self):
        self.proxy_to_backend()

    def do_OPTIONS(self):
        if self.path.startswith("/api/"):
            self.proxy_to_backend()
        else:
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.end_headers()

    def serve_index(self):
        index_file = os.path.join(WEB_DIR, "index.html")
        if not os.path.exists(index_file):
            self.send_error(404, "Flutter web build not found. Please run 'flutter build web --release' in mobile/ first.")
            return
        with open(index_file, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(content)

    def proxy_to_backend(self):
        target_url = f"http://127.0.0.1:{BACKEND_PORT}{self.path}"
        body = None
        if "Content-Length" in self.headers:
            length = int(self.headers["Content-Length"])
            body = self.rfile.read(length)

        req_headers = {k: v for k, v in self.headers.items() if k.lower() != "host"}
        req = urllib.request.Request(target_url, data=body, headers=req_headers, method=self.command)

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in ("transfer-encoding", "content-length"):
                        self.send_header(k, v)
                content = resp.read()
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for k, v in e.headers.items():
                if k.lower() not in ("transfer-encoding", "content-length"):
                    self.send_header(k, v)
            content = e.read()
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(502, f"Bad Gateway (Backend unreachable at http://127.0.0.1:{BACKEND_PORT}): {e}")


def run(port=DEFAULT_PROXY_PORT):
    print(f"Energy Mirror Unified Web & API Proxy starting on port {port}...", flush=True)
    print(f"Serving Flutter Web SPA from: {WEB_DIR}", flush=True)
    print(f"Proxying /api/* calls to backend at: http://127.0.0.1:{BACKEND_PORT}", flush=True)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", port), UnifiedHandler) as httpd:
        print(f"Unified Server is running at http://localhost:{port} (and http://0.0.0.0:{port})", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down Unified Server safely...", flush=True)
            httpd.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PROXY_PORT
    run(port)
