# BRRK Current State

Last updated: 2026-08-09  
Handoff PR: **#148**  
Handoff branch: `dashboard/pro-fund-terminal-v5`  
Authoritative baseline main at branch creation: `1cc9f6fc5cdea10437613b5248feb66aaeeb8e26`  
Latest merged dashboard PR at branch creation: **#147**

Status: **authoritative current-state handoff candidate**

## Executive state

```text
Phase 0-3                         COMPLETE / MERGED
Phase 4 leverage research         FAIL_STOP / NO_PROMOTION
P5.5                              COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP
F27 idle-cash measurement         R2 AUTHORITATIVE / R1 SUPERSEDED-PRESERVED
F7 metrics convergence            PARTIAL
Idle Cash execution feasibility   NOT_FEASIBLE_ON_HYPERLIQUID_STANDARD / FUTURE_OPTION_ONLY
Phase 6 implementation/replay     PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY
Phase 6 identity                  VERIFIED / FROZEN / STANDARD-DISABLED
Phase 6 pre-arm dependencies      4/4
Phase 6 ARM                       MERGED #143 / ACTIVE FUTURE-ONLY OBSERVATION
Phase 6 ARM marker                cbd58adb05187651ca72d67900a0ccbbd3e83b1e
Phase 6 daily schedule            00:00 UTC
Phase 6 live elapsed evidence     MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
Program timeline dashboard        READ-ONLY V5 / PROFESSIONAL FUND TERMINAL UI CANDIDATE
Phase 7                           MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                           TRIGGER ABSENT / NOT RUN
Production                        NO_CHANGE
```

## Phase 6 active observation state

The durable prospective ARM marker remains:

```text
cbd58adb05187651ca72d67900a0ccbbd3e83b1e
```

The authoritative live-observation gate remains:

```text
status                             ARMED_FUTURE_ONLY_OBSERVATION_ACTIVE
collector_armed                    true
schedule_configured                true
elapsed_evidence_credit_authorized true
daily schedule                     0 0 * * *  (UTC)
production_authorized              false
signature_authorized               false
order_submission_authorized        false
```

The evidence backend remains `ARMED_COLLECTING_FUTURE_ONLY`. Genuine scheduled credit still requires a real future `schedule` event plus its create-only evidence artifact and separate hash-bound receipt artifact. Historical replay, pull-request preflight, rerun, duplicate decision timestamps and manual dispatch do not create scheduled-decision credit.

First theoretical eligible canonical timestamp remains `2026-08-10T00:00:00Z`. Frozen acceptance remains:

```text
minimum elapsed calendar days       14
minimum genuine scheduled decisions 10
minimum emergency drills             1
critical reconciliation errors       0
unexplained target drift              0
schedule failures                     0
```

A separately evidenced manual emergency drill remains required and never counts as a scheduled decision.

## Program Timeline Dashboard V5 — candidate

V4 merged in PR #147 at baseline main:

```text
1cc9f6fc5cdea10437613b5248feb66aaeeb8e26
```

V5 remains under:

```text
research/governance/dashboard/
```

and is downstream of authoritative evidence.

### Historical source-of-record inputs

```text
research/results/pit_disp_0015/daily_equity.csv
research/results/pit_disp_0015/daily_weights.csv
research/results/funding_pnl_0003/full_window_daily_equity.csv
config/research_registry.json
config/decision_registry.json
```

The canonical chart window begins `2022-12-10` and currently extends through `2026-07-31`. No exact four-year claim is made.

### V5 presentation and range statistics

V5 preserves the V3 calculations and V4 Chinese simplification, while reorganizing presentation into an investment-committee hierarchy: navy executive header, sticky section navigation, professional chart palette, tabular numerals, compact selected-range summary, and restrained white analytical cards. For the user-selected range it recomputes only from the selected existing equity column:

- cumulative return;
- positive-return-day ratio;
- daily payoff ratio;
- maximum drawdown;
- adjacent target-vector change-day count;
- summed adjacent target-vector L1 change.

Positive-return-day ratio is explicitly not called holding-cycle win rate. Actual rebalance count, executed turnover and holding-cycle win rate remain unavailable unless an authoritative executed-turnover path is present.

### V5 P3.2 timing boundary

The reviewed canonical runtime implementation freezes:

```text
decision D 00:00 UTC
consumes exactly completed D-1 UTC daily session
target row D-1 is intended for D return
```

V5 therefore separates target session, mapped decision timestamp, data cutoff and target holding-return date. It also states that historical NAV row `t` uses the prior target for row-`t` return, rather than falsely pairing row-`t` target with row-`t` return as a cause.

