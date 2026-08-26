import unittest
from datetime import date, timedelta

from research.brrk_factor_ls_0088.construction import construct_target, funding_pnl, trailing_beta
from research.brrk_factor_ls_0088.engine import analyze_weekly_records


def _target(offset=0):
    names = [f"S{i:02d}USDT" for i in range(21)]
    longs = names[offset % 7 : offset % 7 + 7]
    if len(longs) < 7:
        longs += names[: 7 - len(longs)]
    remaining = [n for n in names if n not in longs]
    shorts = remaining[:7]
    out = {n: 0.0 for n in names}
    for n in longs:
        out[n] = 1.0 / 7.0
    for n in shorts:
        out[n] = -1.0 / 7.0
    return out


def _record(i, support=True, ret=0.02):
    target = _target(i % 7)
    return {
        "date": f"{2022 + i // 52:04d}-{(i % 12)+1:02d}-{(i % 27)+1:02d}",
        "support": support,
        "target": target,
        "asset_returns": {name: (ret if w > 0 else -ret if w < 0 else 0.0) for name, w in target.items()},
        "funding_pnl": 0.0,
        "portfolio_beta": 0.05 if i % 2 else -0.05,
        "btc_state": "BTC_UP" if i % 2 else "BTC_NONUP",
        "median_quote_volume": {name: 100_000_000.0 for name in target},
    }


def _panel():
    start = date(2024, 1, 1)
    panel = {}
    for s in range(31):
        symbol = f"S{s:02d}USDT"
        rows = []
        for i in range(130):
            rows.append({
                "date": (start + timedelta(days=i)).isoformat(),
                "close": 100.0 * (1.0 + 0.0002 * (s + 1)) ** i,
                "quote_volume": float((s + 1) * 1_000_000),
            })
        panel[symbol] = rows
    return panel


class Test0088FactorLSBuild(unittest.TestCase):
    def test_adequate_synthetic_support_passes_all_frozen_gates(self):
        result = analyze_weekly_records([_record(i) for i in range(156)])
        self.assertEqual(result["classification"], "PASS_VALIDATED_FACTOR_LS")
        self.assertTrue(all(result["gates"].values()))
        self.assertEqual(result["observations"], 156)

    def test_unsupported_week_removes_preceding_and_restarts_from_zero(self):
        records = [_record(i) for i in range(110)]
        records[50]["support"] = False
        self.assertEqual(analyze_weekly_records(records)["observations"], 108)

    def test_support_admission_is_return_blind(self):
        left = [_record(i) for i in range(110)]
        right = [_record(i) for i in range(110)]
        left[50]["support"] = False
        right[50]["support"] = False
        left[49]["asset_returns"] = {name: -0.90 for name in left[49]["target"]}
        right[49]["asset_returns"] = {name: 0.90 for name in right[49]["target"]}
        self.assertEqual(analyze_weekly_records(left)["observations"], 108)
        self.assertEqual(analyze_weekly_records(right)["observations"], 108)

    def test_missing_capacity_denominator_fails_closed_as_unsupported_transition(self):
        records = [_record(i) for i in range(110)]
        records[50]["median_quote_volume"] = {}
        self.assertEqual(analyze_weekly_records(records)["observations"], 108)

    def test_consecutive_unsupported_weeks_restart_deterministically(self):
        records = [_record(i) for i in range(112)]
        records[50]["support"] = False
        records[51]["support"] = False
        self.assertEqual(analyze_weekly_records(records)["observations"], 109)

    def test_insufficient_support_is_inconclusive_not_invalid(self):
        result = analyze_weekly_records([_record(i) for i in range(50)])
        self.assertEqual(result["classification"], "INCONCLUSIVE_INSUFFICIENT_SUPPORT")
        self.assertTrue(result["gates"]["G0_EXECUTION"])
        self.assertFalse(result["gates"]["G1_SUPPORT"])

    def test_pit_top30_composite_and_terciles_are_deterministic(self):
        panel = _panel()
        result = construct_target(panel, "2024-05-04")
        self.assertEqual(len(result["symbols"]), 30)
        self.assertNotIn("S00USDT", result["symbols"])
        self.assertEqual(len(result["top"]), 10)
        self.assertEqual(len(result["bottom"]), 10)
        self.assertAlmostEqual(sum(abs(w) for w in result["target"].values()), 2.0)
        self.assertAlmostEqual(sum(result["target"].values()), 0.0)

    def test_trailing_beta_uses_exact_60_paired_simple_returns(self):
        start = date(2024, 1, 1)
        btc, asset = [], []
        for i in range(70):
            day = (start + timedelta(days=i)).isoformat()
            btc_close = 100.0 * (1.0 + 0.001 * i + 0.00002 * i * i)
            asset_close = 50.0 * (btc_close / 100.0) ** 1.5
            btc.append({"date": day, "close": btc_close})
            asset.append({"date": day, "close": asset_close})
        beta = trailing_beta(asset, btc, (start + timedelta(days=69)).isoformat())
        self.assertTrue(beta > 1.0)
        self.assertTrue(beta < 2.0)

    def test_funding_window_is_strict_after_entry_and_inclusive_at_exit(self):
        target = {"AUSDT": 1.0, "BUSDT": -1.0}
        events = {
            "AUSDT": [
                {"timestamp": "2024-01-01T23:59:59Z", "rate": 0.5},
                {"timestamp": "2024-01-02T08:00:00Z", "rate": 0.01},
                {"timestamp": "2024-01-06T23:59:59Z", "rate": 0.02},
            ],
            "BUSDT": [{"timestamp": "2024-01-03T08:00:00Z", "rate": 0.03}],
        }
        self.assertAlmostEqual(funding_pnl(target, events, "2024-01-01", "2024-01-06"), 0.0)


if __name__ == "__main__":
    unittest.main()
