# BRRK Next Steps

Last updated: 2026-08-07

## Current instruction

**P5.1 is merged/frozen. P5.2 Feature Families are now implemented and frozen before the first feature-evidence run. Run the blinded P5.2 preflight; if green, execute the already-authorized one-time feature-evidence study without changing P5.1 events or P5.2 feature definitions.**

## Immediate state

```text
Phase 0-3                              COMPLETE / MERGED
LEVERAGE-0039                          STOPPED PRE-RUN / NO RESULT
LEVERAGE-0040                          COMPLETE / IMMUTABLE / NO_PROMOTION
LEVERAGE-0041                          COMPLETE / IMMUTABLE / NO_PROMOTION
P4.6 production leverage               NOT ENTERED / BLOCKED BY NO CANDIDATE
production gross cap                   1.0
production_authorized_components       []
P5.1 event taxonomy                    COMPLETE / MERGED / FROZEN
P5.1 contract                          P5.1-EVENT-TAXONOMY-V1
P5.2 feature families                  IMPLEMENTED / FROZEN / RESULT NOT RUN
P5.2 contract                          P5.2-FEATURE-FAMILIES-V1
next execution                         P5.2 BLINDED PREFLIGHT -> RUN_ONCE
```

## P5.1 — immutable research taxonomy

P5.1 freezes the required 2021/2025 events, anchor mechanics, relative evaluation buckets and multiple non-top high-volatility controls before feature scoring.

Only 2021 November is explicitly terminal in V1. The 2025 sequence remains differentiated as temporary new high / second wind / deleveraging / deterioration.

P5.2 may not move those windows or anchors based on feature results.

## P5.2 — frozen feature evidence

Contract:

`P5.2-FEATURE-FAMILIES-V1`

P5.2 is not the state model. It produces causal descriptive evidence under the frozen taxonomy.

### Available feature families

#### BTC trend maturity

- 20d / 40d log return;
- 20d / 40d annualized log-price slopes;
- KAMA(10,2,30) gap and 10d slope;
- distance from trailing 90d high;
- duration within 5% of trailing 90d high;
- RV20 and RV20/RV60.

#### Momentum exhaustion

- daily Wilder RSI14 / RSI28;
- completed-4h Wilder RSI14 / RSI28 sampled at daily 00:00 UTC;
- 20d price-versus-RSI percentile-rank divergence;
- RSI14 extreme persistence;
- failure from trailing RSI14 maximum.

Daily versus 4h RSI is evaluated under the same framework; neither is preselected visually.

#### Leadership migration

- ETH/BTC, SOL/BTC, BNB/BTC 20d / 40d relative returns;
- BTC/ETH/SOL/BNB cross-sectional 20d return dispersion.

#### Breadth

- ETH/SOL/BNB outperformance breadth versus BTC;
- canonical-five ETH/SOL/BNB/XRP breadth versus BTC;
- SOL/BNB high-beta participation;
- breadth acceleration;
- contraction from recent breadth maximum.

### Explicitly pending data authorities

Do not fabricate substitutes for:

- BTC dominance;
- broad-market breadth;
- 2021/2025-comparable funding history;
- historical OI;
- fixed historical basis/premium panel;
- liquidation proxy.

They remain `DATA_SOURCE_PENDING` and must appear as such in P5.2 output.

### Fixed data window

```text
2020-10-01 -> 2026-02-28
```

The 2026 extension exists only to cover the frozen +90-day post-event evaluation horizon for late-2025 events. It was fixed before the first evidence run.

### Evidence output

For each event × P5.1 bucket × feature:

- count / mean / median / min / max;
- first / last / delta;
- pooled non-top-control median and MAD;
- signed robust-z versus controls when defined.

All `AVAILABLE_V1` features require >=95% nonmissing coverage across required evaluation rows.

P5.2 explicitly does **not** select:

```text
final feature set
P5.3 thresholds
P5.3 state machine parameters
production behavior
```

## Research execution rule

Standing research authorization already covers the one-time P5.2 evidence run after pre-run gates are green.

Therefore do not stop for another owner prompt at RUN_ONCE.

Allowed post-trigger correction is limited to audited non-economic implementation defects. After any feature evidence is observed, do not change:

- P5.1 event windows/anchors;
- P5.2 feature definitions/lookbacks;
- evidence buckets/statistics;
- coverage threshold.

A material economic/research-definition change requires a new governed research ID/version.

## After P5.2

P5.3 may start only after P5.2 evidence is immutable and reviewable.

Target future state vocabulary remains:

```text
NORMAL_BULL
BTC_LEADERSHIP_MATURING
LATE_BULL_ROTATION
EXHAUSTION_WATCH
DE_RISK_1
DE_RISK_2
FLAT
```

P5.3 must use feature evidence rather than retrospectively modifying P5.1/P5.2 to make a preferred state rule work.

## Downstream

- P5.4 behavior semantics after P5.3;
- P5.5 event-level / leave-one-event-out validation;
- P5.6 integration with BRRK as a total-risk layer only;
- Phase 6 integrated shadow with zero trading authority;
- Phase 7 limited-capital live only after shadow acceptance + explicit production approval;
- Phase 8 bear-short research later; first short remains human-gated.

## Exact next step

```text
OPEN / VALIDATE P5.2 PRE-RESULT PR
RUN P5.2 CONTRACT TESTS + BLINDED BINANCE DATA PREFLIGHT
IF GREEN, COMMIT RUN_ONCE_P5_2_FEATURE_EVIDENCE.marker
EXECUTE ONE-TIME FROZEN FEATURE-EVIDENCE RUN
VALIDATE + COMMIT IMMUTABLE P5.2 RESULTS
UPDATE README / CURRENT_STATE / NEXT_STEPS FROM THE OBSERVED RESULT
DO NOT START P5.3 BEFORE P5.2 CLOSEOUT IS MERGED
```