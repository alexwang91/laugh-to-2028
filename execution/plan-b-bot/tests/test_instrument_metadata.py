import pytest

from beta_bot.instrument_metadata import (
    InstrumentMetadata,
    InstrumentMetadataError,
    format_price,
    format_size,
    parse_perp_metadata,
    require_metadata,
)


BRRK = ("BTC", "ETH", "SOL", "BNB")


def _meta():
    return {
        "universe": [
            {"name": "BTC", "szDecimals": 5},
            {"name": "ETH", "szDecimals": 4},
            {"name": "SOL", "szDecimals": 2},
            {"name": "BNB", "szDecimals": 3},
        ]
    }


def test_all_brrk_instruments_are_loaded_from_exchange_metadata():
    parsed = require_metadata(parse_perp_metadata(_meta()), BRRK)
    assert tuple(parsed) == BRRK
    assert {coin: parsed[coin].sz_decimals for coin in BRRK} == {
        "BTC": 5,
        "ETH": 4,
        "SOL": 2,
        "BNB": 3,
    }


@pytest.mark.parametrize(
    ("coin", "raw", "expected"),
    [
        ("BTC", "0.123456789", 0.12345),
        ("ETH", "1.234567", 1.2345),
        ("SOL", "12.349", 12.34),
        ("BNB", "3.14159", 3.141),
    ],
)
def test_all_brrk_sizes_follow_metadata_not_a_global_decimal_constant(coin, raw, expected):
    metadata = parse_perp_metadata(_meta())[coin]
    assert format_size(raw, metadata) == expected


def test_size_rounds_toward_zero_so_formatting_cannot_increase_risk():
    metadata = InstrumentMetadata("BTC", sz_decimals=5)
    assert format_size("0.123459", metadata) == 0.12345


def test_price_applies_metadata_decimal_cap_and_five_significant_figures():
    btc = InstrumentMetadata("BTC", sz_decimals=5)
    sol = InstrumentMetadata("SOL", sz_decimals=2)
    assert btc.max_price_decimals == 1
    assert sol.max_price_decimals == 4
    assert format_price("12345.67", btc) == 12345.0
    assert format_price("123.45678", sol) == 123.45


def test_integer_price_is_allowed_without_significant_figure_truncation():
    metadata = InstrumentMetadata("BTC", sz_decimals=5)
    assert format_price("123456", metadata) == 123456.0


def test_missing_brrk_metadata_fails_closed():
    parsed = parse_perp_metadata({"universe": [{"name": "BTC", "szDecimals": 5}]})
    with pytest.raises(InstrumentMetadataError, match="missing required instruments"):
        require_metadata(parsed, BRRK)


def test_malformed_or_duplicate_metadata_fails_closed():
    with pytest.raises(InstrumentMetadataError, match="Invalid szDecimals"):
        parse_perp_metadata({"universe": [{"name": "BTC", "szDecimals": "5"}]})
    with pytest.raises(InstrumentMetadataError, match="Duplicate"):
        parse_perp_metadata(
            {"universe": [{"name": "BTC", "szDecimals": 5}, {"name": "BTC", "szDecimals": 5}]}
        )


def test_size_that_becomes_zero_is_rejected():
    with pytest.raises(InstrumentMetadataError, match="rounds to zero"):
        format_size("0.000009", InstrumentMetadata("BTC", sz_decimals=5))
