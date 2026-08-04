from http.server import BaseHTTPRequestHandler
import json

from beta_bot.config import Settings
from beta_bot.service import run_public_market_status


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            payload = run_public_market_status(Settings.from_env())
            status = 200
        except Exception as exc:
            payload = {"ok": False, "error": type(exc).__name__, "message": str(exc)}
            status = 500
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
