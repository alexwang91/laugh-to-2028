from __future__ import annotations

import unittest

from research.brrk_beta_handoff_0047 import test_preregistration_contract as contract


class TestBrrkBetaHandoff0047PreregContract(unittest.TestCase):
    def test_design_and_central_registration(self):
        contract.test_design_boundary_exists_and_formal_prereg_matches_central_record_exactly()

    def test_dataset_registration(self):
        contract.test_dataset_declaration_matches_central_registry_exactly_and_is_exposed_development()

    def test_method_families_frozen(self):
        contract.test_frozen_method_families_are_present_without_candidate_tournament()

    def test_target_and_censoring(self):
        contract.test_hindsight_target_is_separate_and_censoring_is_not_negative()

    def test_episode_dependence(self):
        contract.test_transmission_and_uncertainty_preserve_episode_dependence()

    def test_oracle_firewall(self):
        contract.test_oracle_is_firewalled_and_not_a_gate()

    def test_no_runner_model_or_result(self):
        contract.test_preregistration_stage_has_no_runner_model_or_result_files()

    def test_no_portfolio_or_authority(self):
        contract.test_portfolio_translation_and_authority_remain_forbidden()


if __name__ == "__main__":
    unittest.main()
