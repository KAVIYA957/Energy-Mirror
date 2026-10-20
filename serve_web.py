import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

WEB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "mobile", "build", "web"))

class SPAHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        # Resolve requested path on disk
        req_path = self.translate_path(self.path)
        # If target file does not exist, serve index.html for Single Page Application navigation
        if not os.path.exists(req_path) and not os.path.splitext(req_path)[1]:
            self.path = "/index.html"
        return super().do_GET()

def run(port=8080):
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, SPAHandler)
    print(f"Energy Mirror Web running at http://0.0.0.0:{port} serving {WEB_DIR}", flush=True)
    httpd.serve_forever()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run(port)
