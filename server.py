#!/usr/bin/env python3
"""
Servidor local per a Compres Casa Xalbi.
- Serveix el HTML a http://localhost:8765
- GET  /tickets      → llegeix tickets.json
- POST /tickets      → desa tickets.json + git commit + push
"""

import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8765
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TICKETS_FILE = os.path.join(BASE_DIR, "tickets.json")
HTML_FILE = os.path.join(BASE_DIR, "compres_xalbi.html")


def git_save():
    """Commit i push automàtic del tickets.json."""
    try:
        subprocess.run(["git", "add", "tickets.json"], cwd=BASE_DIR, check=True)
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=BASE_DIR
        )
        if result.returncode != 0:  # hi ha canvis
            subprocess.run(
                ["git", "commit", "-m", "auto: actualització tickets"],
                cwd=BASE_DIR, check=True
            )
            subprocess.run(["git", "push"], cwd=BASE_DIR, check=True)
            print("✅ Git push fet correctament")
        else:
            print("ℹ️  Sense canvis nous, no cal push")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Error git: {e}")


class Handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"  {self.command} {self.path} → {args[1]}")

    def send_json(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/tickets":
            try:
                with open(TICKETS_FILE, "r", encoding="utf-8") as f:
                    tickets = json.load(f)
                self.send_json(200, tickets)
            except FileNotFoundError:
                self.send_json(200, [])

        elif self.path in ("/", "/index.html", "/compres_xalbi.html"):
            try:
                with open(HTML_FILE, "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", len(body))
                self.end_headers()
                self.wfile.write(body)
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/tickets":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                tickets = json.loads(body.decode("utf-8"))
                with open(TICKETS_FILE, "w", encoding="utf-8") as f:
                    json.dump(tickets, f, ensure_ascii=False, indent=2)
                git_save()
                self.send_json(200, {"ok": True, "count": len(tickets)})
            except Exception as e:
                self.send_json(500, {"ok": False, "error": str(e)})
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    server = HTTPServer(("localhost", PORT), Handler)
    print(f"🚀 Servidor iniciat a http://localhost:{PORT}")
    print(f"   Dades a: {TICKETS_FILE}")
    print(f"   Prem Ctrl+C per aturar\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Servidor aturat")
