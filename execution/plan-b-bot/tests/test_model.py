import math

from beta_bot.model import apply_funding_filter, build_signal, compute_raw_beta, compute_trend_score


def synthetic_closes(daily_return: float, count: int = 300) -> list[float]:
    return [100.0 * ((1.0 + daily_return) ** i) for i in range(count)]


def test_positive_trend_has_beta_at_least_one():
    closes = synthetic_closes(0.002)
    trend, vol = compute_trend_score(closes)
    beta = compute_raw_beta(trend, vol)
    assert trend > 0
    assert 1.0 <= beta <= 1.30


def test_negative_trend_stays_inside_defensive_bounds():
    closes = synthetic_closes(-0.002)
    trend, vol = compute_trend_score(closes)
    beta = compute_raw_beta(trend, vol)
    assert trend < 0
    assert 0.18 <= beta <= 0.65


def test_high_funding_disables_extra_beta():
    beta, reason = apply_funding_filter(1.30, 0.30)
    assert beta == 1.0
    assert reason == "disable_extra_beta"


def test_build_signal_is_finite():
    closes = [100 + 5 * math.sin(i / 8) + i * 0.05 for i in range(300)]
    signal = build_signal(closes, funding_apr=0.05)
    assert math.isfinite(signal.target_beta)
    assert 0.18 <= signal.target_beta <= 1.5
