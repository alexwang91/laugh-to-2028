from __future__ import annotations

import ast
from pathlib import Path

from beta_bot.bear_short_research import (
    ShortCandidateEvidence,
    ShortEconomics,
    candidate_eligible,
    compare_candidate_to_benchmarks,
    eligible_symbols,
)


def row(symbol: str, **kw) -> ShortCandidateEvidence:
    d=dict(contemporaneous_top20=False,live_liquidity_ok=True,reliable_perp_market=True,spread_depth_ok=True,funding_non_pathological=True,market_structure_ok=True,history_days=365)
    d.update(kw)
    return ShortCandidateEvidence(symbol=symbol, **d)


def test_core_universe_and_top20_expansion_fail_closed() -> None:
    assert candidate_eligible(row('BTC'))
    assert not candidate_eligible(row('DOGE'))
    assert candidate_eligible(row('DOGE', contemporaneous_top20=True))
    assert not candidate_eligible(row('DOGE', contemporaneous_top20=True, spread_depth_ok=False))
    assert not candidate_eligible(row('ETH', funding_non_pathological=False))
    assert not candidate_eligible(row('SOL', history_days=89))


def test_eligible_symbols_are_deterministic() -> None:
    rows=[row('BTC'),row('ETH'),row('DOGE', contemporaneous_top20=True),row('BNB', market_structure_ok=False)]
    assert eligible_symbols(rows)==('BTC','DOGE','ETH')


def test_comparison_is_descriptive_and_never_launch_authority() -> None:
    c=ShortEconomics('SOL',0.22,0.18,0.01,0.005,1.5,0.8)
    result=compare_candidate_to_benchmarks(c, short_btc_after_cost_return=0.14, short_brrk_after_cost_return=0.16)
    assert result['beats_both_benchmarks'] is True
    assert result['research_only'] is True
    assert result['edge_vs_short_btc']==0.08
    assert result['edge_vs_short_brrk']==0.06


def test_research_module_has_no_execution_path() -> None:
    path=Path(__file__).resolve().parents[1]/'beta_bot'/'bear_short_research.py'
    tree=ast.parse(path.read_text())
    imports=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Import): imports.extend(a.name for a in n.names)
        elif isinstance(n,ast.ImportFrom): imports.append(n.module or '')
    forbidden=('executor','hyperliquid','eth_account','web3','emergency','service')
    assert not any(any(x in name for x in forbidden) for name in imports)
