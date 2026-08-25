from __future__ import annotations

from datetime import date, timedelta
from io import BytesIO
import math
import unittest
import zipfile

from research.brrk_cross_sectional_factor_atlas_0086.engine import (
    CrossSectionalFactorAtlas0086Engine,
    FactorAtlasExecutionError,
    _factor_values,
    _holm_adjust,
    analyze_panel,
    normalize_controlled_sources,
    validate_source_keys,
)


def synthetic_panel(days: int = 600, assets: int = 12):
    start = date(2021, 1, 1)
    out = {}
    for a in range(assets):
        symbol = "BTCUSDT" if a == 0 else f"A{a:02d}USDT"
        price = 100.0 + a
        rows = []
        for i in range(days):
            if i:
                cycle = math.sin((i + a * 3) / 17.0) + 0.5 * math.sin((i * (a + 2)) / 29.0)
                price *= math.exp(0.0001 * (a - 5) + 0.004 * cycle)
            quote_volume = 1_000_000.0 * (assets - a) * (1.0 + 0.1 * math.sin((i + a) / 11.0))
            rows.append(
                {
                    "date": (start + timedelta(days=i)).isoformat(),
                    "close": price,
                    "quote_volume": quote_volume,
                }
            )
        out[symbol] = rows
    return out


def one_kline_zip(day: date, close: float = 100.0, quote_volume: float = 1_000_000.0) -> bytes:
    open_ms = int(day.strftime("%s")) * 1000
    csv_row = f"{open_ms},1,1,1,{close},1,{open_ms + 86399999},{quote_volume},1,1,1,0\n"
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("kline.csv", csv_row)
    return buffer.getvalue()


class FactorAtlas0086BuildQualification(unittest.TestCase):
    def test_frozen_factor_formulas(self) -> None:
        rows = []
        start = date(2025, 1, 1)
        for i in range(121):
            rows.append(
                {
                    "date": (start + timedelta(days=i)).isoformat(),
                    "close": math.exp(i / 100.0),
                    "quote_volume": math.exp(10.0 + i / 1000.0),
                }
            )
        values = _factor_values(rows, 120)
        self.assertAlmostEqual(values["MOM60_RAW"], 0.60, places=12)
        expected_liq = math.log((rows[105]["quote_volume"] + rows[106]["quote_volume"]) / 2.0)
        self.assertAlmostEqual(values["LIQ30_RAW"], expected_liq, places=12)
        self.assertGreaterEqual(values["RVOL20_RAW"], 0.0)

    def test_source_key_namespaces_cover_staging_and_github_artifact(self) -> None:
        stage = "stage/payloads/data__futures__um__monthly__klines__BTCUSDT__1d__BTCUSDT-1d-2026-01.zip"
        artifact = "payloads/data__futures__um__monthly__klines__BTCUSDT__1d__BTCUSDT-1d-2026-01.zip"
        validate_source_keys([stage])
        validate_source_keys([artifact])
        with self.assertRaisesRegex(FactorAtlasExecutionError, "DUPLICATE_LOGICAL_OBJECT"):
            validate_source_keys([stage, artifact])
        with self.assertRaisesRegex(FactorAtlasExecutionError, "UNKNOWN_SOURCE_KEY"):
            validate_source_keys(["unexpected.zip"])

    def test_post_marker_zip_adapter_reads_expected_columns(self) -> None:
        key = "payloads/data__futures__um__monthly__klines__BTCUSDT__1d__BTCUSDT-1d-2026-01.zip"
        panel = normalize_controlled_sources({key: one_kline_zip(date(2026, 1, 2), 123.0, 456.0)})
        self.assertEqual(panel["BTCUSDT"][0]["close"], 123.0)
        self.assertEqual(panel["BTCUSDT"][0]["quote_volume"], 456.0)

    def test_holm_step_down_is_monotone_and_exact_three_test_family(self) -> None:
        adjusted = _holm_adjust({"MOM60_RAW": 0.01, "RVOL20_RAW": 0.03, "LIQ30_RAW": 0.04})
        self.assertEqual(set(adjusted), {"MOM60_RAW", "RVOL20_RAW", "LIQ30_RAW"})
        self.assertAlmostEqual(adjusted["MOM60_RAW"], 0.03)
        self.assertAlmostEqual(adjusted["RVOL20_RAW"], 0.06)
        self.assertAlmostEqual(adjusted["LIQ30_RAW"], 0.06)

    def test_short_synthetic_history_is_valid_inconclusive_not_execution_error(self) -> None:
        result = analyze_panel(synthetic_panel(days=600))
        self.assertTrue(result["execution_valid"])
        self.assertEqual(result["classification"], "INCONCLUSIVE_INSUFFICIENT_SUPPORT")
        self.assertEqual(result["factor_candidates"], 3)
        self.assertEqual(
            result["btc_state_rule"],
            "BTC_UP iff BTCUSDT MOM60_RAW > 0 at decision close; otherwise BTC_NONUP",
        )

    def test_full_synthetic_lifecycle_produces_allowed_terminal_result(self) -> None:
        result = analyze_panel(synthetic_panel(days=1500))
        self.assertTrue(result["execution_valid"])
        self.assertIn(result["classification"], {"PASS_VALIDATED_FACTOR_ATLAS", "FAIL_NO_ROBUST_FACTOR_FAMILY"})
        self.assertEqual(result["factor_candidates"], 3)
        self.assertEqual(result["bootstrap"]["replicates"], 10_000)
        self.assertEqual(result["bootstrap"]["seed"], 860086)
        self.assertEqual(set(result["factors"]), {"MOM60_RAW", "RVOL20_RAW", "LIQ30_RAW"})
        for factor in result["factors"].values():
            self.assertEqual(set(factor["gates"]), {f"G{i}_{name}" for i, name in enumerate([
                "EXECUTION", "SUPPORT", "MULTIPLE_TESTING", "BOOTSTRAP", "SIGN_FRACTION",
                "CHRONOLOGY", "CALENDAR", "BTC_STATE", "LEAVE_ONE_YEAR_OUT", "ECONOMIC",
            ])})

    def test_engine_exposes_source_qualified_interface_and_propagates_failures(self) -> None:
        engine = CrossSectionalFactorAtlas0086Engine()
        engine.validate_source_keys([
            "payloads/data__futures__um__monthly__klines__BTCUSDT__1d__BTCUSDT-1d-2026-01.zip"
        ])
        with self.assertRaises(FactorAtlasExecutionError):
            engine.validate_source_keys(["bad"])


if __name__ == "__main__":
    unittest.main()
