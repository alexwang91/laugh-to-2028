from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARM = ROOT / "research/brrk_multi_horizon_trend_vol_target_0085/ARM_CONTRACT.json"
PARENT = ROOT / "research/brrk_crypto_multi_horizon_trend_0074/AUTHORIZED_OBJECT_MANIFEST.json"


def test_arm_binds_exact_kline_subset_without_payload_access():
    arm = json.loads(ARM.read_text(encoding="utf-8"))
    raw = PARENT.read_bytes()
    parent = json.loads(raw)

    assert hashlib.sha256(raw).hexdigest() == arm["source_binding"]["parent_manifest_sha256"]
    spec = arm["source_binding"]["filter"]
    selected = [
        row
        for row in parent["objects"]
        if row["archive_family"] == spec["archive_family"]
        and row["asset"] in spec["assets"]
        and row["symbol"] in spec["symbols"]
        and spec["first_month"] <= row["month"] <= spec["last_month"]
    ]

    assert len(selected) == arm["source_binding"]["expected_authorized_objects"] == 201
    assert len({row["staged_relative_path"] for row in selected}) == 201
    assert {row["asset"] for row in selected} == {"BTC", "ETH", "SOL"}
    assert {row["symbol"] for row in selected} == {"BTCUSDT", "ETHUSDT", "SOLUSDT"}
    assert min(row["month"] for row in selected) == "2021-01"
    assert max(row["month"] for row in selected) == "2026-07"

    for row in selected:
        assert row["staging_status"] == arm["source_binding"]["required_staging_status"]
        assert row["scientific_content_read_budget"] == 1
        assert row["staged_sha256"] == row["official_sha256"]
        assert len(row["staged_sha256"]) == 64
        assert row["staged_byte_size"] > 0
        assert row["staged_relative_path"].startswith("stage/payloads/")


def test_arm_preserves_pre_marker_and_irreversible_budgets():
    arm = json.loads(ARM.read_text(encoding="utf-8"))
    assert arm["attempt"] == "0/1"
    assert arm["attempt_consumed"] is False
    assert arm["controlled_scientific_history_reads"] == 0
    assert arm["scientific_engine_calls"] == "0/1"
    assert arm["scientific_source_network_fetches"] == 0
    assert arm["scientific_values_exposed"] is False
    assert arm["common_runner"] == "CONTROLLED_RESEARCH_RUNNER_V1"
    assert arm["execution_interface"].endswith("ControlledArchiveTrendEngine")
    assert set(arm["pre_marker_forbidden"]) >= {
        "testzip",
        "payload_decompression",
        "inner_csv_open_or_parse",
        "crc_payload_traversal",
        "scientific_row_read",
        "scientific_metric_calculation",
    }
    assert arm["production_authorized"] is False
    assert arm["signature_authorized"] is False
    assert arm["order_submission_authorized"] is False
