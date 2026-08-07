# BRRK Next Steps

Last updated: 2026-08-07

## Current instruction

**P4.5 is now a formal no-promotion closeout for LEVERAGE-0040. Do not retune LEVERAGE-0040 after observing the immutable result.**

The next leverage research, if pursued, must be a new preregistered experiment focused on leverage implementation architecture and the safely sustainable CAGR-maximizing sweet spot.

## Immediate state

```text
main                                  3690f64a6179a759a60d9759c214d59cf604869e
PR #90                                OPEN / DRAFT
LEVERAGE-0040                         COMPLETE / IMMUTABLE RESULT
result commit                         bd256e77a9800556e97769858fbb3ba5054c4389
summary SHA256                        3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0
selection                             NO_PROMOTION
selected research cap                 NONE
selected operating DD budget          NONE
P4.5                                  FAIL_STOP / COMPLETE
P4.6 production authorization         BLOCKED / no eligible candidate
production gross cap                  1.0
production_authorized_components      []
```

## P4.5 decision

The frozen P4.5 selection rule explicitly forbids choosing leverage from the highest in-sample CAGR alone.

LEVERAGE-0040 produced higher historical CAGR as cap increased, but no >1 candidate passed all mandatory hard gates. Therefore:

```text
LEVERAGE-0040 = FAIL_STOP / NO_PROMOTION
1.10 = not selected
1.20 = not selected
1.30 = not selected
production gross cap = 1.0
P4.6 = blocked
```

This is an immutable research decision, not a statement that 1.20 is economically uninteresting.

## Work allowed now

### 1. Close PR #90 post-result evidence

On the final user-authored P4.5 documentation head:

- validate the committed immutable result/digest/provenance;
- rerun applicable Phase 0 / research normalization / P3.2 parity+golden / P4 cap1 parity / P4 prerequisites / P4.4 contract / governance checks;
- confirm `production_authorized_components = []`;
- confirm no immutable result file was changed by P4.5 documentation;
- perform final diff/drift review.

A merge of PR #90, if separately approved after green final-head evidence, is **research-evidence integration only**. It does not authorize production leverage.

### 2. Preserve LEVERAGE-0040 as closed

Do not:

- rerun it;
- change its hard gates;
- change its cap grid;
- reinterpret 1.20 as a pass;
- alter funding/liquidation/gap assumptions to rescue the observed result;
- reuse the experiment ID.

Any material follow-on hypothesis requires a new experiment ID.

## Next independent leverage research direction

The owner has accepted the following planning objective:

> Find the leverage sweet spot that maximizes expected long-run compounded wealth while keeping survival, tail risk, funding, liquidation and implementation risk within explicit preregistered limits.

### Why 1.20 matters

LEVERAGE-0040 showed, at 5 bps cost:

```text
1.00  CAGR 65.31%  MDD -33.53%  Sharpe 1.3561
1.20  CAGR 78.51%  MDD -39.63%  Sharpe 1.3550
```

Therefore **1.20 is an important focal design point for the next architecture study**. It is not a selected or authorized cap.

### What the next study should actually test

The next experiment should not merely repeat `1.00/1.10/1.20/1.30` under relaxed gates. It should test whether a better implementation architecture can safely realize the attractive economic exposure.

Before the next run, preregister at least:

- how base long exposure is split between verified spot and perp;
- whether only incremental exposure above 1.0 is implemented with perp;
- required collateral / margin reserve;
- liquidation-distance calculation mapped to the actual Hyperliquid account architecture;
- funding-aware deleveraging or cap reduction rules;
- synthetic-gap and stressed-volatility survival rules;
- degraded execution/capacity assumptions;
- operating drawdown candidate budgets;
- an exact candidate-cap neighborhood around the focal region;
- broad-region / neighboring-parameter robustness criteria;
- fixed seeds and result-selection rule.

The exact candidate grid is **not frozen yet**. Do not pick it after observing the next experiment.

## Objective hierarchy

The project objective remains:

```text
maximize expected long-run compounded wealth
```

subject to:

1. survival / no unacceptable ruin or liquidation path;
2. catastrophic drawdown boundary;
3. explicit operating drawdown budget;
4. funding/cost-aware economics;
5. implementation realism;
6. parameter-region robustness rather than a knife-edge winner.

Risk is a constraint, not an objective to minimize. CAGR is the objective, but not at the cost of failing the preregistered survival constraints.

## P4.6 boundary

P4.6 remains blocked because LEVERAGE-0040 selected no research cap.

Do not authorize production gross >1 from the current result.

If a future separately preregistered leverage study selects an eligible research candidate, P4.6 remains a separate production decision requiring explicit authorization and live/shadow evidence.

## Downstream roadmap

```text
P4.5 formal no-promotion closeout
-> final-head post-result validation / research-evidence merge decision
-> new preregistered leverage-architecture sweet-spot experiment
-> P4.6 only if that new research produces an eligible candidate
-> Phase 5 cycle-top / exit intelligence after the leverage dependency is properly resolved
```

Do not jump directly into P5 merely because LEVERAGE-0040 failed. The leverage objective remains unresolved: the current experiment rejected its implementation architecture, while the next accepted hypothesis is to test a safer architecture around the economically attractive focal region.
