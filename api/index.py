from http.server import BaseHTTPRequestHandler
import urllib.parse
import json
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            with open("index.html", "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n).decode()
        data = urllib.parse.parse_qs(body)
        url = data.get("target_url", [""])[0]

        m = re.search(r"(.*?)(\d+)$", url)
        if not m:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "URL must end with a number"}).encode())
            return

        base, num = m.group(1), int(m.group(2))
        urls = [f"{base}{i}" for i in range(num, -1, -1)]

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(urls).encode())
