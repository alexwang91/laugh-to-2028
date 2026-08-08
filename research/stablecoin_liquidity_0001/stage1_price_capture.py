from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ASSETS = ("BTC", "ETH", "SOL", "BNB", "XRP")
SYMBOLS = {asset: f"{asset}USDT" for asset in ASSETS}
ENDPOINTS = (
    "https://data-api.binance.vision/api/v3/klines",
    "https://api.binance.com/api/v3/klines",
)
DAY_MS = 86_400_000
START_MS = int(datetime(2020, 8, 1, tzinfo=timezone.utc).timestamp() * 1000)
END_EXCLUSIVE_MS = int(datetime(2026, 8, 8, tzinfo=timezone.utc).timestamp() * 1000)
SOURCE_ID = "BINANCE_SPOT_KLINES_V1"
CAPTURE_ID = "STABLECOIN-LIQUIDITY-0001-STAGE1-BINANCE-CAPTURE-V1"
_CAPTURED_HEADERS = ("content-type", "date", "etag", "last-modified")


class PriceCaptureError(RuntimeError):
    pass


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _write_exclusive(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    with os.fdopen(fd, "wb", closefd=True) as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())


def _selected_headers(headers) -> dict[str, str]:
    lowered = {str(k).lower(): str(v) for k, v in headers.items()}
    return {k: lowered[k] for k in _CAPTURED_HEADERS if k in lowered}


def _fetch_once(symbol: str, cursor: int) -> tuple[bytes, dict[str, object]]:
    params = {
        "symbol": symbol,
        "interval": "1d",
        "timeZone": "0",
        "startTime": cursor,
        "endTime": END_EXCLUSIVE_MS - 1,
        "limit": 1000,
    }
    last_error: Exception | None = None
    for endpoint in ENDPOINTS:
        url = f"{endpoint}?{urlencode(params)}"
        started = datetime.now(timezone.utc)
        request = Request(url, method="GET", headers={"Accept": "application/json"})
        try:
            with urlopen(request, timeout=45.0) as response:  # nosec B310: frozen HTTPS source
                raw = response.read()
                status = int(getattr(response, "status", response.getcode()))
                headers = _selected_headers(response.headers)
            retrieved = datetime.now(timezone.utc)
            if status != 200:
                raise PriceCaptureError(f"HTTP {status}")
            return raw, {
                "endpoint": endpoint,
                "request_url": url,
                "retrieval_started_at": _iso(started),
                "retrieved_at": _iso(retrieved),
                "http_status": status,
                "response_headers": headers,
            }
        except Exception as exc:  # transport fallback occurs only before any result evaluation
            last_error = exc
    raise PriceCaptureError(f"Could not fetch {symbol} cursor={cursor}: {type(last_error).__name__}")


def capture(root: Path) -> dict[str, object]:
    root = Path(root)
    if not root.is_absolute():
        raise PriceCaptureError("capture root must be absolute")
    if root.exists() and any(p.is_file() for p in root.rglob("*")):
        raise PriceCaptureError("capture root already contains files; refusing second capture")

    pages: list[dict[str, object]] = []
    for asset in ASSETS:
        symbol = SYMBOLS[asset]
        cursor = START_MS
        page_number = 0
        seen_open_ms: set[int] = set()
        while cursor < END_EXCLUSIVE_MS:
            raw, metadata = _fetch_once(symbol, cursor)
            digest = _sha(raw)
            relative = Path(asset) / f"page-{page_number:03d}__{digest}.json"
            path = root / relative
            _write_exclusive(path, raw)

            # Pagination parses only the already-persisted bytes. No research calculation occurs here.
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, list):
                raise PriceCaptureError(f"{symbol} page root is not a list")
            if not payload:
                break
            open_times: list[int] = []
            for row in payload:
                if not isinstance(row, list) or len(row) < 7:
                    raise PriceCaptureError(f"{symbol} malformed kline row")
                open_ms = int(row[0])
                if open_ms in seen_open_ms:
                    raise PriceCaptureError(f"{symbol} duplicate session {open_ms}")
                seen_open_ms.add(open_ms)
                open_times.append(open_ms)
            if open_times != sorted(open_times):
                raise PriceCaptureError(f"{symbol} page sessions not sorted")
            next_cursor = open_times[-1] + DAY_MS
            if next_cursor <= cursor:
                raise PriceCaptureError(f"{symbol} non-advancing cursor")

            entry = {
                "asset": asset,
                "symbol": symbol,
                "page_number": page_number,
                "requested_start_ms": cursor,
                "first_open_ms": open_times[0],
                "last_open_ms": open_times[-1],
                "row_count": len(payload),
                "raw_sha256": digest,
                "raw_size_bytes": len(raw),
                "raw_relative_path": relative.as_posix(),
                **metadata,
            }
            pages.append(entry)
            cursor = next_cursor
            page_number += 1

        if not any(page["asset"] == asset for page in pages):
            raise PriceCaptureError(f"no persisted Binance pages for {asset}")

    manifest = {
        "schema_version": 1,
        "capture_id": CAPTURE_ID,
        "research_id": "STABLECOIN-LIQUIDITY-0001",
        "run_interface_id": "STABLECOIN-LIQUIDITY-0001-RUN-INTERFACE-V1",
        "source_id": SOURCE_ID,
        "assets": list(ASSETS),
        "interval": "1d",
        "timezone": "0",
        "start_ms": START_MS,
        "end_exclusive_ms": END_EXCLUSIVE_MS,
        "page_count": len(pages),
        "pages": pages,
    }
    manifest_path = root / "BINANCE_STAGE1_CAPTURE_MANIFEST.json"
    manifest_raw = (json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    _write_exclusive(manifest_path, manifest_raw)
    summary = {
        "capture_id": CAPTURE_ID,
        "manifest_path": str(manifest_path),
        "manifest_sha256": _sha(manifest_raw),
        "page_count": len(pages),
        "row_count_by_asset": {
            asset: sum(int(page["row_count"]) for page in pages if page["asset"] == asset)
            for asset in ASSETS
        },
    }
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args(argv)
    print(json.dumps(capture(args.root), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
