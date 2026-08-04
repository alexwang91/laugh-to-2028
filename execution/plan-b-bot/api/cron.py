from http.server import BaseHTTPRequestHandler
import json
import os

from beta_bot.config import Settings
from beta_bot.service import run_strategy


def _authorized(headers, settings: Settings) -> bool:
    auth = headers.get("Authorization")
    if settings.cron_secret:
        return auth == f"Bearer {settings.cron_secret}"
    # A secret is mandatory before trade mode can run. Shadow mode may be invoked by Vercel Cron.
    if settings.can_trade:
        return False
    return headers.get("User-Agent") == "vercel-cron/1.0" or os.getenv("VERCEL") is None


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            settings = Settings.from_env()
            if not _authorized(self.headers, settings):
                payload = {"ok": False, "error": "unauthorized"}
                status = 401
            else:
                payload = run_strategy(settings)
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
