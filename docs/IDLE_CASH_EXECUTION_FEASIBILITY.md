# Idle Cash Execution Feasibility — 2026-08-09

Status: **NOT_FEASIBLE_ON_HYPERLIQUID_STANDARD / FUTURE_OPTION_ONLY / NOT_AUTHORIZED**

This document evaluates whether the corrected F27 idle-cash credit can be realized inside the already-frozen Phase-6 / Phase-7 V1 operating contract. It is an execution-feasibility review, not a new strategy experiment, not a yield forecast, and not production authorization.

## Authoritative economic evidence

Authoritative measurement: `research/results/idle_cash_credit_0027r2.json` (`IDLE-CASH-CREDIT-F27-R2-MEASUREMENT-FIX`).

R2 supersedes R1 for measurement authority because R1 dropped the first realized equity observation when constructing returns. R2 preserves day-one PnL from the known `$10,000` starting base. R1 remains immutable historical evidence.

Corrected R2 headline evidence:

| Metric | V1 baseline | BRRK-0011 core |
| --- | ---: | ---: |
| mean idle-cash fraction | 20.5183% | 24.5700% |
| raw CAGR | 61.3127% | 65.1661% |
| credited CAGR | 62.6632% | 66.8068% |
| CAGR delta | +1.3505 pp | +1.6407 pp |
| Sharpe, rf=0, raw -> credited | 1.2950 -> 1.3138 | 1.3532 -> 1.3756 |
| excess Sharpe, raw -> credited | 1.2724 -> 1.3029 | 1.3667 -> 1.4039 |
| max drawdown, raw -> credited | -37.6349% -> -36.6003% | -33.7151% -> -33.5524% |

The R2 economic conclusion remains the same as R1: assigning a risk-free-like return to otherwise idle cash improves the measured historical path. That is a **counterfactual credit**, not proof that the current Hyperliquid Standard account can earn the same return while preserving identical margin availability.

## Frozen V1 execution constraint

Phase-6 account identity and valuation semantics require Hyperliquid Standard mode:

```text
userAbstraction = disabled
production gross cap = 1.0
production_authorized_components = []
production_authorized = false
signature_authorized = false
order_submission_authorized = false
```

Any implementation must preserve, at minimum:

- immediate margin availability for the canonical BRRK target;
- liquidation distance / margin buffer;
- real-time callability at the canonical decision boundary;
- frozen valuation semantics;
- no hidden venue, asset, smart-contract, redemption or maturity dependency.

If a yield mechanism weakens any of those properties, it is not equivalent to idle Standard-mode margin and is rejected for V1.

## Hyperliquid mechanism review

### 1. Standard account idle perp margin

**Result: NOT FEASIBLE AS AN AUTOMATIC YIELD SOURCE.**

The frozen V1 account mode is Standard. Current Hyperliquid documentation distinguishes Standard from Portfolio Margin; the documented automatic yield on eligible unused borrowable assets belongs to Portfolio Margin, not the frozen Standard account semantics.

Therefore F27's risk-free credit cannot be treated as an automatic return on unused Standard-mode perp margin.

### 2. Portfolio Margin supply / automatic idle-asset yield

**Result: REJECT FOR V1 / FUTURE SEPARATE DESIGN ONLY.**

Official Hyperliquid Portfolio Margin documentation states that Portfolio Margin accounts automatically earn yield on borrowable assets not actively used for trading and can supply eligible quote assets. It also defines a different unified spot/perp margin, borrowing, interest and liquidation regime.

Switching the observation/execution account from Standard to Portfolio Margin would therefore change the already-frozen account-abstraction, valuation, collateral and liquidation semantics. It is not a docs-only implementation detail and cannot be used to realize F27 inside V1.

Official source: `https://hyperliquid.gitbook.io/hyperliquid-docs/trading/portfolio-margin`

### 3. Separate HyperCore lending / supply position

**Result: NOT EQUIVALENT TO IMMEDIATELY CALLABLE STANDARD PERP MARGIN.**

A separate supplied/lent balance is a different position from unused Standard-mode perp collateral. Even where supply functionality exists, treating supplied capital as simultaneously available canonical margin would require a separate valuation, withdrawal/callability, failure-mode and liquidation-impact contract.

