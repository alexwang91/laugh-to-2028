import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
AUDIT_ID = "PIT-UNIVERSE-0001-DISCOVERY"
S3_URL = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
DATA_API = "https://data-api.binance.vision"
ROOT_PREFIX = "data/spot/monthly/klines/"

STABLE_BASES = {
    "USDC", "BUSD", "TUSD", "FDUSD", "USDP", "DAI", "UST", "USTC", "PAX", "SUSD", "EUR", "AEUR"
}
LEVERAGED_SUFFIXES = ("UP", "DOWN", "BULL", "BEAR")


def s3_list(prefix: str, delimiter: str | None = None, max_keys: int = 1000):
    items = []
    prefixes = []
    token = None
    while True:
        params = {"list-type": "2", "prefix": prefix, "max-keys": str(max_keys)}
        if delimiter is not None:
            params["delimiter"] = delimiter
        if token:
            params["continuation-token"] = token
        r = requests.get(S3_URL, params=params, timeout=45)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        ns = "{http://s3.amazonaws.com/doc/2006-03-01/}"
        for cp in root.findall(f"{ns}CommonPrefixes"):
            el = cp.find(f"{ns}Prefix")
            if el is not None and el.text:
                prefixes.append(el.text)
        for content in root.findall(f"{ns}Contents"):
            key = content.find(f"{ns}Key")
            size = content.find(f"{ns}Size")
            if key is not None and key.text:
                items.append({"key": key.text, "size": int(size.text) if size is not None else None})
        truncated = root.find(f"{ns}IsTruncated")
        if truncated is None or truncated.text != "true":
            break
        nxt = root.find(f"{ns}NextContinuationToken")
        if nxt is None or not nxt.text:
            raise RuntimeError("S3 listing truncated without continuation token")
        token = nxt.text
    return prefixes, items


def archive_symbols():
    prefixes, _ = s3_list(ROOT_PREFIX, delimiter="/")
    out = []
    for p in prefixes:
        sym = p[len(ROOT_PREFIX):].strip("/")
        if sym:
            out.append(sym)
    return sorted(set(out))


def current_symbols():
    r = requests.get(f"{DATA_API}/api/v3/exchangeInfo", timeout=45)
    r.raise_for_status()
    data = r.json()
    rows = {}
    for x in data.get("symbols", []):
        rows[x["symbol"]] = {
            "status": x.get("status"),
            "baseAsset": x.get("baseAsset"),
            "quoteAsset": x.get("quoteAsset"),
            "isSpotTradingAllowed": x.get("isSpotTradingAllowed"),
        }
    return rows


def classify(symbol: str):
    if not symbol.endswith("USDT"):
        return "non_usdt"
    base = symbol[:-4]
    if base in STABLE_BASES:
        return "stable_base"
    if any(base.endswith(s) and len(base) > len(s) for s in LEVERAGED_SUFFIXES):
        return "leveraged_token_like"
    return "ordinary_usdt_candidate"


def dated_1d_files(symbol: str):
    prefix = f"{ROOT_PREFIX}{symbol}/1d/"
    _, items = s3_list(prefix)
    pat = re.compile(rf"/{re.escape(symbol)}-1d-(\d{{4}}-\d{{2}})\.zip$")
    months = []
    for item in items:
        m = pat.search(item["key"])
        if m:
            months.append(m.group(1))
    months = sorted(set(months))
    return {
        "symbol": symbol,
        "monthly_1d_file_count": len(months),
        "first_month": months[0] if months else None,
        "last_month": months[-1] if months else None,
        "sample_first": months[:3],
        "sample_last": months[-3:] if months else [],
    }


def main():
    arc = archive_symbols()
    cur = current_symbols()
    arc_usdt = sorted(s for s in arc if s.endswith("USDT"))
    cur_usdt = sorted(s for s, x in cur.items() if x.get("quoteAsset") == "USDT")
    arc_set = set(arc_usdt)
    cur_set = set(cur_usdt)
    archive_only = sorted(arc_set - cur_set)
    current_only = sorted(cur_set - arc_set)
    common = sorted(arc_set & cur_set)

    class_counts = {}
    for s in arc_usdt:
        c = classify(s)
        class_counts[c] = class_counts.get(c, 0) + 1

    ordinary_archive_only = [s for s in archive_only if classify(s) == "ordinary_usdt_candidate"]
    ordinary_common = [s for s in common if classify(s) == "ordinary_usdt_candidate"]

    sample_syms = []
    for group in (ordinary_archive_only[:5], ordinary_archive_only[-5:], ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]):
        for s in group:
            if s in arc_set and s not in sample_syms:
                sample_syms.append(s)
    sample_files = []
    for s in sample_syms[:14]:
        try:
            sample_files.append(dated_1d_files(s))
        except Exception as e:
            sample_files.append({"symbol": s, "error": repr(e)})

    report = {
        "audit_id": AUDIT_ID,
        "trading_changes": False,
        "s3_root_prefix": ROOT_PREFIX,
        "archive_symbol_count_all_quotes": len(arc),
        "archive_usdt_symbol_count": len(arc_usdt),
        "current_exchangeinfo_usdt_symbol_count": len(cur_usdt),
        "common_usdt_symbol_count": len(common),
        "archive_only_usdt_count": len(archive_only),
        "current_only_usdt_count": len(current_only),
        "archive_usdt_classification_counts": class_counts,
        "ordinary_archive_only_count": len(ordinary_archive_only),
        "ordinary_common_count": len(ordinary_common),
        "archive_only_usdt_symbols": archive_only,
        "ordinary_archive_only_usdt_symbols": ordinary_archive_only,
        "current_only_usdt_symbols": current_only,
        "dated_file_discovery_samples": sample_files,
        "success_criteria": {
            "archive_prefix_enumeration": len(arc) > 0,
            "historical_inactive_candidates_found": len(ordinary_archive_only) > 0,
            "dated_1d_files_discoverable": any(x.get("monthly_1d_file_count", 0) > 0 for x in sample_files),
        },
        "interpretation": "Archive-only ordinary USDT pairs demonstrate that a candidate universe can include assets that later disappeared. This is discovery only; it does not establish historical eligibility, which must be based on point-in-time age/liquidity in a separately preregistered construction audit."
    }
    (HERE / "archive_discovery_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        k: v for k, v in report.items() if k not in {"archive_only_usdt_symbols", "ordinary_archive_only_usdt_symbols", "current_only_usdt_symbols"}
    }, indent=2))
    print("archive_only_examples", ordinary_archive_only[:30])
    print("current_only_examples", current_only[:30])


if __name__ == "__main__":
    main()
