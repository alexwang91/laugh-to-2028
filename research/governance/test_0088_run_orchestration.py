from __future__ import annotations

from pathlib import Path
import unittest

from research.brrk_factor_ls_0088.engine import FactorLS0088Engine
from research.brrk_factor_ls_0088.run_controlled_once import (
    FUNDING_FAMILY,
    KLINE_FAMILY,
    RUN_BRANCH,
    _runtime_key,
)
from research.governance.no_drift import ALLOWED_EXACT_PATHS


class FactorLS0088RunOrchestrationTest(unittest.TestCase):
    def test_runtime_key_maps_both_frozen_source_families(self) -> None:
        staged_kline = "stage/payloads/data__futures__um__monthly__klines__BTCUSDT__1d__BTCUSDT-1d-2026-07.zip"
        staged_funding = "stage/payloads/data__futures__um__monthly__fundingRate__BTCUSDT__BTCUSDT-fundingRate-2026-07.zip"
        runtime_kline = staged_kline[len("stage/") :]
        runtime_funding = staged_funding[len("stage/") :]
        self.assertEqual(_runtime_key(staged_kline), runtime_kline)
        self.assertEqual(_runtime_key(staged_funding), runtime_funding)
        FactorLS0088Engine().validate_source_keys([runtime_kline, runtime_funding])

    def test_runtime_key_rejects_unknown_namespace(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "UNKNOWN_STAGED_SOURCE_KEY"):
            _runtime_key("other/BTCUSDT-1d-2026-07.zip")

    def test_source_family_constants_are_exact(self) -> None:
        self.assertEqual(KLINE_FAMILY, "USD_M_MONTHLY_1D_PERPETUAL_KLINE")
        self.assertEqual(FUNDING_FAMILY, "USD_M_MONTHLY_FUNDING_RATE")

    def test_unique_workflow_is_exactly_trigger_scoped(self) -> None:
        root = Path(__file__).resolve().parents[2]
        path = root / ".github" / "workflows" / "0088-unique-controlled-run.yml"
        text = path.read_text(encoding="utf-8")
        self.assertIn(f'- "{RUN_BRANCH}"', text)
        self.assertIn('- "research/brrk_factor_ls_0088/RUN_TRIGGER.json"', text)
        self.assertNotIn("workflow_dispatch:", text)

    def test_no_drift_allowlist_is_exact_not_broad(self) -> None:
        self.assertIn(".github/workflows/0088-unique-controlled-run.yml", ALLOWED_EXACT_PATHS)
        self.assertNotIn(".github/workflows/", ALLOWED_EXACT_PATHS)


if __name__ == "__main__":
    unittest.main()
