from __future__ import annotations

import unittest

from research.brrk_cross_sectional_factor_atlas_0086.engine import CrossSectionalFactorAtlas0086Engine
from research.brrk_cross_sectional_factor_atlas_0086.run_controlled_once import _runtime_key


class FactorAtlas0086RunOrchestrationTest(unittest.TestCase):
    def test_runtime_key_maps_frozen_stage_namespace_to_artifact_namespace(self) -> None:
        staged = "stage/payloads/data__futures__um__monthly__klines__BTCUSDT__1d__BTCUSDT-1d-2026-07.zip"
        runtime = "payloads/data__futures__um__monthly__klines__BTCUSDT__1d__BTCUSDT-1d-2026-07.zip"
        self.assertEqual(_runtime_key(staged), runtime)
        CrossSectionalFactorAtlas0086Engine().validate_source_keys([runtime])

    def test_runtime_key_preserves_already_runtime_namespace(self) -> None:
        runtime = "payloads/data__futures__um__monthly__klines__BTCUSDT__1d__BTCUSDT-1d-2026-07.zip"
        self.assertEqual(_runtime_key(runtime), runtime)

    def test_runtime_key_rejects_unknown_namespace(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "UNKNOWN_STAGED_SOURCE_KEY"):
            _runtime_key("other/BTCUSDT-1d-2026-07.zip")

    def test_engine_rejects_duplicate_logical_object_across_namespaces(self) -> None:
        runtime = "payloads/data__futures__um__monthly__klines__BTCUSDT__1d__BTCUSDT-1d-2026-07.zip"
        staged = "stage/" + runtime
        with self.assertRaisesRegex(Exception, "DUPLICATE_LOGICAL_OBJECT"):
            CrossSectionalFactorAtlas0086Engine().validate_source_keys([runtime, staged])


if __name__ == "__main__":
    unittest.main()
