from __future__ import annotations

from datetime import datetime, timezone
from urllib.request import Request, urlopen

from .raw_vintage import HttpCapture, SOURCE_URL


class SourceFetchError(RuntimeError):
    pass


def fetch_raw_snapshot(timeout_seconds: float = 30.0) -> HttpCapture:
    """Fetch exactly one raw DefiLlama response.

    This function performs no parsing, normalization, feature computation,
    retry loop, result inspection or persistence. Callers must persist the exact
    returned bytes through raw_vintage.write_snapshot before downstream use.
    """
    started = datetime.now(timezone.utc)
    request = Request(
        SOURCE_URL,
        method="GET",
        headers={"Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:  # nosec B310: frozen HTTPS source
            raw_bytes = response.read()
            status = int(getattr(response, "status", response.getcode()))
            headers = {str(key): str(value) for key, value in response.headers.items()}
    except Exception as exc:  # network failures are capture failures, not research evidence
        raise SourceFetchError(f"DefiLlama capture failed: {type(exc).__name__}") from exc
    retrieved = datetime.now(timezone.utc)
    if status != 200:
        raise SourceFetchError(f"DefiLlama capture returned HTTP {status}")
    return HttpCapture(
        raw_bytes=raw_bytes,
        retrieval_started_at=started,
        retrieved_at=retrieved,
        http_status=status,
        response_headers=headers,
    )
