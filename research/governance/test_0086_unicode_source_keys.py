from __future__ import annotations

import unittest

from research.brrk_cross_sectional_factor_atlas_0086.engine import validate_source_keys


class FactorAtlas0086UnicodeSourceKeyTest(unittest.TestCase):
    def test_frozen_unicode_symbol_filename_is_metadata_valid(self) -> None:
        validate_source_keys([
            "payloads/data__futures__um__monthly__klines__BTCUSDT__1d__BTCUSDT-1d-2026-01.zip",
            "payloads/data__futures__um__monthly__klines__币安人生USDT__1d__币安人生USDT-1d-2026-01.zip",
        ])


if __name__ == "__main__":
    unittest.main()