### V5 P3.3 controller boundary

The reviewed canonical P3.3 controller freezes:

```text
control_version  P3.3-L1-BAND-V1
gap metric       L1_ABSOLUTE_WEIGHT_GAP
rebalance band   0.05
boundary         REBALANCE_WHEN_L1_GAP_GTE_BAND
```

The actual controller gap compares the current account position weights with the P3.2 model target. Safety overrides bypass the band when the current account has short exposure or current gross above 1.

The existing `pit_disp_0015` historical result directory does not persist daily:

```text
current_position_weights
l1_target_gap
control_turnover_weight
P3.3 control plans
```

Therefore V5 does not infer historical actual `HOLD` / `REBALANCE` events from adjacent target rows. The charted adjacent-target L1 series is separately labelled as a target-vector change metric, and the 5% line is controller-rule reference only.

### V5 P3.2 signal / regime boundary

The reviewed canonical target implementation proves model structure including:

```text
btc_trend < 0 -> BTC-only V1 branch
ETH/SOL eligibility -> score > 0 AND asset trend > 0 AND ratio trend > 0
BNB eligibility -> score > 0 AND slow BNB trend > 0 AND slow BNB/BTC trend > 0
semantic states -> RISK_OFF / BTC_LEAD / MAJOR_ROTATION / ALT_EXPANSION
long-only gross -> <= 1
XRP -> feature-only
```

P3.2 target results can contain `risk_state`, state probabilities, `riskoff_probability`, `meta_scale`, `defensive_scale` and feature snapshots. Those daily snapshots are not persisted in the frozen `pit_disp_0015` historical result directory. V5 therefore does not reverse-engineer a 2023 signal/regime from target weights or NAV.

Frozen V5 source semantics:

```text
dashboard_version=v5-pro-fund-terminal
dashboard_record_authoritative=false
scheduled_decision_credit_created=false
production_authorized=false
target_change_mechanics_authoritative_from_canonical_weights=true
p3_3_rule_authoritative_from_controller=true
historical_p3_3_execution_state_available=false
historical_signal_snapshot_available=false
execution_causality_asserted=false
```

The economic layers remain:

```text
historical backtest NAV
!= Phase-6 hypothetical shadow PnL
!= future real-account PnL
```

### Public deployment

Canonical public entry supplied and verified by the owner:

```text
https://laugh-to-2028.vercel.app/
```

V5 deployment is not considered complete by this handoff until the merged public URL is independently observed serving the unique `v5-pro-fund-terminal` marker.

## Canonical production / security authority

```text
directional core                  BRRK-0011
long universe                     BTC / ETH / SOL / BNB
XRP                               feature-only
primary venue                     Hyperliquid
decision boundary                 00:00 UTC
BNB route policy                  PERP_ONLY_DEFAULT
production gross cap              1.0
production_authorized_components = []
production_authorized             false
signature_authorized              false
order_submission_authorized       false
first real short authority        NONE
```

V5 changes none of these fields and adds no signer, private key, order submission, withdrawal, transfer, or production capability.

## Other frozen decisions

- F27 R2 remains authoritative; R1 remains superseded-preserved.
- F7 remains `PARTIAL`; immutable studies are not rewritten.
- LEVERAGE-0040 remains `FAIL_STOP / NO_PROMOTION`.
- Idle Cash remains `NOT_FEASIBLE_ON_HYPERLIQUID_STANDARD / FUTURE_OPTION / NOT_AUTHORIZED`.
- Future new Research IDs capable of lowering canonical BRRK gross remain subject to the frozen right-tail gate.

## Current drift assessment

`DRIFT_0`.

This V5 candidate changes only dashboard HTML/documentation/tests and this handoff. The visible page is reorganized into a professional fund-dashboard hierarchy with a dark executive header, sticky Chinese navigation, compact investment-committee summary, tabular numerals and fixed chart colors; advanced technical/governance material remains collapsed by default. It does not modify `execution/**`, `config/**`, `research/results/**`, strategy mathematics, Phase-6 scheduling, immutable economic evidence, or execution authority.

## Exact next task

1. Require governance/no-drift/dashboard CI to be green.
2. Merge PR #148 only if the final diff remains dashboard/docs/tests only.
3. Verify `https://laugh-to-2028.vercel.app/` serves `v5-pro-fund-terminal`.
4. Continue Phase-6 future-only evidence accumulation independently of dashboard presentation.
