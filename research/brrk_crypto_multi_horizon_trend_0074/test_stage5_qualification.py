import math

from engine import (
    breakout_vote,
    cap_portfolio,
    equal_vote,
    executable_interval_weight,
    funding_contribution,
    lagged_ann_vol,
    past_return_vote,
    risk_scale,
    target_weight,
    turnover_cost,
)


def test_flat_and_exact_vote_ties_fail_closed_to_flat():
    closes = [100.0] * 241
    assert past_return_vote(closes, 20) == 0
    assert breakout_vote(closes, 20) == 0
    assert equal_vote((1, -1, 0)) == 0


def test_breakout_boundary_excludes_current_close_from_prior_window():
    closes = [100.0] * 20 + [101.0]
    assert breakout_vote(closes, 20) == 1
    closes = [100.0] * 20 + [99.0]
    assert breakout_vote(closes, 20) == -1


def test_vol_floor_target_and_high_vol_deleveraging():
    assert math.isclose(risk_scale(0.0), 1.0)
    assert math.isclose(target_weight(1, 0.0), 1.0 / 3.0)
    assert math.isclose(risk_scale(0.40), 0.5)
    assert math.isclose(target_weight(-1, 0.40), -1.0 / 6.0)
    assert lagged_ann_vol([0.0] * 19) is None
    assert target_weight(1, None) == 0.0


def test_multi_asset_gross_cap_and_cost_regimes():
    capped = cap_portfolio((2.0 / 3.0, -2.0 / 3.0, 2.0 / 3.0))
    assert math.isclose(sum(abs(x) for x in capped), 1.0)
    assert turnover_cost(1.0, 0.0) == 0.0
    assert math.isclose(turnover_cost(1.0, 10.0), 0.001)
    assert math.isclose(turnover_cost(1.0, 30.0), 0.003)


def test_funding_sign_for_long_and_short():
    assert funding_contribution(1.0, 0.001) == -0.001
    assert funding_contribution(-1.0, 0.001) == 0.001
    assert funding_contribution(1.0, -0.001) == 0.001
    assert funding_contribution(-1.0, -0.001) == -0.001


def test_missing_or_nonpositive_inputs_fail_closed():
    assert past_return_vote([100.0] * 20, 20) == 0
    closes = [100.0] * 20 + [0.0]
    assert past_return_vote(closes, 20) == 0
    assert target_weight(1, float('nan')) == 0.0


def test_executable_weight_uses_only_returns_available_through_close_t():
    returns_through_t = [0.01, -0.01] * 10
    weight_for_t_to_t1 = executable_interval_weight(1, returns_through_t)
    assert weight_for_t_to_t1 > 0.0
    assert weight_for_t_to_t1 <= 1.0 / 3.0
