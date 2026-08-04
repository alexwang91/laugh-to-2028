from __future__ import annotations

import json

import requests

from .config import Settings


def send_telegram(settings: Settings, payload: dict) -> None:
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return
    text = (
        "BTC Beta Bot\n"
        f"mode={payload.get('mode')} network={payload.get('network')}\n"
        f"trend={payload.get('signal', {}).get('trend_score')} "
        f"beta={payload.get('signal', {}).get('target_beta')}\n"
        f"result={payload.get('result')}\n"
        f"details={json.dumps(payload.get('plan', {}), ensure_ascii=False)[:1500]}"
    )
    requests.post(
        f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
        json={"chat_id": settings.telegram_chat_id, "text": text},
        timeout=settings.request_timeout_seconds,
    ).raise_for_status()
