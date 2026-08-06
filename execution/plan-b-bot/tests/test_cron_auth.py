import importlib.util
from pathlib import Path
from types import SimpleNamespace


def load_cron_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "api" / "cron.py"
    spec = importlib.util.spec_from_file_location("cron_api_for_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_shadow_request_without_secret_rejects_spoofed_vercel_user_agent():
    cron = load_cron_module()
    settings = SimpleNamespace(cron_secret=None)
    headers = {"User-Agent": "vercel-cron/1.0"}
    assert not cron._authorized(headers, settings)


def test_cron_authorization_requires_exact_bearer_secret():
    cron = load_cron_module()
    settings = SimpleNamespace(cron_secret="correct-secret")
    assert cron._authorized({"Authorization": "Bearer correct-secret"}, settings)
    assert not cron._authorized({"Authorization": "Bearer wrong-secret"}, settings)
    assert not cron._authorized({}, settings)


def test_public_500_payload_does_not_echo_exception_message():
    cron = load_cron_module()
    payload = cron._public_error_payload(ValueError("sensitive internal detail"))
    assert payload == {"ok": False, "error": "ValueError"}
    assert "sensitive internal detail" not in str(payload)
