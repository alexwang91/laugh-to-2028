import math

from engine import (
    breakout_vote,
    candidate_signals,
    cap_portfolio,
    funding_contribution,
    lagged_ann_vol,
    past_return_vote,
    sma_vote,
    target_weight,
    turnover,
    turnover_cost,
)


def test_monotone_up_series_votes_long():
    closes = [100.0 + i for i in range(300)]
    assert past_return_vote(closes, 20) == 1
    assert sma_vote(closes, 10, 40) == 1
    assert breakout_vote(closes, 20) == 1
    sig = candidate_signals(closes)
    assert (sig.past_return, sig.moving_average, sig.breakout) == (1, 1, 1)


def test_monotone_down_series_votes_short():
    closes = [500.0 - i for i in range(300)]
    assert past_return_vote(closes, 60) == -1
    assert sma_vote(closes, 20, 80) == -1
    assert breakout_vote(closes, 60) == -1


def test_breakout_excludes_current_observation():
    closes = [100.0] * 20 + [101.0]
    assert breakout_vote(closes, 20) == 1


def test_risk_target_and_caps():
    returns = [0.01, -0.01] * 10
    vol = lagged_ann_vol(returns)
    assert vol is not None and vol > 0
    w = target_weight(1, vol)
    assert 0 < w <= 1 / 3
    capped = cap_portfolio((0.5, -0.5, 0.5))
    assert math.isclose(sum(abs(x) for x in capped), 1.0)


def test_turnover_cost_and_funding_sign():
    assert turnover((0.0, 0.0), (1 / 3, -1 / 3)) == 2 / 3
    assert math.isclose(turnover_cost(1.0, 10), 0.001)
    assert funding_contribution(1.0, 0.001) == -0.001
    assert funding_contribution(-1.0, 0.001) == 0.001
