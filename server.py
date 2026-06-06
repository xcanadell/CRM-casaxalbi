#!/usr/bin/env python3
"""
Servidor local per a Compres Casa Xalbi.
- Serveix el HTML a http://localhost:8765
- GET  /tickets      → llegeix tickets.json
- POST /tickets      → desa tickets.json + git commit + push
- GET  /plats        → llegeix plats.json
- POST /plats        → desa plats.json + git commit + push
- GET  /bodega       → llegeix bodega.json
- POST /bodega       → desa bodega.json + git commit + push
"""

import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8765
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TICKETS_FILE = os.path.join(BASE_DIR, "tickets.json")
PLATS_FILE   = os.path.join(BASE_DIR, "plats.json")
BODEGA_FILE  = os.path.join(BASE_DIR, "bodega.json")
CLIENTS_FILE = os.path.join(BASE_DIR, "clients.json")
HTML_FILE    = os.path.join(BASE_DIR, "compres_xalbi.html")


def git_save(files, message):
    """Commit i push automàtic dels fitxers indicats."""
    try:
        subprocess.run(["git", "add"] + files, cwd=BASE_DIR, check=True)
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=BASE_DIR
        )
        if result.returncode != 0:
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=BASE_DIR, check=True
            )
            subprocess.run(["git", "push"], cwd=BASE_DIR, check=True)
            print(f"✅ Git push: {message}")
        else:
            print("ℹ️  Sense canvis nous, no cal push")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Error git: {e}")


def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


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
            self.send_json(200, read_json(TICKETS_FILE))
        elif self.path == "/plats":
            self.send_json(200, read_json(PLATS_FILE))
        elif self.path == "/bodega":
            self.send_json(200, read_json(BODEGA_FILE))
        elif self.path == "/clients":
            self.send_json(200, read_json(CLIENTS_FILE))
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
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body.decode("utf-8"))
        except Exception as e:
            self.send_json(400, {"ok": False, "error": str(e)})
            return

        if self.path == "/tickets":
            write_json(TICKETS_FILE, data)
            git_save(["tickets.json"], "auto: actualitzacio tickets")
            self.send_json(200, {"ok": True, "count": len(data)})
        elif self.path == "/plats":
            write_json(PLATS_FILE, data)
            git_save(["plats.json"], "auto: actualitzacio plats")
            self.send_json(200, {"ok": True, "count": len(data)})
        elif self.path == "/bodega":
            write_json(BODEGA_FILE, data)
            git_save(["bodega.json"], "auto: actualitzacio bodega")
            self.send_json(200, {"ok": True, "count": len(data)})
        elif self.path == "/clients":
            write_json(CLIENTS_FILE, data)
            git_save(["clients.json"], "auto: actualitzacio clients")
            self.send_json(200, {"ok": True, "count": len(data)})
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    server = HTTPServer(("localhost", PORT), Handler)
    print(f"🚀 Servidor iniciat a http://localhost:{PORT}")
    print(f"   Prem Ctrl+C per aturar\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Servidor aturat")
