# 0083 SOL Long-Sideways Controller Integration Replacement — DESIGN

Research ID: `BRRK-SOL-LONG-SIDEWAYS-CONTROLLER-INTEGRATION-REPLACEMENT-0083`

Status: `DESIGN / NOT PREREGISTERED / NOT IMPLEMENTED / NOT RUN`

## Purpose
0083 independently tests whether the locked 0070 P02 SOL `T4_LONG_SIDEWAYS` warning at exactly 10 sessions provides incremental economic risk-control value when translated into a bounded SOL long-or-cash controller under prospectively frozen costs and robustness tests.

0083 is the governance-authorized replacement for permanently blocked 0071. It is not a 0071 rerun and inherits no completed formal lifecycle stage. The accidental 0071 preflight content exposure has zero authority over 0083 scientific choices.

It does not reopen predictive discovery. P02 cannot be retrained, reselected, recalibrated or rescreened. P03/P08 cannot enter controller construction. The universe is SOL only, exposure is bounded to `[0,1]`, and leverage and shorting are excluded.

## Immutable lineage
Required upstream anchors are closed 0064, 0069 and 0070, permanently blocked 0071, and merged governance resolution PR #296. The 0070 immutable result merge is `174a30dc4950e7351f3a746edc8f581b8f12e6d3`, closeout merge is `d87607070cf03ccbbc318065f8c4c14ec6c6a50b`. The 0083 OWNER-FIRST merge is `dd9f3f28aabfdf6c05dcb9ca5a3dd13ca36a2467`. Governance replacement authority is merge `b58960ee3bc9e5cc5976d889cc28026614525686`.

Locked predictive input is `P02_RAW_ELASTIC_NET_LOGIT|SOL|T4_LONG_SIDEWAYS`, lead exactly 10 sessions. Closed reference anchors are PR-AUC `0.7974030713822858`, prevalence `0.45544554455445546`, PR-AUC lift `0.34195752682783037`, ROC-AUC `0.7913043478260869`, and 0070 median LOEO PR-lift retention `0.9823275624` with retention >=0.50 in `7/7` folds. These are immutable closed-lineage anchors, not new 0083 evidence.

The complete scientific question, target, mechanism and candidate ceiling are mechanically preserved from frozen 0071. No information observed during the accidental 0071 preflight exposure may be used to add, delete, reprioritize, retune or rescue an 0083 candidate, threshold, cost, benchmark or gate.

## Six selectable controller families
The complete selectable ceiling is exactly six families:
1. `BINARY_RISK_OFF`.
2. `LINEAR_DERISK`.
3. `PIECEWISE_DERISK`.
4. `VOL_ADJUSTED`.
5. `DRAWDOWN_AWARE`.
6. `HYSTERESIS`.

Exact thresholds, exposure levels, volatility settings, drawdown settings and hysteresis parameters must be frozen only in PREREGISTRATION before implementation or controlled reads. No seventh family or post-result rescue variant is allowed.

`VOL_ADJUSTED` requires a matched signal-off volatility-only comparator. `DRAWDOWN_AWARE` requires a matched signal-off drawdown-only comparator. These are attribution diagnostics, not selectable candidates. Any P02 claim for those families must show incremental value over the matched comparator.

## Causal exposure and cash accounting
Information available through session `t` close may affect only the exposure applied to return `t -> t+1`. Future returns, future event labels, future rates or future risk state cannot enter a decision.

The uninvested fraction uses frozen 0064 passive-cash semantics. PREREGISTRATION must pin cash-engine blob `4060a307be2204c11952cb52e2fc718a5343d8e1`, DTB3 blob `71d50e26f8a9afb6bcb88401d20b97d5fb0a891a`, and DTB3 payload SHA256 `4d8aee67dbd528ce38ff8482e9bb02dd5ccf2c6cd461f606fe90007151ab6879`. Cash uses causal DTB3 alignment, 50% yield realization and a 100 bps annual continuous idle-cash spread/fee. Zero-return cash substitution is forbidden.

