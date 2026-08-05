import unittest

from run_carry_pm_0035 import compare_snapshots, summarize_borrow_state, summarize_spot_state


class CarryPm0035Tests(unittest.TestCase):
    def test_spot_state_portfolio_fields(self):
        state = {
            "portfolioMarginEnabled": True,
            "portfolioMarginRatio": "0.12",
            "tokenToAvailableAfterMaintenance": [[0, "480.0"], [197, "0.004"]],
            "tokenToPortfolioBorrowRatio": [[0, "0.03"]],
            "balances": [
                {"coin": "USDC", "token": 0, "total": "100.0", "hold": "0", "entryNtl": "0"},
                {"coin": "UBTC", "token": 197, "total": "0.0078", "hold": "0", "entryNtl": "500", "ltv": "0.5"},
            ],
        }
        out = summarize_spot_state(state)
        self.assertTrue(out["portfolioMarginEnabled"])
        self.assertAlmostEqual(out["portfolioMarginRatio"], 0.12)
        self.assertAlmostEqual(out["ubtc"]["total"], 0.0078)
        self.assertAlmostEqual(out["tokenToAvailableAfterMaintenance"]["0"], 480.0)

    def test_borrow_state_sums_values(self):
        state = {
            "health": "healthy",
            "healthFactor": "10.0",
            "tokenToState": [
                [0, {"borrow": {"basis": "0", "value": "3.5"}, "supply": {"basis": "0", "value": "1.5"}}],
                [197, {"borrow": {"basis": "0", "value": "0"}, "supply": {"basis": "0", "value": "4"}}],
            ],
        }
        out = summarize_borrow_state(state)
        self.assertAlmostEqual(out["total_borrow_value"], 3.5)
        self.assertAlmostEqual(out["total_supply_value"], 5.5)

    def test_compare_passes_clean_mechanism(self):
        def snap(label, ubtc, short_ntl, short_szi, avail, pm_ratio=0.0):
            return {
                "label": label,
                "account_fingerprint": "abc123",
                "user_abstraction": "portfolioMargin",
                "spot": {
                    "portfolioMarginEnabled": True,
                    "portfolioMarginRatio": pm_ratio,
                    "tokenToAvailableAfterMaintenance": {"0": avail},
                    "ubtc": {"total": ubtc},
                },
                "borrow_lend": {"total_borrow_value": 0.0, "health": "healthy", "healthFactor": None},
                "perp": {"btc_position": {"szi": short_szi}, "other_positions": []},
                "derived": {
                    "has_ubtc_spot": ubtc > 0,
                    "has_btc_short": short_szi < 0,
                    "has_other_perp_positions": False,
                    "ubtc_spot_notional": ubtc * 64000,
                    "btc_short_notional": short_ntl,
                    "match_mismatch_fraction": (
                        abs(ubtc * 64000 - short_ntl) / max(ubtc * 64000, short_ntl)
                        if ubtc and short_ntl
                        else None
                    ),
                },
            }

        cash = snap("cash", 0, 0, 0, 500)
        spot = snap("spot", 0.0075, 0, 0, 470)
        matched = snap("matched", 0.0075, 478, -0.00747, 450, 0.10)
        closed = snap("closed", 0, 0, 0, 497)
        out = compare_snapshots(cash, spot, matched, closed)
        self.assertEqual(out["status"], "PASS_PM_ACCOUNT_BEHAVIOR")
        self.assertLess(out["measurements"]["incremental_maintenance_fraction_of_short_notional"], 0.25)

    def test_compare_fails_size_mismatch(self):
        def base(spot_ntl, short_ntl, mismatch, has_spot, has_short):
            return {
                "account_fingerprint": "same",
                "user_abstraction": "portfolioMargin",
                "spot": {
                    "portfolioMarginEnabled": True,
                    "portfolioMarginRatio": 0.1,
                    "tokenToAvailableAfterMaintenance": {"0": 100.0},
                    "ubtc": {"total": 0.0 if not has_spot else 0.005},
                },
                "borrow_lend": {"total_borrow_value": 0.0},
                "perp": {"btc_position": {"szi": -0.002 if has_short else 0.0}, "other_positions": []},
                "derived": {
                    "has_ubtc_spot": has_spot,
                    "has_btc_short": has_short,
                    "has_other_perp_positions": False,
                    "ubtc_spot_notional": spot_ntl,
                    "btc_short_notional": short_ntl,
                    "match_mismatch_fraction": mismatch,
                },
            }

        cash = base(0, 0, None, False, False)
        spot = base(300, 0, None, True, False)
        matched = base(300, 150, 0.5, True, True)
        closed = base(0, 0, None, False, False)
        out = compare_snapshots(cash, spot, matched, closed)
        self.assertEqual(out["status"], "FAIL_OR_INCONCLUSIVE_PM_ACCOUNT_BEHAVIOR")
        self.assertFalse(out["checks"]["matched_base_notional_within_2pct"])


if __name__ == "__main__":
    unittest.main()
