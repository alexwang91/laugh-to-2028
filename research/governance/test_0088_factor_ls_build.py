import unittest

from research.brrk_factor_ls_0088.engine import analyze_weekly_records


def _target(offset=0):
    # 21 names, 7 long / 7 short / 7 zero, gross 2/net 0, max 1/7 < .15.
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


class Test0088FactorLSBuild(unittest.TestCase):
    def test_adequate_synthetic_support_passes_all_frozen_gates(self):
        records = [_record(i) for i in range(156)]
        result = analyze_weekly_records(records)
        self.assertEqual(result["classification"], "PASS_VALIDATED_FACTOR_LS")
        self.assertTrue(all(result["gates"].values()))
        self.assertEqual(result["observations"], 156)

    def test_unsupported_week_removes_preceding_and_restarts_from_zero(self):
        records = [_record(i) for i in range(110)]
        records[50]["support"] = False
        result = analyze_weekly_records(records)
        self.assertEqual(result["observations"], 108)

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
        result = analyze_weekly_records(records)
        self.assertEqual(result["observations"], 108)

    def test_consecutive_unsupported_weeks_restart_deterministically(self):
        records = [_record(i) for i in range(112)]
        records[50]["support"] = False
        records[51]["support"] = False
        result = analyze_weekly_records(records)
        self.assertEqual(result["observations"], 109)

    def test_insufficient_support_is_inconclusive_not_invalid(self):
        result = analyze_weekly_records([_record(i) for i in range(50)])
        self.assertEqual(result["classification"], "INCONCLUSIVE_INSUFFICIENT_SUPPORT")
        self.assertTrue(result["gates"]["G0_EXECUTION"])
        self.assertFalse(result["gates"]["G1_SUPPORT"])


if __name__ == "__main__":
    unittest.main()
