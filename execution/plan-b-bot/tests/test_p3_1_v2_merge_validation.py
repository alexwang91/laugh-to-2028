# CI retrigger marker 2: no semantic change; emits another fresh pull_request synchronize event.

from beta_bot.data_contract import (
    CANONICAL_ASSETS,
    STRATEGY_FEATURE_ASSETS,
    STRATEGY_SIGNAL_ASSETS,
    load_data_contract,
)


def test_p3_1_v2_post_merge_contract_roles_are_frozen():
    policy = load_data_contract()

    assert policy.schema_version == 2
    assert CANONICAL_ASSETS == ("BTC", "ETH", "SOL", "BNB")
    assert STRATEGY_FEATURE_ASSETS == ("XRP",)
    assert STRATEGY_SIGNAL_ASSETS == CANONICAL_ASSETS + STRATEGY_FEATURE_ASSETS

    assert policy.canonical_assets == CANONICAL_ASSETS
    assert policy.strategy_feature_assets == STRATEGY_FEATURE_ASSETS
    assert policy.strategy_signal_assets == STRATEGY_SIGNAL_ASSETS
    assert set(policy.source_mappings) == set(STRATEGY_SIGNAL_ASSETS)
    assert policy.source_symbol("XRP", 0) == "XRPUSDT"
