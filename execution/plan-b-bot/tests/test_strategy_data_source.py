from beta_bot.data_contract import DAY_MS, load_data_contract
from beta_bot.strategy_data_source import build_binance_daily_request, fetch_binance_daily_rows


def test_binance_daily_request_makes_utc_timezone_explicit():
    policy = load_data_contract()
    params = build_binance_daily_request(
        policy=policy,
        symbol="BTCUSDT",
        start_ms=DAY_MS,
        end_ms=2 * DAY_MS - 1,
    )
    assert params == {
        "symbol": "BTCUSDT",
        "interval": "1d",
        "startTime": DAY_MS,
        "endTime": 2 * DAY_MS - 1,
        "timeZone": "0",
        "limit": 1000,
    }


def test_binance_source_uses_contract_endpoint_fallback(monkeypatch):
    policy = load_data_contract()
    calls = []

    class Response:
        def __init__(self, payload, fail=False):
            self.payload = payload
            self.fail = fail

        def raise_for_status(self):
            if self.fail:
                raise RuntimeError("primary unavailable")

        def json(self):
            return self.payload

    row = [DAY_MS, "1", "1", "1", "1", "1", 2 * DAY_MS - 1, "1", 1, "1", "1", "0"]

    def fake_get(url, params, timeout):
        calls.append((url, dict(params), timeout))
        if len(calls) == 1:
            return Response([], fail=True)
        return Response([row])

    monkeypatch.setattr("beta_bot.strategy_data_source.requests.get", fake_get)
    result = fetch_binance_daily_rows(
        policy=policy,
        symbol="BTCUSDT",
        start_ms=DAY_MS,
        end_ms=2 * DAY_MS - 1,
        timeout=2.5,
    )
    assert result == [row]
    assert calls[0][0] == policy.strategy_endpoints[0]
    assert calls[1][0] == policy.strategy_endpoints[1]
    assert calls[1][1]["timeZone"] == "0"
