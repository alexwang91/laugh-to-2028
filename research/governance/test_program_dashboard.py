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

    def test_dashboard_reads_governed_strategy_and_decision_registries(self) -> None:
        self.assertIn("config/research_registry.json", self.html)
        self.assertIn("config/decision_registry.json", self.html)
        self.assertIn("production_authorized", self.html)

    def test_phase6_candidate_requires_success_evidence_and_receipt(self) -> None:
        self.assertIn("run.conclusion==='success'&&ev&&receipt", self.html)
        self.assertIn("phase6-evidence-", self.html)
        self.assertIn("phase6-receipt-", self.html)
        self.assertIn("dashboard itself never creates evidence credit", self.readme)
        self.assertIn("scheduled_decision_credit_created=false", self.html)

    def test_backtest_shadow_and_real_pnl_are_explicitly_non_equivalent(self) -> None:
        self.assertIn("historical backtest NAV", self.readme)
        self.assertIn("Phase-6 hypothetical shadow PnL", self.readme)
        self.assertIn("future real-account PnL", self.readme)
        self.assertIn("!=", self.readme)

    def test_xrp_is_feature_only_and_not_target_holding(self) -> None:
        self.assertIn("const TARGET_ASSETS=['BTC','ETH','SOL','BNB']", self.html)
        self.assertNotIn("TARGET_ASSETS=['BTC','ETH','SOL','BNB','XRP']", self.html)
        self.assertIn("XRP remains **feature-only**", self.readme)

    def test_v2_has_explicit_daily_target_change_contract(self) -> None:
        self.assertIn("const REBALANCE_EPS=1e-9", self.html)
        for action in ("ENTER", "EXIT", "INCREASE", "DECREASE", "HOLD"):
            self.assertIn(action, self.html)
            self.assertIn(action, self.readme)
        self.assertIn("目标权重变化（由 canonical weights 派生）", self.html)
        self.assertIn("target_change_mechanics_authoritative_from_canonical_weights=true", self.html)
        self.assertIn("execution_causality_asserted=false", self.html)
        self.assertIn("dashboard_record_authoritative=false", self.html)

    def test_v2_daily_metrics_are_derived_from_existing_series(self) -> None:
        self.assertIn("r.v/clean[i-1].v-1", self.html)
        self.assertIn("r.v/peak-1", self.html)
        self.assertIn("point.v/full.clean[0].v-1", self.html)
        self.assertIn("Math.abs(x.curr)", self.html)
        self.assertIn("Math.abs(x.delta)", self.html)
        self.assertIn("dateSlider", self.html)
        self.assertIn("plotly_click", self.html)

    def test_v2_refuses_to_invent_browser_unavailable_phase6_detail(self) -> None:
        self.assertIn("artifact detail not browser-indexed", self.html)
        self.assertIn("does **not** fabricate detailed forward values", self.readme)
        self.assertIn("execution_causality_asserted=false", self.readme)


if __name__ == "__main__":
    unittest.main()
