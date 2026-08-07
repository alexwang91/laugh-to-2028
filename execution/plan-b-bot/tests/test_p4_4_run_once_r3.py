from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "research" / "leverage_0040"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

MODULE = HERE / "run_leverage_0040_once_r3.py"
spec = importlib.util.spec_from_file_location("leverage_0040_r3", MODULE)
assert spec and spec.loader
r3 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r3
spec.loader.exec_module(r3)


def test_r3_starting_liquidatable_state_becomes_zero_distance_failure(monkeypatch):
    idx = pd.DatetimeIndex([pd.Timestamp("2025-01-01")])
    candidate = pd.DataFrame(
        [{"BTC": 0.0, "ETH": 0.25, "SOL": 0.0, "BNB": 0.0}], index=idx
    )
    matched = candidate.copy()

    monkeypatch.setattr(r3.base, "load_frozen_snapshot", lambda: {})
    monkeypatch.setattr(
        r3.base,
        "evaluate_cross_margin_state",
        lambda **kwargs: SimpleNamespace(liquidatable=True),
    )

    def forbidden_distance(**kwargs):
        raise AssertionError("distance solver must not run from liquidatable start")

    monkeypatch.setattr(
        r3.base, "uniform_long_down_liquidation_distance", forbidden_distance
    )

    out = r3._minimum_liquidation_distance_r3(candidate, matched)
    assert out == {
        "pass": False,
        "minimum_uniform_down_move": 0.0,
        "worst_date": "2025-01-01",
    }


def test_r3_correction_record_changes_no_economic_parameter():
    data = __import__("json").loads(
        (HERE / "LEVERAGE-0040-PRE-RESULT-CORRECTION-R3.json").read_text(
            encoding="utf-8"
        )
    )
    assert data["correction_id"] == "PREFLIGHT-LIQUIDATION-START-004"
    assert data["evidence"]["immutable_result_written"] is False
    assert data["evidence"]["cap_gt_1_metrics_emitted_to_stdout"] is False
    assert data["correction"]["economic_parameter_change"] is False
    assert data["correction"]["liquidation_model_changed"] is False
    assert data["correction"]["liquidation_distance_threshold_changed"] is False
