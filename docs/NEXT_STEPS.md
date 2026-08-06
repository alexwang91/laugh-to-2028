# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current roadmap task

```text
P3.2 Target calculation API
```

P0.1, P0.2, P1.1-P1.8, P2.1-P2.4 and P3.1 are PASS / MERGED.

Pre-P3.2 audit corrections are also closed:

- PR #71: PASS / MERGED;
- PR #72: PASS / MERGED as `6edaff4bb62bba8316722265dd216ba6e5e7d541`;
- F27 R2 is the authoritative corrected measurement while R1 remains preserved as superseded history;
- EXPOSURE-SMOOTH-0038 is recorded as mechanism validated but NOT PROMOTED / BASELINE UNCHANGED.

P3.2 is now the unique next roadmap implementation. Do not start P3.3, P3.4, P4, P5, P6, P7 or P8 early.

## P3.2 acceptance boundary

Input:
- canonical daily data from P3.1;
- account equity;
- current positions;
- approved config.

Output must expose at least:
- relative target weights for BTC / ETH / SOL / BNB;
- cash share;
- base gross target;
- risk state and corrected defensive scale;
- model/version;
- economic decision timestamp;
- feature snapshot;
- data-contract digest/version;
- target-engine version.

The implementation must deterministically reproduce the frozen BRRK-0011 directional core from the same canonical historical input.

Canonical frozen research chain to reproduce:

```text
build_brrk0011_scale
-> fit_state_v1_distribution
-> sample_v1_paths
-> choose_scale_corrected
-> corrected 0-1 regime scale
-> BRRK_0011_BASELINE = v1_raw.mul(brrk_scale, axis=0)
```

The P3.2 gross target must remain within `[0, 1]`; cash is the residual `1 - gross`.

P3.2 is target calculation only. Do not add:
- P3.3 rebalance/turnover bands;
- P3.4 weekly contribution handling;
- F23 funding-response redesign;
- P4 leverage-above-1 research;
- P5 cycle-exit intelligence;
- short logic;
- production authorization.

`EXPOSURE-SMOOTH-0038` is not the P3.2 baseline. It is mechanism-validation evidence that was not promoted. `ASYM-BETA-0024` is also not P3.2 authority.

## Required parity evidence

P3.2 must include deterministic research/live golden-parity tests across multiple historical decision dates using the same canonical P3.1 data and frozen parameters.

The parity set should cover materially different regimes, including:
- bull / full-exposure behavior;
- risk-off / low-exposure behavior;
- regime transitions;
- 2021 stress;
- 2022 bear conditions;
- 2024 stress;
- recent 2025/2026 decisions.

Compare at least:
- per-asset target weights;
- gross target;
- cash share;
- risk state / scale;
- feature snapshot and version metadata.

No same-window retuning is allowed merely to make parity pass.

## Dependency architecture requirement

Research code currently depends on scientific Python packages including numpy/pandas/scipy/sklearn/hmmlearn. P3.2 must establish an explicit canonical target-engine dependency boundary suitable for live deterministic execution. Do not simply import ad-hoc research scripts into runtime without a versioned architecture and parity evidence.

## Ordered forward program

```text
P1.1-P1.8 COMPLETE
P2.1-P2.4 COMPLETE
P3.1 COMPLETE
AUDIT CORRECTIONS COMPLETE
P3.2 NEXT ROADMAP IMPLEMENTATION
P3.3 BLOCKED ON P3.2
P3.4 BLOCKED
P4   BLOCKED
P5   BLOCKED
P6   BLOCKED
P7   BLOCKED
P8   BLOCKED
```

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Project drift audit

Current audit finding after the #72 normalization chain:

```text
DRIFT_0
```

No known roadmap/handoff correction now blocks P3.2. This does not alter product objective, universe, venue, research authority, risk philosophy, human-approval, wallet/security, stopped-line policy, or production authorization.

## Exact next action

```text
merge this narrow post-#72 handoff normalization
-> create a fresh P3.2 target-calculation branch from then-current main
-> recover the exact frozen BRRK-0011 allocation / regime / corrected defensive-scale implementation from GitHub
-> define the canonical deterministic target-engine boundary
-> implement P3.2 only
-> add multi-date research/live golden parity
-> tests / self-review / drift audit / PR / CI / expected-head merge
```
