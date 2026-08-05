import unittest

from run_carry_rf_0036r1 import corrected_0031_qualification, corrected_0033_qualification


class CarryRf0036R1Tests(unittest.TestCase):
    def test_0031_rf_failure_blocks_stack_even_when_old_other_gates_pass(self):
        published = {
            "qualification": {
                "net_economics": True,
                "funding_mechanism": True,
                "daily_correlation_below_0_50": True,
                "nonnegative_brrk_worst_decile_day_alpha": True,
                "qualified_for_stack_test": True,
            }
        }
        out = corrected_0031_qualification(published, False)
        self.assertFalse(out["net_economics"])
        self.assertFalse(out["qualified_for_stack_test"])
        self.assertTrue(out["funding_mechanism"])

    def test_0033_new_cash_gate_does_not_rescue_old_failed_gates(self):
        published = {
            "qualification": {
                "return_improvement": False,
                "sharpe_improvement": False,
                "drawdown_nonworsening": False,
                "calmar_improvement": False,
                "gross_discipline": True,
                "qualified_idle_capital_stack": False,
            }
        }
        out = corrected_0033_qualification(published, True)
        self.assertTrue(out["net_economics_vs_idle_cash"])
        self.assertFalse(out["qualified_idle_capital_stack_corrected"])


if __name__ == "__main__":
    unittest.main()
