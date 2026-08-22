from engine import (
    C1_REALISTIC,
    C2_STRESSED,
    candidate_pass,
    enforce_same_underlying,
    exposure_and_reserve_valid,
    nearest_eligible_dated_future,
    rebalance_required,
    target_pair_nav,
    terminal_classification,
)


def run() -> None:
    assert target_pair_nav(1.0) == (0.5, -0.5)
    enforce_same_underlying("BTC", "BTC")
    try:
        enforce_same_underlying("BTC", "ETH")
    except ValueError:
        pass
    else:
        raise AssertionError("cross-asset hedge must fail")
    assert rebalance_required(0.011)
    assert not rebalance_required(0.01)
    assert exposure_and_reserve_valid(1.0, 0.20)
    assert nearest_eligible_dated_future((("A", 90), ("B", 30), ("C", 10))) == "B"
    assert C2_STRESSED.one_way_cost(0.5, -0.5) == 2 * C1_REALISTIC.one_way_cost(0.5, -0.5)
    assert candidate_pass(
        eligible_days=365,
        c1_cagr=0.01,
        c2_cagr=0.01,
        c1_sharpe=0.51,
        c2_sharpe=0.26,
        c1_max_drawdown=-0.34,
        bootstrap_p05=0.001,
        dsr=0.95,
        cost_break_even_bps=20,
        neutrality_rate=0.01,
        exposure_ok=True,
        stresses_terminal_wealth_gt_one=True,
        concentration_ok=True,
        capacity_ok_or_not_required=True,
    )
    assert terminal_classification(execution_valid=False, decision_complete=True, any_candidate_passes=True) == "INVALID_EXECUTION"
    assert terminal_classification(execution_valid=True, decision_complete=False, any_candidate_passes=False) == "INCONCLUSIVE_INSUFFICIENT_SUPPORT"
    assert terminal_classification(execution_valid=True, decision_complete=True, any_candidate_passes=True) == "PASS"
    assert terminal_classification(execution_valid=True, decision_complete=True, any_candidate_passes=False) == "FAIL"


if __name__ == "__main__":
    run()