No such contract is frozen for V1. Do not count supplied capital as available margin by assumption.

### 4. HLP / protocol vault

**Result: REJECT FOR V1.**

HLP is a strategy-bearing protocol vault, not a cash-equivalent margin account. Depositors share vault PnL, and official documentation states a 4-day deposit lock-up. That introduces strategy risk and destroys immediate callability.

Official source: `https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/vaults/protocol-vaults`

### 5. HYPE staking

**Result: REJECT FOR V1.**

Staking requires conversion/exposure to HYPE rather than maintaining the required quote-collateral economics. Official documentation also states that transfers from staking back to spot have a 7-day queue. It therefore fails both cash-equivalence and immediate-callability requirements.

Official source: `https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/staking`

### 6. Treasury / RWA / yield-bearing token

**Result: REJECT FOR V1.**

A tokenized treasury, RWA or yield token introduces at least conversion, redemption, issuer/product and potentially smart-contract risk. Unless Hyperliquid Standard margin natively recognizes the asset with identical frozen valuation and immediate collateral semantics, it cannot be assumed equivalent to idle USDC margin.

### 7. External lending venue / HyperEVM protocol / off-venue sweep

**Result: REJECT FOR V1.**

Moving capital outside the frozen Standard account adds withdrawal/bridge/venue/smart-contract risk and makes the measured portfolio depend on an additional execution system. It also creates a return-of-capital latency problem at exactly the point when BRRK may need to raise gross exposure.

### 8. Bridge / withdrawal to an external cash instrument

**Result: REJECT FOR V1.**

A withdrawal is an explicit signed transfer and takes funds out of the frozen venue/account state. It is neither instantaneous margin nor within the current observation/valuation contract.

## Primary conclusion

```text
F27 economic opportunity                 REAL AS A COUNTERFACTUAL MEASUREMENT
Hyperliquid Standard automatic yield     NOT ESTABLISHED
V1 implementation feasibility            NOT_FEASIBLE_ON_HYPERLIQUID_STANDARD
production implementation                NOT_AUTHORIZED
future research/design status             FUTURE_OPTION
required before any future use            SEPARATE DESIGN + CONTRACT + APPROVAL
```

The key distinction is:

> **R2 measures the value of idle-cash credit if such credit can be obtained without changing the portfolio. It does not establish that Hyperliquid Standard provides that return while preserving the same immediately callable margin.**

For Phase-7 V1, preserving margin buffer and liquidation distance has priority over harvesting the measured ~1.64 pp historical CAGR credit.

## Small-capital materiality

Using the BRRK R2 CAGR delta of `1.6406994813 percentage points` only as simple arithmetic:

### Static `$2,000`

```text
$2,000 × 0.016406994813 = $32.81 per year
```

### `$2,000` initial capital + `$100/week`

Under a simple uniform-contribution approximation:

```text
52 weekly contributions = $5,200
average contribution capital during year ≈ $2,600
average capital ≈ $2,000 + $2,600 = $4,600
$4,600 × 0.016406994813 = $75.47 per year
```

These are arithmetic illustrations, not strategy simulations, not current executable yield quotes, and not guaranteed returns. At this capital scale the absolute dollar benefit is too small to justify adding a materially different margin regime, lock-up, bridge, venue or smart-contract dependency to V1.

## Future-option gate

Idle-cash yield may be reconsidered only as a separate future work item if all of the following are frozen before implementation or economic testing:

1. exact account abstraction / venue / instrument;
2. capital-call latency and deterministic redemption behavior;
3. treatment in P3.3 / Phase-6 valuation;
4. liquidation-distance and available-margin effect;
5. smart-contract / issuer / venue / bridge failure modes;
6. fail-closed rule when the yield asset cannot be converted immediately;
7. prospective evidence and explicit approval.

A future design must not reuse F27 R2 as evidence that these execution risks have already been tested.

## Production authority

No production authority changes here.

```text
production gross cap              1.0
production_authorized_components = []
production_authorized             false
signature_authorized              false
order_submission_authorized       false
collector_armed                   false
schedule_configured               false
elapsed_evidence_credit_authorized false
```
