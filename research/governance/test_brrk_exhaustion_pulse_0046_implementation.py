from __future__ import annotations

"""Standing-CI bridge for the pre-result BRRK-EXHAUSTION-PULSE-0046 tests.

The repository's immutable governance workflow discovers unittest tests only
under research/governance. This bridge executes the formal research module's
synthetic math/firewall/lifecycle tests without changing workflow or policy.
"""

import unittest

from research.brrk_exhaustion_pulse_0046 import test_detector_math as math_tests
from research.brrk_exhaustion_pulse_0046 import test_firewall_contract as firewall_tests
from research.brrk_exhaustion_pulse_0046 import test_preregistration_contract as prereg_tests


class TestBrrkExhaustionPulse0046Implementation(unittest.TestCase):
    def test_detector_math_reference_suite(self) -> None:
        math_tests.test_prefix_rolling_ols_matches_explicit_lstsq()
        math_tests.test_subset_product_identity_matches_explicit_15_subset_enumeration()
        math_tests.test_flat_linear_path_has_zero_score_and_smallest_tie_age()
        math_tests.test_positive_acceleration_scores_but_improvement_is_one_sided()
        math_tests.test_first_valid_session_cannot_emit_pulse()
        math_tests.test_empirical_p90_is_nearest_rank()

    def test_firewall_and_interface_suite(self) -> None:
        firewall_tests.test_calibration_module_has_no_raw_market_nav_or_taxonomy_import_path()
        firewall_tests.test_predictor_materializer_does_not_call_taxonomy_functions()
        firewall_tests.test_s1_s4_construction_exactly_matches_0044_constants()
        firewall_tests.test_run_once_validates_lock_before_dynamic_evaluation_import()
        firewall_tests.test_frozen_detector_and_calibration_constants()
        firewall_tests.test_var1_fit_and_bootstrap_are_deterministic()
        firewall_tests.test_stopping_time_clock_and_censor_are_frozen()
        firewall_tests.test_run_interface_is_pre_result_zero_authority()
        firewall_tests.test_pre_result_branch_contains_no_generated_predictor_lock_or_result_evidence()

    def test_preregistration_lifecycle_monotonicity_suite(self) -> None:
        prereg_tests.test_formal_preregistration_matches_central_record_exactly()
        prereg_tests.test_dataset_declaration_matches_central_exposure_registry_exactly()
        prereg_tests.test_frozen_detector_parameters_and_firewall_are_present()
        prereg_tests.test_parent_evidence_remains_immutable_and_0045_does_not_create_dynamic_gross()
        prereg_tests.test_lifecycle_only_allows_pre_result_implementation_not_generated_evidence()
        prereg_tests.test_zero_authority_and_no_portfolio_translation()


if __name__ == "__main__":
    unittest.main()
