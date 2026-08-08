# P5.4 Fixed Gross-Behavior Candidates — Preregistration

Status: **FROZEN BEFORE P5.4/P5.5 ECONOMIC EVALUATION**  
Contract: `P5.4-FIXED-GROSS-BEHAVIOR-CANDIDATES-V1`  
Base main: `9c630c9b4b22146ffabd8fd3f62b08477f3da0f7`

## Objective

Define a small, fixed family of total-gross-risk responses to the already-frozen P5.3 V2 `MARKET_STATE` vocabulary. P5.4 defines **behavior candidates only**. It does not select a P5.3 profile, does not select a behavior winner, and does not authorize production.

The P5.3 V2 architecture is usable for downstream research, but its signal layer remains unselected and still contains false positives. P5.5 therefore owns joint profile × behavior-map robustness and economic selection.

## Frozen dependencies

- P5.3 V2 architecture: `P5.3-MARKET-STATE-PERMISSION-SEPARATION-V2`;
- P5.3 V2 immutable result commit: `e732b7ebe570236bf43084caecb6ea15f7edecb8`;
- P5.3 V2 immutable summary SHA256: `05d5d68a59c8b13f1122d98ed75d03934defdc9d73c7dd92e038c92fd97d2e52`;
- selected P5.3 profile: none;
- P4.1 defensive scale remains `[0,1]`;
- Phase 4 produced no eligible >1 leverage candidate;
- production gross cap remains `1.0`.

## Frozen MARKET_STATE order

```text
NORMAL_BULL
BTC_LEADERSHIP_MATURING
LATE_BULL_ROTATION
EXHAUSTION_WATCH
DE_RISK_1
DE_RISK_2
FLAT
```

P5.4 does not alter this state path.

## Fixed candidate family

Exactly three maps are frozen before economic evaluation:

| MARKET_STATE | DE_RISK_ONLY | PROGRESSIVE | EARLY_DEFENSIVE |
| --- | ---: | ---: | ---: |
| NORMAL_BULL | 1.00 | 1.00 | 1.00 |
| BTC_LEADERSHIP_MATURING | 1.00 | 1.00 | 0.95 |
| LATE_BULL_ROTATION | 1.00 | 0.95 | 0.90 |
| EXHAUSTION_WATCH | 1.00 | 0.80 | 0.70 |
| DE_RISK_1 | 0.65 | 0.55 | 0.45 |
| DE_RISK_2 | 0.30 | 0.25 | 0.20 |
| FLAT | 0.00 | 0.00 | 0.00 |

### DE_RISK_ONLY

Delayed-intervention comparator. It leaves upstream gross unchanged through maturity, rotation and exhaustion and only cuts gross after explicit `DE_RISK_1` / `DE_RISK_2` states.

### PROGRESSIVE

Moderate cycle overlay. It preserves essentially full late-bull participation but begins reducing total risk in rotation/exhaustion before explicit de-risk states.

### EARLY_DEFENSIVE

Earlier defensive sensitivity case. It starts a small reduction at maturity and continues progressively while still retaining meaningful exposure through late-bull rotation.

These are not optimized values. They are a deliberately coarse policy family for P5.5 to stress and reject/accept as a group or individually.

## Why only three maps

A dense or continuous multiplier search would allow the economic backtest to become an implicit optimizer over the same small event set. That is forbidden.

The frozen downstream candidate set is:

```text
3 P5.3 profiles
x
3 P5.4 behavior maps
=
9 joint candidates
```

P5.5 evaluates all nine. P5.4 may not add a fourth map after seeing economic results.

## Composition rule

P5.4 is a total-risk overlay **after** the frozen upstream BRRK/P4.1 target:

```text
P5.4 asset target
= frozen upstream P4.1/BRRK asset target
x cycle gross multiplier(MARKET_STATE)
```

Therefore:

```text
P5.4 target gross
= frozen upstream P4.1 target gross
x cycle gross multiplier(MARKET_STATE)
```

Consequences:

- P5.4 can only preserve or reduce upstream gross;
- no P5.4 multiplier may exceed `1.0`;
- relative BTC/ETH/SOL/BNB ranking is unchanged;
- no short exposure is added;
- freed risk goes to cash/stablecoin;
- P4.1 remains upstream and unchanged.

## Structural behavior rules

Every map must satisfy:

- values in `[0,1]`;
- `NORMAL_BULL = 1.0`;
- monotone non-increasing multiplier with increasing state severity;
- `FLAT = 0.0`;
- `LATE_BULL_ROTATION > 0`;
- no asset-specific multipliers;
- no profile-specific map parameters;
- no intraday P5.4 risk addition.

## DATA_INSUFFICIENT

`DATA_INSUFFICIENT` is not a MARKET_STATE and P5.4 defines no multiplier for it.

P5.5 matched economic comparisons begin on the common P5.3 initialization date:

```text
2021-01-17
```

This prevents an arbitrary pre-initialization cycle multiplier from affecting candidate ranking.

## FLAT and operational permission

All P5.4 maps set `FLAT = 0`, but research market-state recovery and live re-risk authority remain separate.

If an actual integrated system reaches zero directional exposure, operational state must become/remain:

```text
LOCKED_PENDING_HUMAN_APPROVAL
```

A later MARKET_STATE improvement has zero authority to clear that lock.

For P5.5 research economics, a historical 0 -> positive target after MARKET_STATE recovery may be computed only as:

```text
RESEARCH_HYPOTHETICAL_REENTRY
```

This is needed to measure signal/mapping economics across the historical sample. It is not a production permission and cannot be reused as live execution authority.

## P5.5 handoff

P5.5 owns selection and must evaluate all nine frozen profile/map combinations against a baseline without the cycle overlay.

Required dimensions include:

- leave-one-event-out or comparable event-held-out robustness;
- lead/lag distribution;
- false-positive duration;
- missed upside;
- drawdown avoided;
- terminal wealth and CAGR impact;
- turnover and explicit cost sensitivity;
- second-wind preservation;
- 2021 terminal bear-transition behavior;
- non-top controls including the `2021-02-23` false FLAT;
- no single-event dependency;
- nearby-policy/broad-region robustness rather than a knife-edge winner.

If no joint candidate is robust, P5.5 must fail-stop rather than force a selection.

## Forbidden

- selecting a P5.3 profile in P5.4;
- selecting a P5.4 winner before P5.5;
- adding a fourth map after seeing economics;
- dense/continuous multiplier optimization;
- modifying P5.3 V2 MARKET_STATE history;
- changing BRRK relative ranking;
- any multiplier above 1.0;
- treating late-bull rotation as automatic zero exposure;
- automatic live re-entry after FLAT;
- adding shorts;
- production authorization.

## Completion boundary

P5.4 preregistration is complete when the machine contract, tests, CI and handoff are green and merged **before economic evaluation**.

After merge, implement deterministic mapping mechanics only. Do not run P5.5 economics until the mapping implementation reproduces this contract exactly.
