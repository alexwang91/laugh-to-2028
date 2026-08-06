import pytest

from beta_bot import market


def test_fetch_l2_book_uses_canonical_info_payload(monkeypatch):
    calls = []
    snapshot = {
        "coin": "BTC",
        "time": 1,
        "levels": [
            [{"px": "99", "sz": "1", "n": 1}],
            [{"px": "101", "sz": "1", "n": 1}],
        ],
    }

    def fake_post(api_url, payload, timeout):
        calls.append((api_url, payload, timeout))
        return snapshot

    monkeypatch.setattr(market, "_post", fake_post)
    result = market.fetch_l2_book("https://api.hyperliquid.xyz", "BTC", 3.0)
    assert result == snapshot
    assert calls == [
        ("https://api.hyperliquid.xyz", {"type": "l2Book", "coin": "BTC"}, 3.0)
    ]


def test_fetch_l2_book_preserves_runtime_spot_pair_id(monkeypatch):
    captured = {}

    def fake_post(api_url, payload, timeout):
        captured.update(payload)
        return {"coin": "@142", "time": 1, "levels": [[], []]}

    monkeypatch.setattr(market, "_post", fake_post)
    market.fetch_l2_book("https://api.hyperliquid.xyz", "@142", 2.0)
    assert captured == {"type": "l2Book", "coin": "@142"}


@pytest.mark.parametrize("payload", [None, [], {"levels": []}, {"levels": [{}, {}]}])
def test_fetch_l2_book_rejects_malformed_shape(monkeypatch, payload):
    monkeypatch.setattr(market, "_post", lambda *_args, **_kwargs: payload)
    with pytest.raises(RuntimeError, match="l2Book"):
        market.fetch_l2_book("https://api.hyperliquid.xyz", "BTC", 2.0)
