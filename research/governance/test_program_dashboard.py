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

    def test_backtest_shadow_and_real_pnl_are_explicitly_non_equivalent(self) -> None:
        self.assertIn("historical backtest NAV", self.readme)
        self.assertIn("Phase-6 hypothetical shadow PnL", self.readme)
        self.assertIn("future real-account PnL", self.readme)
        self.assertIn("!=", self.readme)

    def test_xrp_is_not_plotted_as_target_holding(self) -> None:
        self.assertIn("const assets=['BTC','ETH','SOL','BNB']", self.html)
        self.assertIn("XRP remains feature-only", self.readme)


if __name__ == "__main__":
    unittest.main()
