# BRRK-CRYPTO-CARRY-ATLAS-0072 — DESIGN

Status: `STAGE_2_DESIGN / NO_CONTROLLED_HISTORY_READ`

Research ID: `BRRK-CRYPTO-CARRY-ATLAS-0072`

Lifecycle stage: `2/10 DESIGN`

OWNER-FIRST merge: `e1d61eadb8a4564cae2689a718e2eaaa859aa05e`

Program roadmap merge: `169d9adf6531dc099a43541df413fef079322adf`

Post-resolution prerequisite: immutable 0083 closeout `f4abfcabe68fa09f27900aac59228420f8721403`

Production authority: `false`

Signature authority: `false`

Order-submission authority: `false`

Controlled scientific/history reads in DESIGN: `0`

Controlled attempt: `0/1`

## 1. Economic question and falsifiable hypothesis

Question: can a prospectively frozen point-in-time BTC/ETH/SOL carry atlas establish a reproducible structural relationship among perpetual funding, spot-perpetual and dated-futures basis, term structure, cross-venue dispersion, leverage/crowding and future crash-risk states across sufficient assets, venues and regimes before any carry strategy is defined?

Hypothesis: a bounded atlas of the ten OWNER-FIRST variable families will reveal a reproducible, state-dependent carry mechanism. Carry persistence and dispersion should vary with crowding/liquidity/volatility state, while prospectively defined extreme-carry states should contain non-random information about future crash-risk outcomes after the preregistered multiple-testing correction. A valid failure is admissible. No trading profitability is claimed or tested in 0072.

## 2. Exact immutable lineage and scope boundary

0072 is permitted to start because governance resolution #296 replaced the blocked 0071 dependency with immutable 0083 closeout; it did not require an 0083 scientific PASS. The prerequisite is therefore governance eligibility, not evidence that 0083's controller hypothesis succeeded.

Authoritative anchors are:

- program roadmap merge `169d9adf6531dc099a43541df413fef079322adf`;
- 0083 immutable closeout merge `f4abfcabe68fa09f27900aac59228420f8721403`;
- 0072 OWNER-FIRST merge `e1d61eadb8a4564cae2689a718e2eaaa859aa05e`.

0072 does not inherit any 0071 or 0083 scientific result, parameter, signal, model, controller, threshold, cost setting or performance statistic. 0072 is a separate structural derivatives/crowding experiment.

## 3. Data families and point-in-time semantics

The DESIGN permits only these ten OWNER-FIRST families:

1. perpetual funding;
2. spot-perpetual basis;
3. spot-dated-futures annualized basis;
4. term-structure slope/curvature where instrument support permits;
5. cross-venue funding/basis dispersion;
6. open interest and open-interest change;
7. volume/liquidity/spread state;
8. realized volatility;
9. liquidation intensity only if point-in-time qualification succeeds before controlled execution;
10. price-trend or attention proxy only if its exact representation is frozen prospectively before controlled history.

For every source, PREREGISTRATION must distinguish source event time, exchange time, publication/availability time and calculation time where the source exposes them. Every as-of join at decision/state time `t` may use only observations whose availability timestamp is `<= t`. Contract metadata, expiry, multiplier, quote/base units, funding interval and venue eligibility must be evaluated using information effective at `t`, never end-of-sample metadata projected backward.

No network fetch is allowed during the controlled attempt. Exact source identities, blob/SHA identities, extraction transforms, revision treatment and maximum staleness belong to Stage 3 PREREGISTRATION and must be frozen before Stage 4 implementation.

## 4. Universe construction

The initial asset universe is exactly `BTC`, `ETH`, `SOL`.

DESIGN permits multiple venues and instrument types only under prospectively frozen point-in-time availability and data-quality rules. Venue/instrument membership must be determined at each time from contemporaneously available contract/venue metadata. A venue or contract may not enter merely because it survived to the end of the sample. Delisted, expired or migrated instruments remain represented when they were then eligible, subject to the frozen data-quality rules.

Stablecoins, wrapped duplicates and unrelated assets are not atlas targets. They may appear only as mechanically required quote/collateral metadata if PREREGISTRATION defines the treatment without adding a new research target.

Universe expansion beyond BTC/ETH/SOL is forbidden under 0072.

## 5. Allowed structural hypothesis families

0072 may evaluate structural relationships among the ten allowed variable families only. The atlas may characterize:

- level and dispersion of funding/basis;
- persistence, transition and mean reversion;
- cross-asset, cross-venue and regime heterogeneity;
- association of carry extremes with contemporaneous crowding/liquidity/volatility state;
- prospectively defined future crash-risk outcomes after a maturation barrier;
- robustness to leaving out an asset or venue where sufficient support exists.

0072 may not construct trade positions, hedge ratios, leverage rules, portfolio weights, executable carry PnL, Sharpe-based candidate selection or strategy profitability. Those belong to a separately owner-first 0073 only after an immutable 0072 PASS closeout.

## 6. Candidate-budget ceiling

The complete structural family ceiling remains exactly `10`, matching OWNER-FIRST. No eleventh family may be added under this ID.

Within each family, Stage 3 must freeze the exact representations, transformations, thresholds, horizon choices and atlas hypothesis count. Stage 3 may use fewer than the ceiling when a family fails prospective data qualification, but it may not replace a disqualified family with an unregistered alternative family.

Every tested hypothesis/representation that reaches controlled evaluation must be counted for multiple-testing purposes according to the preregistered accounting rule. Post-result hypothesis addition or pruning is forbidden.

## 7. Chronology, maturation and anti-lookahead design

The controlled analysis must be chronological and point-in-time. Stage 3 must freeze the exact study window and any chronological partitions before implementation.

