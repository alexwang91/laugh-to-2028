import importlib.util
from datetime import datetime, timezone
from pathlib import Path

from beta_bot.data_contract import DAY_MS, build_canonical_daily_dataset, load_data_contract


def kline(day, close):
    open_ms = day * DAY_MS
    return [
        open_ms,
        str(close),
        str(close),
        str(close),
        str(close),
        "1",
        open_ms + DAY_MS - 1,
        "1",
        1,
        "1",
        "1",
        "0",
    ]


def batches():
    policy = load_data_contract()
    output = {}
    for index, asset in enumerate(("BTC", "ETH", "SOL", "BNB")):
        symbol = policy.source_symbol(asset, DAY_MS)
        output[asset] = [(symbol, [kline(day, 100 + index + day) for day in range(1, 5)])]
    return output


def load_research_adapter():
    repo_root = Path(__file__).resolve().parents[3]
    path = repo_root / "research" / "integration" / "p3_1_data_contract_adapter.py"
    spec = importlib.util.spec_from_file_location("p3_1_data_contract_adapter", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_research_and_live_adapters_emit_byte_identical_canonical_payload():
    source = batches()
    decision = datetime.fromtimestamp(5 * DAY_MS / 1000, tz=timezone.utc)
    live = build_canonical_daily_dataset(
        source_batches=source,
        decision_timestamp=decision,
        policy=load_data_contract(),
    )
    research = load_research_adapter().canonicalize_research_daily_history(
        source_batches=source,
        decision_timestamp=decision.isoformat().replace("+00:00", "Z"),
    )
    assert research.canonical_json() == live.canonical_json()
    assert research.digest() == live.digest()
