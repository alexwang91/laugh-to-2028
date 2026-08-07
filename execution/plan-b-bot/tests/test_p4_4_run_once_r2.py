from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "research" / "leverage_0040"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

MODULE = HERE / "run_leverage_0040_once_r2.py"
spec = importlib.util.spec_from_file_location("leverage_0040_r2", MODULE)
assert spec and spec.loader
r2 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r2
spec.loader.exec_module(r2)


def test_r2_gap_stress_fails_closed_on_zero_cross_equity_with_perp_notional():
    idx = pd.DatetimeIndex([pd.Timestamp("2025-01-01")])
    candidate = pd.DataFrame(
        [{"BTC": 1.0, "ETH": 1e-12, "SOL": 0.0, "BNB": 0.0}],
        index=idx,
    )
    matched = pd.DataFrame(
        [{"BTC": 1.0, "ETH": 0.0, "SOL": 0.0, "BNB": 0.0}],
        index=idx,
    )
    out = r2._gap_stress_r2(candidate, matched)
    assert out
    assert all(row["liquidation_pass"] is False for row in out.values())
    assert all(row["liquidatable"] is True for row in out.values())


def test_r2_correction_record_freezes_no_economic_change_before_cap_gt_1():
    data = __import__("json").loads(
        (HERE / "LEVERAGE-0040-PRE-RESULT-CORRECTION-R2.json").read_text(
            encoding="utf-8"
        )
    )
    assert data["correction_id"] == "PREFLIGHT-GAP-CROSS-EQUITY-003"
    assert data["evidence"]["cap_gt_1_constructed_before_failure"] is False
    assert data["evidence"]["immutable_result_written"] is False
    assert data["correction"]["economic_parameter_change"] is False
    assert data["correction"]["liquidation_model_changed"] is False
