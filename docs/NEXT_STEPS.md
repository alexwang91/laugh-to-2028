# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current dependency

```text
P4.3 generalized corrected-risk leverage runner
```

P4.1 and P4.2 are merged by PR #82 as main `6d0e497583607e09991593588e62df7fb418087c`.

Final #82 evidence:

- Phase 0 #126 / run `31163656193`: SUCCESS, 224 execution tests + 5/5 integration
- Research evidence #37 / run `31163656181`: SUCCESS
- P3.2 parity/golden #24 / run `31163656179`: SUCCESS
- final body-edit governance #166 / run `31163843751`: SUCCESS

## Frozen P4.1 baseline

`research/leverage_0039/P4_1_BASELINE_FREEZE.json`

`P4.1-BRRK0011-CORRECTED-0-1-V1`

```text
corrected scale domain       0 .. 1
scenario CVaR/CDaR budget    20%
production gross cap         1.0
operating risk budget        UNFROZEN
catastrophic DD boundary     70% termination boundary only
```

Historical BRRK artifacts and separate metric-provenance conventions remain frozen.

## Frozen P4.2 prereg

`research/leverage_0039/LEVERAGE-0039.json`

Status:

`PREREGISTERED_BEFORE_FIRST_RUN`

```text
research caps               1.00 / 1.10 / 1.20 / 1.30
operating MDD constraints   35% / 40% / 45% / 50%
matched costs               5 / 10 / 20 / 50 bps
scenario tail budget        20%
catastrophe boundary        70%
```

Funding remains cost-only; Hyperliquid native evidence is mandatory; Binance is proxy/stress-only; no funding signal/threshold; F23 remains separate.

## P4.3 required order

Do not run `LEVERAGE-0039` immediately after normalization. First:

1. create a fresh P4.3 branch from latest main;
2. snapshot and hash the canonical Hyperliquid margin/leverage-tier inputs needed for liquidation-distance modeling;
3. implement a generalized version of the **same corrected CVaR/CDaR selector**, changing only its maximum scale/cap;
4. preserve BRRK relative targets, HMM states/features, Student-t model, 20% scenario tail budget and Phase-3 semantics;
5. build a deterministic runner that can reproduce the frozen <=1 baseline;
6. require cap=1 exact parity before any >1 candidate is evaluated;
7. only then execute the preregistered candidate/stress suite exactly once.

No prereg thresholds, cap grid, stress windows, funding treatment or promotion gates may be retuned after results are seen. Material change requires a new experiment ID.

## Still blocked

```text
LEVERAGE SEARCH RUN:         NO
RESULT SELECTED:             NO
OPERATING BUDGET FROZEN:     NO
>1 RUNTIME IMPLEMENTED:      NO
PRODUCTION AUTHORIZED:       NO_CHANGE
```

Also blocked/separate:

- search >1.30 under LEVERAGE-0039;
- EXPOSURE-SMOOTH-0038 promotion;
- F23 funding response;
- shorts / XRP targets;
- P5 exit intelligence;
- production authorization.

`production_authorized_components = []` remains unchanged.

## Project drift audit

```text
DRIFT_0
```

## Exact next action

```text
finish post-P4.1/P4.2 normalization
-> fresh P4.3 branch
-> freeze Hyperliquid liquidation inputs
-> generalized selector/runner
-> cap=1 parity
-> execute LEVERAGE-0039 once only after parity passes
```
