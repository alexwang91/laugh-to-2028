import numpy as np
import pandas as pd
import pytest

from research.brrk_idle_cash_sweep_robustness_0063 import engine as e


def test_causal_forward_fill_future_invariant():
    strategy = pd.date_range("2024-01-01", periods=5, freq="D")
    source = [pd.Timestamp("2023-12-29"), pd.Timestamp("2024-01-03")]
    got = e.causal_align_rates(strategy, source, [4.0, 5.0])
    assert np.allclose(got, [4.0, 4.0, 5.0, 5.0, 5.0])
    extended = source + [pd.Timestamp("2024-01-10")]
    got2 = e.causal_align_rates(strategy, extended, [4.0, 5.0, 999.0])
    assert np.array_equal(got, got2)


def test_no_backfill():
    strategy = pd.date_range("2024-01-01", periods=3, freq="D")
    with pytest.raises(e.MeasurementError, match="missing preceding"):
        e.causal_align_rates(strategy, [pd.Timestamp("2024-01-02")], [5.0])


def test_duplicate_or_unsorted_dates_rejected():
    with pytest.raises(e.MeasurementError):
        e.causal_align_rates(
            [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-01")],
            [pd.Timestamp("2023-12-31")],
            [5.0],
        )
    with pytest.raises(e.MeasurementError):
        e.causal_align_rates(
            [pd.Timestamp("2024-01-01")],
            [pd.Timestamp("2023-12-31"), pd.Timestamp("2023-12-30")],
            [5.0, 4.0],
        )
