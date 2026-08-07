# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current dependency

```text
P4 dynamic leverage / operating risk budget
```

Phase 3 is complete:

```text
P3.1 data contract                 PASS / MERGED
P3.2 target calculation API       PASS / MERGED
P3.3 rebalance / turnover control PASS / MERGED
P3.4 contribution handling        PASS / MERGED
```

P3.4 PR #80 merged by expected-head squash as:

`949fb9f1d079df7c2462a4b13b0eb778e91bb3ae`

Final #80 evidence:

- Phase 0 #121 / run `31159909523`: SUCCESS, **215 passed in 7.58s** and 5/5 research integration OK
- Research evidence #32 / run `31159909467`: SUCCESS
- P3.2 parity/golden #19 / run `31159909468`: SUCCESS, independent parity + committed golden enforcement
- final body-edit governance #159 / run `31160307257`: SUCCESS

## Frozen upstream Phase 3 interfaces

P4 must not rewrite the completed Phase 3 chain merely to study leverage:

```text
P3.1 canonical daily data
-> P3.2-BRRK0011-V1
-> P3.3-L1-BAND-V1
-> P3.4-EQUITY-CHANGE-DAILY-V1
```

Frozen role boundary:

```text
target assets = BTC, ETH, SOL, BNB
feature-only  = XRP
current approved base gross <= 1
short targets forbidden
production_authorized_components = []
```

P3.2 target goldens, P3.3 0.05 L1 control semantics, and P3.4 next-daily contribution timing remain authoritative unless a later explicitly registered decision changes their own scope.

## P4 entry rule

Before any P4 implementation or experiment, reread the exact Phase 4 section of:

`docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`

Do not infer the P4 objective, search domain, operating drawdown budget, hard gross cap, funding/cost treatment or stress acceptance thresholds from memory.

The roadmap already makes several high-level boundaries explicit:

- preserve the current 0–1 corrected CVaR/CDaR scaler as the defensive baseline;
- do not overwrite historical BRRK results;
- preregister the leverage study before running it;
- candidate search may include gross >1, but deployment remains separately capped;
- optimize long-run compounded wealth subject to operating drawdown, catastrophe, tail-risk, liquidation-distance, cost and robustness constraints;
- P4 must include the roadmap-defined historical and synthetic stress suite.

These are entry constraints only. The exact P4 subsections must be reread before a fresh P4 branch is created.

## Explicit boundaries that remain separate

Do not silently absorb into P4 without explicit registered ownership:

- F23 funding-response redesign;
- P5 exit intelligence;
- short targets;
- XRP target exposure;
- production authorization;
- withdrawals/master-wallet-key handling.

The historical `EXPOSURE-SMOOTH-0038` experiment remains mechanism-validated but NOT PROMOTED and must not become a P4 baseline by implication.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Project drift audit

```text
DRIFT_0
```

## Exact next action

```text
finish post-P3.4 docs normalization
-> applicable CI / parity / governance
-> expected-head merge normalization
-> verify latest main
-> reread exact P4 roadmap section in full
-> create fresh P4 branch from that main
-> preregister / implement only the first P4 dependency authorized by the roadmap
```
