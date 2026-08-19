from __future__ import annotations

import argparse
import http.client
import json
import ssl
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "research/brrk_crypto_carry_atlas_0072/SOURCE_ACCESS_REQUALIFICATION_PLAN.json"
REQUEST = ROOT / "research/brrk_crypto_carry_atlas_0072/ACCESS_PROBE_EXECUTION_REQUEST.json"
ALLOWED_HEADERS = {"content-type", "content-length", "last-modified", "etag", "date", "server", "via", "x-cache", "cf-ray"}


def _load_contracts():
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    request = json.loads(REQUEST.read_text(encoding="utf-8"))
    assert plan["probe_id"] == request["probe_id"]
    assert request["status"] == "PROSPECTIVE_NOT_EXECUTED"
    assert request["capture_0001_retry_forbidden"] is True
    constraints = request["execution_constraints"]
    for key in (
        "automatic_retry",
        "redirect_following",
        "response_body_read_or_persist",
        "scientific_history_payload_read",
        "scientific_computation",
        "stage8_marker_creation",
        "stage8_attempt_consumption",
        "new_source_admission",
        "source_precedence_change",
        "new_feature_family_admission",
        "ad_hoc_additional_host_probe",
    ):
        assert constraints[key] is False
    probes = plan["probes"]
    assert [p["canonical_probe_id"] for p in probes] == request["allowed_probe_set"]
    assert len(probes) == 2
    assert probes[0]["host"] == "data.binance.vision" and probes[0]["http_method"] == "HEAD"
    assert probes[1]["host"] == "api.bybit.com" and probes[1]["http_method"] == "GET_HEADERS_ONLY_NO_BODY_READ"
    return plan, request


def _probe(row):
    parsed = urlsplit(row["url"])
    assert parsed.scheme == "https"
    assert parsed.hostname == row["host"]
    path = parsed.path + (("?" + parsed.query) if parsed.query else "")
    method = "HEAD" if row["http_method"] == "HEAD" else "GET"
    conn = http.client.HTTPSConnection(parsed.hostname, parsed.port or 443, timeout=20, context=ssl.create_default_context())
    status = None
    headers = {}
    failure = None
    try:
        conn.request(method, path, headers={"User-Agent": "BRRK-0072-access-probe/1"})
        response = conn.getresponse()
        status = response.status
        headers = {k.lower(): v for k, v in response.getheaders() if k.lower() in ALLOWED_HEADERS}
        # Deliberately never call response.read(); close immediately after status/headers.
        response.close()
    except Exception as exc:
        failure = type(exc).__name__
    finally:
        conn.close()
    return {
        "probe_id": "BRRK-CRYPTO-CARRY-ATLAS-0072-ACCESS-PROBE-0001",
        "canonical_probe_id": row["canonical_probe_id"],
        "source_id": row["source_id"],
        "host": row["host"],
        "http_method": row["http_method"],
        "http_status_or_transport_failure_class": status if status is not None else failure,
        "selected_non_secret_response_headers": headers,
        "probed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-contract", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    plan, request = _load_contracts()
    if args.validate_contract:
        print("ACCESS_PROBE_CONTRACT_VALID")
        return
    if not args.execute or not args.output:
        raise SystemExit("execution requires --execute --output")
    evidence = {
        "schema_version": 1,
        "research_id": request["research_id"],
        "request_id": request["request_id"],
        "probe_id": request["probe_id"],
        "scientific_payload_read": False,
        "stage8_attempt_consumed": 0,
        "controlled_scientific_history_reads_to_researcher": 0,
        "results": [_probe(row) for row in plan["probes"]],
    }
    Path(args.output).write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
