# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current dependency

```text
P3.1 feature-input parity correction
```

P0.1/P0.2, P1.1-P1.8, P2.1-P2.4 and the original P3.1 contract are merged. PR #71 and #72 are merged. PR #73 was manually merged as `89b095d7a7d746b768afca8245b963ecf15ffabc`; do not retroactively label #73 CI VERIFIED.

P3.2 remains the unique next roadmap implementation, but it is temporarily blocked by a concrete P3.1 parity defect discovered while recovering the frozen BRRK-0011 implementation.

## Why P3.2 is blocked

Frozen BRRK-0011 target weights are only for:

```text
BTC ETH SOL BNB
```

However its frozen regime feature model consumes an additional Binance spot series:

```text
XRPUSDT — feature-only, never a target/router asset
```

The original P3.1 payload contains only four price series. Removing XRP from the HMM feature panel would alter the frozen model; proceeding with only four canonical inputs would therefore fail the required research/live golden-parity gate.

The active correction makes the distinction explicit:

```text
target_assets  = BTC, ETH, SOL, BNB
feature_assets = XRP
strategy-signal daily payload = BTC, ETH, SOL, BNB, XRP
router-eligible assets         = BTC, ETH, SOL, BNB only
```

## Active correction scope

Branch:

```text
fix/p3-1-feature-input-parity
```

Required closure:

- schema-v2 machine data contract;
- XRPUSDT source mapping as feature-only;
- five-series fail-closed canonical strategy payload;
- four-asset router boundary preserved;
- research/live adapter parity regression;
- missing-XRP and router-rejection regression tests;
- CURRENT_STATE / P3.1 docs / crosswalk normalization;
- tests, self-review, PR governance, final-head CI, expected-head merge.

No decision-registry change is required because this correction does not promote research or authorize a new asset.

## P3.2 acceptance boundary after correction

Input:
- corrected canonical strategy-signal daily data;
- account equity;
- current positions;
- approved config.

Output must expose at least:
- BTC/ETH/SOL/BNB relative/target weights;
- cash share;
- base gross target;
- risk state and corrected defensive scale;
- model/version;
- economic decision timestamp;
- feature snapshot;
- data-contract digest/version;
- target-engine version.

Frozen chain:

```text
build_brrk0011_scale
-> fit_variational_regime_model_nd
-> filtered_posterior
-> fit_state_v1_distribution
-> sample_v1_paths
-> choose_scale_corrected
-> final_scale = 1 - P(RISK_OFF) * (1 - meta_scale)
-> BRRK_0011_BASELINE = v1_raw.mul(final_scale, axis=0)
```

Gross target remains within `[0, 1]`; cash is residual `1 - gross`.

Do not add:
- P3.3 rebalance/turnover bands;
- P3.4 weekly contribution handling;
- F23 funding-response redesign;
- P4 leverage above 1;
- P5 cycle-exit intelligence;
- short logic;
- XRP target exposure;
- production authorization.

## Required P3.2 parity evidence

After the correction is on main, create a **new fresh P3.2 branch**. Do not continue `p3-2/target-calculation-api-v2`, which was created before this dependency correction and intentionally contains no P3.2 implementation.

P3.2 must include deterministic research/live golden parity across materially different historical decisions, including bull/full exposure, risk-off/low exposure, transitions, 2021 stress, 2022 bear, 2024 stress and recent 2025/2026 decisions.

Compare at least:
- per-asset target weights;
- gross target;
- cash share;
- risk state / scale;
- feature snapshot;
- model/data/engine version metadata.

No same-window retuning is permitted.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Project drift audit

```text
DRIFT_1
```

The drift is an implementation/data-contract mismatch: XRP was part of the frozen feature model but absent from P3.1 canonical inputs. Product universe, venue, BRRK research authority, risk philosophy, human approval and security boundaries remain unchanged.

## Exact next action

```text
complete and verify fix/p3-1-feature-input-parity
-> correction PR / CI / expected-head merge
-> post-merge normalization
-> fresh P3.2 branch from corrected main
-> canonical target-engine implementation
-> multi-date research/live golden parity
-> self-review / CI / expected-head merge
```
