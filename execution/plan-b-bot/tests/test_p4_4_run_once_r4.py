from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "research" / "leverage_0040"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

MODULE = HERE / "run_leverage_0040_once_r4.py"
spec = importlib.util.spec_from_file_location("leverage_0040_r4", MODULE)
assert spec and spec.loader
r4 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r4
spec.loader.exec_module(r4)


def test_r4_funding_inputs_include_prior_decision_day_but_keep_frozen_window():
    start = r4.base.COMMON_FUNDING_START
    idx = pd.date_range(start - pd.Timedelta(days=2), start + pd.Timedelta(days=2), freq="D")
    prices = pd.DataFrame({a: range(100, 100 + len(idx)) for a in r4.base.ASSETS}, index=idx, dtype=float)
    targets = pd.DataFrame(
        {a: [0.25] * len(idx) for a in r4.base.ASSETS}, index=idx, dtype=float
    )
    px, ct, mt = r4._funding_inputs_r4(prices, targets, targets)
    assert px.index[0] == start - pd.Timedelta(days=1)
    assert start in px.index
    assert ct.index.equals(px.index)
    assert mt.index.equals(px.index)
    assert r4.base.COMMON_FUNDING_START == pd.Timestamp("2023-06-18")
    assert r4.base.COMMON_FUNDING_END == pd.Timestamp("2026-07-31")


def test_r4_record_is_blinded_and_not_result_driven():
    data = __import__("json").loads(
        (HERE / "LEVERAGE-0040-BLINDED-RUN-CORRECTION-R4.json").read_text(
            encoding="utf-8"
        )
    )
    assert data["correction_id"] == "BLINDED-FUNDING-SESSION-005"
    assert data["observability"]["cap_gt_1_partial_computation_occurred"] is True
    assert data["observability"]["candidate_metrics_emitted_to_stdout"] is False
    assert data["observability"]["candidate_metrics_committed"] is False
    assert data["correction"]["economic_parameter_change"] is False
    assert data["correction"]["result_driven_retuning"] is False
