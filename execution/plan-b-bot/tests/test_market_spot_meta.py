import pytest

from beta_bot import market


def test_fetch_spot_metadata_uses_spotmeta_info_request(monkeypatch):
    calls = []

    def fake_post(api_url, payload, timeout):
        calls.append((api_url, payload, timeout))
        return {
            "tokens": [
                {"name": "USDC", "index": 0},
                {"name": "UBTC", "index": 1},
            ],
            "universe": [
                {"name": "BTC/USDC", "tokens": [1, 0], "index": 42},
            ],
        }

    monkeypatch.setattr(market, "_post", fake_post)
    result = market.fetch_spot_metadata("https://api.hyperliquid.xyz", timeout=3.5)
    assert result["universe"][0]["index"] == 42
    assert calls == [
        ("https://api.hyperliquid.xyz", {"type": "spotMeta"}, 3.5),
    ]


def test_fetch_spot_metadata_rejects_malformed_shape(monkeypatch):
    monkeypatch.setattr(market, "_post", lambda *args, **kwargs: {"tokens": []})
    with pytest.raises(RuntimeError, match="Unexpected spotMeta shape"):
        market.fetch_spot_metadata("https://api.hyperliquid.xyz", timeout=1.0)