Any outcome defined over a future horizon becomes usable only after the full horizon has matured. Observations near the sample end whose future outcome has not matured cannot be labeled by truncated future information.

Revised-history substitution is forbidden unless Stage 3 prospectively establishes that no point-in-time revision history exists and explicitly classifies the resulting limitation. Forward filling beyond a preregistered maximum staleness is forbidden.

## 8. Calculation order

The frozen implementation must preserve this conceptual order:

1. validate pinned source and contract identities;
2. normalize timestamps, units, multipliers and funding conventions;
3. determine point-in-time venue/instrument eligibility;
4. build synchronized spot reference prices without future venue inclusion;
5. calculate perpetual funding and annualized funding according to contemporaneous venue convention;
6. calculate spot-perpetual and dated-futures annualized basis using information known at `t`;
7. calculate term structure and cross-venue dispersion where supported;
8. construct OI, liquidity, spread, volume, volatility and any prospectively qualified optional states;
9. calculate persistence/transition/mean-reversion/dispersion diagnostics;
10. construct prospectively defined extreme-carry and future crash-risk association tests after maturation;
11. perform preregistered robustness and multiple-testing procedures;
12. persist the complete atlas and full tested-candidate accounting;
13. classify using the frozen terminal gates.

No result-informed reordering is allowed.

## 9. Cost and execution-model boundary

0072 is a structural atlas, not a strategy-producing ID. Therefore trading costs, hedge execution, borrow, collateral opportunity cost, margin reserve, liquidation buffer and portfolio transaction costs cannot become 0072 PASS criteria.

Where data-source or venue mechanics themselves require unit/funding/settlement conventions to measure carry correctly, those conventions are measurement semantics rather than strategy execution economics and must be frozen in Stage 3.

Strategy-level C0/C1/C2 profitability accounting is reserved for 0073. 0072 cannot obtain PASS from hypothetical gross or net carry PnL.

## 10. Metrics and robustness families

Stage 3 may freeze exact metrics only within these DESIGN families:

- level/distribution summaries for funding and basis;
- persistence and transition diagnostics;
- mean-reversion diagnostics;
- cross-venue dispersion;
- term-structure geometry;
- crowding-state association using OI/liquidity/volatility and prospectively qualified optional states;
- extreme-carry versus future crash-risk association;
- asset, venue and regime support/coverage;
- leave-one-asset and leave-one-venue robustness where mathematically supported;
- family-wise or experiment-wise multiple-testing correction;
- serial-dependence-aware uncertainty procedures where mathematically appropriate;
- missingness, staleness and coverage diagnostics.

Raw uncorrected significance or one venue/asset/regime result cannot by itself establish PASS.

## 11. Evidence tier and limitations

The future Stage 8 controlled attempt will use development-history evidence and is not automatically independent out-of-sample proof. DESIGN itself reads zero controlled scientific/history payload and releases no historical performance statistic.

A 0072 PASS means only that the frozen structural carry mechanism reproduced under the preregistered atlas experiment with sufficient support and robustness. It does not prove a profitable carry trade, does not authorize 0073 automatically before 0072 immutable closeout, and confers no production authority.

## 12. Terminal classification vocabulary

Stage 3 must freeze exact numerical gates while preserving this vocabulary:

- `PASS_STRUCTURAL_CARRY_MECHANISM`: valid execution and all preregistered structural/support/robustness/multiple-testing PASS gates succeed;
- `FAIL_NO_ROBUST_STRUCTURAL_CARRY_MECHANISM`: valid execution but one or more required scientific gates fail;
- `INCONCLUSIVE_INSUFFICIENT_SUPPORT`: only for prospectively defined insufficient asset/venue/regime/data support or mathematically undefined inference conditions;
- `INVALID_EXECUTION`: identity, timestamp, lookahead, unit, source, candidate-count, read-count, persistence or other execution-contract drift.

Stage 3 may make the exact strings more specific only if it preserves these meanings and does not create a rescue category.

## 13. Failure and stop conditions

Stop or fail closed when any of the following occurs:

- exact source/contract identity cannot be pinned prospectively;
- point-in-time availability semantics cannot be represented according to the preregistered rule;
- required asset/venue/regime support falls below the later frozen minimum;
- a candidate count exceeds the frozen ceiling/accounting;
- any future information enters a state at `t`;
- controlled input is read before a durable Stage 8 attempt marker;
- any unapproved network access occurs during the controlled attempt;
- a strategy-profitability calculation is introduced into the 0072 decision gate;
- any result-informed source, variable, threshold, horizon, universe or hypothesis substitution is attempted.

An implementation fault discovered before attempt consumption may be corrected only when it is semantics-preserving relative to merged DESIGN and PREREGISTRATION. A scientific contract change requires a new research ID.

## 14. No-drift and authority

This DESIGN does not modify canonical BRRK, 0064-0071, 0083, Phase 6, Phase 7, Phase 8, production configuration, signing or order submission.

`production_authorized=false`

`signature_authorized=false`

`order_submission_authorized=false`

Controlled scientific/history reads remain `0`; attempt remains `0/1`.

## 15. Exact next stage

After this DESIGN merges on an exact-head all-green PR, Stage 3 PREREGISTRATION must freeze the exact source/blob identities, venue/instrument eligibility rules, study window, timestamp transformations, candidate definitions/count, future crash-risk horizons, support minima, formulas, missing/staleness rules, multiple-testing procedure, serial-dependence/bootstrap settings and seeds where used, exact PASS/FAIL/INCONCLUSIVE/INVALID gates, synthetic qualification fixtures, physical read/call accounting and exactly-once result-persistence contract.

No controlled funding/basis/history payload may be read before the lifecycle permits it.