## Ordered economic computation
The controlled implementation must preserve this order:
1. verify frozen identities;
2. reconstruct the frozen P02 score without retraining or reselection;
3. align SOL returns, P02 timestamps and permitted lagged state;
4. compute session-`t` decision state;
5. convert state to target SOL exposure in `[0,1]`;
6. lag exposure so it first applies to `t -> t+1` return;
7. compute idle cash and causal cash accrual;
8. compute turnover;
9. apply C0/C1/C2 costs;
10. compute net daily returns and NAV;
11. compute economic, tail, turnover, cost and concentration metrics;
12. run preregistered robustness and multiple-testing controls;
13. apply frozen Pareto/non-inferiority logic;
14. persist complete candidate/comparator accounting before terminal classification.

## Cost and metric framework
Three mandatory cost states are `C0_THEORETICAL`, `C1_REALISTIC` and `C2_STRESSED`. C0 is diagnostic and cannot establish PASS. Exact fee, slippage, turnover-cost and stress assumptions must be frozen in PREREGISTRATION.

Required metric families include return/NAV, CAGR, annualized volatility, Sharpe, Sortino, maximum drawdown, Calmar, downside deviation, worst 1/5/10/20-session loss, average exposure, time in cash, turnover, switch count, cost drag, cost break-even, bull participation, bear protection, sideways performance, recovery time where defined, and profit/loss concentration by time block and extreme observations.

## Robustness and selection
PREREGISTRATION must freeze identity/reproduction tolerances, C1/C2 cost sensitivity, deterministic candidate/trial accounting, block bootstrap settings, DSR treatment, PBO or a prospectively defined unsupported rule, concentration-removal tests, matched-overlay attribution gates and exact PASS/FAIL/INCONCLUSIVE/INVALID thresholds.

Selection must use a fixed net Pareto/non-inferiority rule spanning return retention, drawdown/tail improvement, turnover/cost burden, concentration robustness, multiple-testing correction and matched-overlay attribution where required. Observed Sharpe maximization is forbidden.

Selectable candidate budget is exactly six. Every evaluated candidate must remain in immutable accounting regardless of outcome.

## Evidence tier and classification
Evidence tier remains `RESEARCHER_EXPOSED_DEVELOPMENT_NOT_INDEPENDENT_OOS`.

Terminal meanings are PASS for valid execution with at least one fixed candidate passing all preregistered primary economic, robustness, concentration, attribution and multiple-testing gates under C1 and required C2 stress; FAIL for valid execution with sufficient support but no passing candidate; INCONCLUSIVE only for prospectively defined insufficient-support or mathematically undefined states; and INVALID_EXECUTION for identity, causal timing, candidate count, read count, cash/cost accounting, persistence or exactly-once contract breach.

## Lifecycle and stop rules
Lifecycle is exactly `OWNER-FIRST -> DESIGN -> PREREGISTRATION -> IMPLEMENTATION -> NONHISTORICAL QUALIFICATION -> CONTROLLED BOUNDARY -> ZERO-RESULT PREFLIGHT -> ONE CONTROLLED DEVELOPMENT-HISTORY ATTEMPT -> RESULT -> IMMUTABLE CLOSEOUT`.

No formal stage is inherited from 0071. The unique 0083 controlled attempt may occur only after every preceding 0083 stage has merged and exact merged-boundary zero-result preflight passes with attempt `0/1`, 0083 controlled reads zero and no result artifacts. A durable 0083 attempt marker must precede the first 0083 controlled content read. After attempt creation, no same-ID rerun, retune or rescue is permitted.

Fail closed on frozen identity mismatch, lookahead, exposure outside `[0,1]`, cash-rule drift, candidate-count drift, unregistered variants, excessive controlled reads, network data substitution or result-persistence drift.

At every stage production, signature and order authority remain false; Canonical BRRK-0011 and Phase 6 remain unchanged.

## Exact next stage
After exact-head standing CI passes and DESIGN merges, create a separate comprehensive PREREGISTRATION that mechanically reproduces the frozen 0071 numerical/data/analysis contract for 0083, with no result-informed change. It must freeze exact controller parameters, benchmark/calendar alignment, costs, volatility/drawdown rules, turnover, metric formulas, bootstrap/DSR/PBO settings and seeds, concentration tests, attribution gates, classification thresholds, source identities/read budgets and exactly-once persistence rules before implementation or any 0083 controlled historical/economic read.
