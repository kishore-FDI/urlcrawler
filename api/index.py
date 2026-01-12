from http.server import BaseHTTPRequestHandler
import urllib.parse, json, re
import requests
from bs4 import BeautifulSoup

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            with open("index.html", "rb") as f:
                d = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(d)))
            self.end_headers()
            self.wfile.write(d)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        l = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(l).decode()
        data = urllib.parse.parse_qs(body)
        url = data.get("target_url", [""])[0]

        m = re.search(r"(.*?)(\d+)$", url)
        if not m:
            self.send_response(400)
            self.end_headers()
            return

        base, n = m.group(1), int(m.group(2))
        pages = [f"{base}{i}" for i in range(n, -1, -1)]

        vids = []

        for p in pages:
            try:
                r = requests.get(p, timeout=5)
                if r.status_code != 200:
                    continue
                s = BeautifulSoup(r.text, "html.parser")
                for v in s.find_all("video"):
                    cls = v.get("class", [])
                    if "hidden" in cls:
                        continue
                    src = v.get("src")
                    if not src:
                        src_tag = v.find("source")
                        if src_tag:
                            src = src_tag.get("src")
                    if src:
                        vids.append(src)
            except Exception:
                pass

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(vids).encode())
