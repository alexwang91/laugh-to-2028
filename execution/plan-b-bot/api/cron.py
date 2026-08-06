from http.server import BaseHTTPRequestHandler
import hmac
import json

from beta_bot.config import Settings
from beta_bot.service import run_strategy


def _authorized(headers, settings: Settings) -> bool:
    """Fail closed unless the caller presents the configured cron bearer secret."""
    if not settings.cron_secret:
        return False
    auth = headers.get("Authorization") or ""
    expected = f"Bearer {settings.cron_secret}"
    return hmac.compare_digest(auth, expected)


def _public_error_payload(exc: Exception) -> dict:
    """Expose only the exception class; detailed messages stay server-side."""
    return {"ok": False, "error": type(exc).__name__}


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
            payload = _public_error_payload(exc)
            status = 500

        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
