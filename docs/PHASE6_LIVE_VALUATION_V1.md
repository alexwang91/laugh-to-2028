# Phase 6 Live Valuation V1

Status: **FROZEN STANDARD-MODE VALUATION / ACCOUNT NOT YET BOUND / ZERO AUTHORITY**

Machine authority: `research/governance/phase6_live_valuation_contract.json`.

This prospective operational contract maps exact read-only Hyperliquid account state into the already-frozen P3.3 inputs. It does not change P3.2 targets, P3.3 banding, routing economics, Phase-6 acceptance thresholds, production authorization, signing, or order submission.

## Supported account mode

V1 accepts only an account whose `userAbstraction` response is exactly `disabled`, i.e. explicit Standard mode with separate spot and perp balances. `unifiedAccount`, `portfolioMargin`, `default`, and `dexAbstraction` fail closed and cannot earn Phase-6 elapsed credit under this contract.

The account address remains a separate pre-arm dependency and is not selected by this document.

## Canonical position mapping

For BTC / ETH / SOL / BNB:

- perp component = `sign(szi) * abs(positionValue)` from the first canonical perp DEX `clearinghouseState`;
- spot component = `balances[].total * spot markPx` for the instrument-registry identities UBTC / UETH / USOL;
- current P3.3 notional = perp component + spot component for the same economic asset;
- BNB spot is forbidden because canonical product policy remains `PERP_ONLY_DEFAULT`;
- missing canonical assets are zero;
- unknown nonzero spot/perp assets and duplicate identities fail closed.

## Canonical account equity mapping

For Standard mode only:

`account_equity_usd = first-perp-dex marginSummary.accountValue + spot USDC total + allowed spot base mark-to-market value`.

Spot `hold` is validated but is not subtracted from `total`, because held tokens remain owned balances. `entryNtl` is not used for current mark-to-market equity.

The derived equity must be finite and strictly positive.

## Scope exclusions

The measured portfolio is one exact Hyperliquid master or subaccount address. An agent-wallet address is not an account identity. External exchange/wallet holdings, other perp-DEX/vault/borrow-lend positions, Unified Account and Portfolio Margin are unsupported by V1 and may not be silently ignored or aggregated.

If the eventual observation account does not satisfy this scope, the collector remains blocked; the contract is not broadened after seeing live evidence merely to make the account fit.

## Provenance

Raw response bytes must be preserved before parsing under `PHASE6-LIVE-EVIDENCE-BACKEND-V1`. Runtime spot identity must match `spotMeta` and `config/instrument_registry.json`; no nearest-symbol, cross-venue price, or asset substitution is permitted.

## Remaining pre-arm dependency

After this contract merges, the only unresolved pre-arm dependency is one explicit verified read-only observation account identity compatible with this V1. The collector remains unarmed and creates no elapsed evidence until a later prospective arm change.
