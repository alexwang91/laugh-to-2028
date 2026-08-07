# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current dependency

```text
P3.1 schema-v2 post-merge validation
```

PR #74 has merged to main as `277eb777b4b28d32bb24c201bba1155b08686c71`, so the XRP feature-input implementation residual is no longer an unmerged code dependency. However neither #74 head `22a00c894b2ae54a7e1d45ebeefb996e8597182f` nor the resulting main SHA received a GitHub Actions workflow run during the Actions outage.

Therefore the correct evidence state is:

```text
IMPLEMENTED = YES
MERGED = YES
TESTED = NOT YET VERIFIED
CI VERIFIED = NO
```

P3.2 remains the unique next roadmap implementation, but it must not begin until a fresh validation PR produces real Phase 0 and governance evidence for the merged P3.1 v2 contract.

## Frozen P3.1 v2 role boundary

```text
target_assets  = BTC, ETH, SOL, BNB
feature_assets = XRP
strategy-signal daily payload = BTC, ETH, SOL, BNB, XRP
router-eligible assets         = BTC, ETH, SOL, BNB only
```

XRP remains feature-only. It cannot receive a target weight and cannot enter funding/basis routing.

## Validation gate

Use a narrow post-merge validation/handoff PR from current main. It must trigger the existing `Phase 0 baseline contract` workflow and require:

- full `execution/plan-b-bot` pytest suite;
- research integration contract;
- PR handoff governance;
- no strategy logic, parameter, decision-registry or production-authorization change.

Do not treat the absence of #74 workflow runs as a test pass or test failure; it is missing evidence caused by the GitHub Actions incident.

## P3.2 acceptance boundary after validation

Input:
- corrected schema-v2 canonical strategy-signal daily data;
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

After the validation PR is merged, create a **new fresh P3.2 branch** from then-current main. Do not continue `p3-2/target-calculation-api-v2`, which predates the schema-v2 correction and contains no P3.2 implementation.

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

The model/input semantics are now aligned on main. The remaining drift is evidence/governance: the merged correction has no recorded Actions validation.

## Exact next action

```text
post-merge validation/handoff PR
-> Phase 0 pytest + research integration
-> PR governance
-> merge
-> fresh P3.2 branch from new main
-> canonical target-engine implementation
-> multi-date research/live golden parity
-> self-review / CI / expected-head merge
```
