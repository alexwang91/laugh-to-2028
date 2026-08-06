# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0.1 / P0.2: PASS / MERGED
- P1.1 through P1.8: PASS / MERGED; Phase 1 COMPLETE
- P2.1 through P2.4: PASS / MERGED; Phase 2 COMPLETE
- P3.1 Data contract: PASS / MERGED
- Audit correction PR #71: PASS / MERGED
- Research/evidence normalization PR #72: PASS / MERGED
- Current authoritative `main`: `6edaff4bb62bba8316722265dd216ba6e5e7d541`
- Legacy backlog/roadmap bridge: `docs/BACKLOG_ROADMAP_CROSSWALK_2026-08-06.md`
- Historical stale-main PR #70: INVALID / CLOSED / DO NOT REVIVE

## Current roadmap position

```text
P3.1     PASS / MERGED
#71      PASS / MERGED
#72      PASS / MERGED
P3.2     UNIQUE NEXT ROADMAP IMPLEMENTATION
P3.3+    BLOCKED
```

P3.2 is target calculation only. It must reproduce the frozen BRRK-0011 baseline and must not absorb F23 funding redesign, EXPOSURE-SMOOTH-0038 promotion, ASYM-BETA promotion, >1 leverage, cycle-exit logic, short logic, P3.3 rebalance/turnover behavior, P3.4 contributions, or production authorization.

## PR #72 closure

PR `#72 Audit normalization: repair F27 measurement and record EXPOSURE-SMOOTH-0038` was squash-merged after final-head CI passed.

Final PR head:

```text
fb13142082d0f2b0ca15dc61103954708e87af15
```

Squash merge on `main`:

```text
6edaff4bb62bba8316722265dd216ba6e5e7d541
```

### IMPLEMENTED

F27 measurement correction:

- `research/results/idle_cash_credit_0027r1.json` is preserved as superseded historical measurement evidence;
- day-one return is reconstructed from the known `$10,000` base instead of being dropped by `pct_change().dropna()`;
- the script refuses to emit R2 unless BRRK-0011 raw CAGR reproduces the frozen calendar-span anchor `0.6516609785...`;
- corrected evidence is committed as `research/results/idle_cash_credit_0027r2.json`;
- no BRRK/V1 weights, parameters, regime fit, source convention, or strategy economics changed.

Corrected F27 R2 headline metrics:

| Metric | V1 baseline | BRRK-0011 core |
|---|---:|---:|
| mean idle cash | 20.5183% | 24.5700% |
| raw CAGR | 61.3127% | 65.1661% |
| credited CAGR | 62.6632% | 66.8068% |
| CAGR delta | +1.3505 pp | +1.6407 pp |
| raw Sharpe (rf=0) | 1.2950 | 1.3532 |
| credited Sharpe (rf=0) | 1.3138 | 1.3756 |
| raw excess Sharpe | 1.2724 | 1.3667 |
| credited excess Sharpe | 1.3029 | 1.4039 |
| raw MDD | -37.6349% | -33.7151% |
| credited MDD | -36.6003% | -33.5524% |

BRRK-vs-V1 rf=0 Sharpe gap moves from `+0.0581629` to `+0.0617832`, shift `+0.0036204`. Qualitative F27 conclusion is unchanged.

EXPOSURE-SMOOTH-0038 authority normalization:

- result summary states `MECHANISM_VALIDATED_NOT_PROMOTED_BASELINE_UNCHANGED`;
- `docs/EXPOSURE_SMOOTH_0038_DECISION_2026-08-06.md` records the governance decision;
- `config/decision_registry.json` records `EXPOSURE-SMOOTH-0038` as `SHADOW_ONLY` historical/mechanism evidence;
- frozen V1 and BRRK-0011 authority remain unchanged;
- 0038 must not be substituted into P3.2 and is not leverage or production authorization.

### TESTED / CI VERIFIED

Final head `fb13142082d0f2b0ca15dc61103954708e87af15` completed the required gates successfully:

- `Research evidence normalization` run `31119256543`: SUCCESS;
- `Phase 0 baseline contract` run `31119256293`: SUCCESS;
- `PR handoff governance` run `31119364631`: SUCCESS;
- incidental `CARRY RF 0036R1` run `31119256178`: SUCCESS.

Earlier setup-only `Service Unavailable` / queued-timeout failures occurred during the GitHub Actions outage and were retried without lowering any gate.

### MERGED

```text
YES — PR #72 squash-merged to main as 6edaff4bb62bba8316722265dd216ba6e5e7d541.
```

### PRODUCTION AUTHORIZED

```text
NO_CHANGE
production_authorized_components = []
```

No live capital, leverage expansion, new asset, short, withdrawal, transfer, or cutover authorization was created by #72.

## Research / strategy boundaries retained

- `BRRK-0011` remains the frozen canonical directional research target; do not retune it on the current historical window.
- `EXPOSURE-SMOOTH-0038` is mechanism-valid evidence only: **NOT PROMOTED / BASELINE UNCHANGED**.
- `ASYM-BETA-0024` remains shadow-only evidence, not leverage authorization.
- stopped PIT-alpha, TSMOM and carry lines remain stopped.
- F23 funding-response redesign remains a separately registered research boundary and must not enter P3.2.
- P4 is the first phase allowed to research >1 gross exposure.

## Project drift audit

```text
DRIFT_0
```

The pre-P3.2 audit/evidence correction chain is now closed on main. No known roadmap/handoff mismatch blocks P3.2. This does not change product scope, research authority, risk philosophy, human-approval boundaries, credential/security boundaries, stopped-line policy, or production authorization.

## Exact next action

```text
complete this narrow post-merge handoff normalization
-> create a fresh P3.2 branch from then-current main
-> recover exact frozen BRRK-0011 allocation / regime / corrected defensive-scale chain from GitHub
-> implement canonical Target calculation API only
-> add deterministic multi-date research/live golden parity
-> self-review / CI / expected-head merge
```
