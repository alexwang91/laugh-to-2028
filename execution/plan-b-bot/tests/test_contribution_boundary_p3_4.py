from beta_bot.contribution_handling import observe_equity_change


def test_equity_change_at_already_accepted_boundary_rolls_to_next_day():
    observation = observe_equity_change(
        baseline_decision_timestamp="2026-08-08T00:00:00Z",
        baseline_equity_usd=2_000.0,
        observed_at="2026-08-08T00:00:00Z",
        observed_equity_usd=2_100.0,
    )
    assert observation.observed_at_daily_boundary
    assert observation.scheduled_daily_decision_timestamp == "2026-08-09T00:00:00Z"
    assert observation.contribution_candidate_pending
    assert not observation.intraday_target_recalculation_allowed
    assert not observation.intraday_risk_increase_allowed
