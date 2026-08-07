from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
P5 = ROOT / "research" / "cycle_exit"
if str(P5) not in sys.path:
    sys.path.insert(0, str(P5))

import run_p5_2_feature_evidence_r2 as r2


def test_series_frame_preserves_index_and_values_without_names_keyword():
    idx = pd.date_range("2025-01-01 04:00:00", periods=3, freq="4h")
    s = pd.Series([1.5, 2.5, 3.5], index=idx)
    frame = r2._series_frame(s, "completion_boundary", "close")
    assert list(frame.columns) == ["completion_boundary", "close"]
    assert frame["completion_boundary"].tolist() == list(idx)
    assert frame["close"].tolist() == [1.5, 2.5, 3.5]


def test_r2_provenance_declares_no_research_definition_change():
    assert r2.CORRECTION_ID == "P5.2-POST-COMPUTE-SERIALIZATION-R2"
    assert r2.PRIOR_RUN == 31217880218
