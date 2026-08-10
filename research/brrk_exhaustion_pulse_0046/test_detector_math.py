from __future__ import annotations

import math

import numpy as np

from research.brrk_exhaustion_pulse_0046 import detector


def _explicit_ols(window: np.ndarray) -> tuple[float, float, float]:
    q = np.arange(1.0, 65.0)
    design = np.column_stack([np.ones(64), q])
    beta, _, _, _ = np.linalg.lstsq(design, window, rcond=None)
    resid = window - design @ beta
    sigma = math.sqrt(max(float(np.square(resid).sum()) / 62.0, 1e-8))
    return float(beta[0]), float(beta[1]), sigma


def test_prefix_rolling_ols_matches_explicit_lstsq() -> None:
    rng = np.random.default_rng(460046)
    x = rng.normal(size=(2, 120, 4))
    px, px2, pix = detector._prefix_moments(x)
    a, b, s = detector._rolling_ols_from_prefix(px, px2, pix, x.shape[1])
    for batch in (0, 1):
        for end in (63, 79, 119):
            for axis in range(4):
                ea, eb, es = _explicit_ols(x[batch, end - 63 : end + 1, axis])
                idx = end - 63
                assert np.isclose(a[batch, idx, axis], ea, atol=1e-11, rtol=1e-11)
                assert np.isclose(b[batch, idx, axis], eb, atol=1e-12, rtol=1e-11)
                assert np.isclose(s[batch, idx, axis], es, atol=1e-11, rtol=1e-10)


def test_subset_product_identity_matches_explicit_15_subset_enumeration() -> None:
    rng = np.random.default_rng(460047)
    ell = np.abs(rng.normal(size=(100, 4))) * 3.0
    fast = detector.subset_mixture_logscore(ell)
    explicit = detector.subset_mixture_logscore_explicit(ell)
    assert np.allclose(fast, explicit, atol=1e-12, rtol=1e-12)


def test_flat_linear_path_has_zero_score_and_smallest_tie_age() -> None:
    t = np.arange(160, dtype=np.float64)
    x = np.column_stack([0.01 * t, -0.02 * t + 3.0, 0.005 * t - 1.0, np.full_like(t, 2.0)])
    out = detector.compute_detector(x, details=True)
    finite = np.isfinite(out.score)
    assert finite.any()
    assert float(np.nanmax(np.abs(out.score))) < 1e-6
    # At sessions where all ages are available, equal zero scores retain tau=3.
    assert np.all(out.selected_age[np.flatnonzero(finite)[-20:]] == 3)


def test_positive_acceleration_scores_but_improvement_is_one_sided() -> None:
    base = np.zeros((140, 4), dtype=np.float64)
    up = base.copy()
    down = base.copy()
    for r in range(1, 21):
        up[90 + r, 0] = 0.08 * r
        down[90 + r, 0] = -0.08 * r
    up_score = detector.compute_detector(up, details=False)
    down_score = detector.compute_detector(down, details=False)
    assert float(up_score[110]) > 1.0
    assert float(down_score[110]) <= 1e-10


def test_first_valid_session_cannot_emit_pulse() -> None:
    score = np.array([np.nan, np.nan, 5.0, 6.0, 0.0, 7.0])
    eligible, alarm, pulse = detector.raw_alarm_and_pulse(score, 4.0)
    assert eligible.tolist() == [False, False, True, True, True, True]
    assert alarm.tolist() == [False, False, True, True, False, True]
    assert pulse.tolist() == [False, False, False, False, False, True]


def test_empirical_p90_is_nearest_rank() -> None:
    assert detector.empirical_nearest_rank([1, 2, 3, 4, 20], 0.90) == 20.0
    assert detector.empirical_nearest_rank([1] * 9 + [14], 0.90) == 1.0
