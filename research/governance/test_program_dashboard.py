from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DASHBOARD = ROOT / "research" / "governance" / "dashboard" / "index.html"
README = ROOT / "research" / "governance" / "dashboard" / "README.md"


class ProgramDashboardContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.html = DASHBOARD.read_text(encoding="utf-8")
        self.readme = README.read_text(encoding="utf-8")

    def test_dashboard_reads_canonical_existing_history(self) -> None:
        for path in (
            "research/results/pit_disp_0015/daily_equity.csv",
            "research/results/pit_disp_0015/daily_weights.csv",
            "research/results/funding_pnl_0003/full_window_daily_equity.csv",
        ):
            self.assertIn(path, self.html)
            self.assertIn(path, self.readme)

    def test_dashboard_reads_governed_registry_without_authority_change(self) -> None:
        self.assertIn("config/research_registry.json", self.html)
        self.assertIn("config/decision_registry.json", self.html)
        self.assertIn("production_authorized=false", self.html)
        self.assertIn("dashboard_record_authoritative=false", self.html)

    def test_phase6_candidate_requires_success_evidence_and_receipt(self) -> None:
        self.assertIn("run.conclusion==='success'&&ev&&receipt", self.html)
        self.assertIn("phase6-evidence-", self.html)
        self.assertIn("phase6-receipt-", self.html)
        self.assertIn("dashboard itself never creates evidence credit", self.html)
        self.assertIn("scheduled_decision_credit_created=false", self.html)

    def test_backtest_shadow_and_real_pnl_are_explicitly_non_equivalent(self) -> None:
        for text in (
            "historical backtest NAV",
            "Phase-6 hypothetical shadow PnL",
            "future real-account PnL",
        ):
            self.assertIn(text, self.readme)
        self.assertIn("!=", self.readme)

    def test_xrp_is_feature_only_and_not_target_holding(self) -> None:
        self.assertIn("const TARGET_ASSETS=['BTC','ETH','SOL','BNB']", self.html)
        self.assertNotIn("TARGET_ASSETS=['BTC','ETH','SOL','BNB','XRP']", self.html)
        self.assertIn("XRP remains **feature-only**", self.readme)

    def test_v3_exposes_range_statistics_without_renaming_daily_hit_rate(self) -> None:
        for text in (
            "Cumulative return",
            "Positive-return-day ratio",
            "Daily payoff ratio",
            "Max drawdown",
            "Target-change days",
            "Holding-cycle win rate",
        ):
            self.assertIn(text, self.html)
        self.assertIn("Positive-return-day ratio` is not labelled as holding-cycle win rate", self.readme)
        self.assertIn("metric('Actual rebalance count','UNAVAILABLE')", self.html)
        self.assertIn("metric('Holding-cycle win rate','UNAVAILABLE')", self.html)

    def test_v3_freezes_p33_rule_but_does_not_infer_historical_execution(self) -> None:
        self.assertIn("const P33_REBALANCE_BAND=0.05", self.html)
        self.assertIn("L1_ABSOLUTE_WEIGHT_GAP", self.html)
        self.assertIn("REBALANCE_WHEN_L1_GAP_GTE_BAND", self.html)
        self.assertIn("Historical P3.3 action: UNAVAILABLE", self.html)
        self.assertIn("historical_p3_3_execution_state_available=false", self.html)
        self.assertIn("execution_causality_asserted=false", self.html)
        self.assertIn("current_position_weights", self.readme)
        self.assertIn("l1_target_gap", self.readme)

    def test_v3_separates_target_session_decision_and_return_date(self) -> None:
        self.assertIn("Target session", self.html)
        self.assertIn("Decision timestamp", self.html)
        self.assertIn("Data cutoff", self.html)
        self.assertIn("Target holding return", self.html)
        self.assertIn("Selected NAV return", self.html)
        self.assertIn("uses completed daily data through D-1", self.readme)
        self.assertIn("does not introduce look-ahead", self.readme)

    def test_v3_signal_rules_are_explicit_but_daily_snapshot_is_not_invented(self) -> None:
        for text in (
            "btc_trend < 0",
            "ETH eligibility",
            "SOL eligibility",
            "BNB eligibility",
            "RISK_OFF / BTC_LEAD / MAJOR_ROTATION / ALT_EXPANSION",
            "Selected historical daily signal values: UNAVAILABLE",
        ):
            self.assertIn(text, self.html)
        self.assertIn("historical_signal_snapshot_available=false", self.html)
        self.assertIn("never reverse-engineers a 2023 signal/regime", self.readme)

    def test_v3_target_actions_remain_mechanical_only(self) -> None:
        self.assertIn("const REBALANCE_EPS=1e-9", self.html)
        for action in ("ENTER", "EXIT", "INCREASE", "DECREASE", "HOLD"):
            self.assertIn(action, self.html)
            self.assertIn(action, self.readme)
        self.assertIn("目标权重变化（由 canonical weights 派生）", self.html)
        self.assertIn("target_change_mechanics_authoritative_from_canonical_weights=true", self.html)

    def test_v3_public_deploy_has_unique_marker(self) -> None:
        self.assertIn('content="v3-daily-audit"', self.html)
        self.assertIn("BRRK Program Timeline · V3 Daily Audit", self.html)
        self.assertIn("https://laugh-to-2028.vercel.app/", self.readme)


if __name__ == "__main__":
    unittest.main()
