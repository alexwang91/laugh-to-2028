from __future__ import annotations

import unittest

from research.governance.no_drift import path_is_allowed


class NoDriftAllowlistTests(unittest.TestCase):
    def test_governance_paths_are_allowed(self):
        self.assertTrue(path_is_allowed("config/research_governance_v1.json"))
        self.assertTrue(path_is_allowed("research/governance/no_drift.py"))
        self.assertTrue(path_is_allowed("docs/PROGRAM_LEVEL_EPISTEMIC_GOVERNANCE_V1_FINAL_REPORT_2026-08-08.md"))
        self.assertTrue(path_is_allowed(".github/workflows/research-governance.yml"))
        self.assertTrue(path_is_allowed("./.github/workflows/research-governance.yml"))

    def test_strategy_and_historical_research_paths_are_blocked(self):
        self.assertFalse(path_is_allowed("config/product.json"))
        self.assertFalse(path_is_allowed("config/phase6_shadow_contract.json"))
        self.assertFalse(path_is_allowed("src/strategy.py"))
        self.assertFalse(path_is_allowed("research/leverage_0040/LEVERAGE-0040.json"))
        self.assertFalse(path_is_allowed("research/cycle_exit/p5_5_validation_contract.json"))

    def test_unrelated_docs_are_blocked(self):
        self.assertFalse(path_is_allowed("docs/MASTER_PLAN_2026-08-05.md"))
        self.assertFalse(path_is_allowed("docs/PHASE_0_8_DRIFT_AUDIT_2026-08-08.md"))


if __name__ == "__main__":
    unittest.main()
