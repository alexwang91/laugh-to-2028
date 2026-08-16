# 0070 SOL Long-Sideways Early-Warning Episode-Robustness DESIGN

Research ID: `BRRK-SOL-LONG-SIDEWAYS-EARLY-WARNING-EPISODE-ROBUSTNESS-0070`

## Purpose
0070 is a deliberately narrow successor to immutably closed 0069. It does **not** reopen discovery, retune 0069, repair the unavailable controller path, or claim independent OOS evidence. It asks one falsifiable robustness question raised by the closed result: is the strongest 0069 finding—SOL `T4_LONG_SIDEWAYS` at a 10-session warning lead—robust to removal of each independent final event onset, or is the apparent edge dominated by one episode?

0069 is used only as hypothesis-generating, researcher-exposed DEVELOPMENT evidence. The 0070 research ID and its robustness rule are fixed before any 0070 controlled historical/evidence read.

## Frozen signal
Primary confirmatory track:
- asset: `SOL`
- target: `T4_LONG_SIDEWAYS`
- warning lead: exactly `10` sessions
- architecture: `P02_RAW_ELASTIC_NET_LOGIT`
- source scientific semantics: immutable 0067 event/label/feature/model definitions as inherited by 0069
- source execution result: immutable 0069 historical bundle

Corroborative cluster:
- `P03_VALIDATION_SCREENED_SIGNAL_LOGIT|SOL|T4_LONG_SIDEWAYS`
- `P08_STACKED_PROBABILITY_ENSEMBLE|SOL|T4_LONG_SIDEWAYS`

P03 and P08 are explicitly treated as **one dependent corroborative cluster**, because their 0069 final metrics/predictions can be highly overlapping. They may not be counted as two independent replications.

No BTC target, DOWN target, alternate sideways target, alternate warning lead, alternate architecture, new feature family, new atlas screen, threshold search, hyperparameter search, or result-informed fallback is permitted.

## Frozen 0069 reference values
The preregistration will pin exact immutable blobs and numerical references. The primary 0069 P02 reference is:
- final PR-AUC = `0.7974030713822858`
- final prevalence = `0.45544554455445546`
- final PR-AUC lift = `0.34195752682783037`
- final ROC-AUC = `0.7913043478260869`
- preferred warning horizon = `10`
- final unique onsets = `7`
- train+validation unique onsets = `15`

P03/P08 closed-reference PR-AUC lift = `0.28384632505003554` and ROC-AUC = `0.8027667984189722`.

These closed values are allowed only as frozen reference anchors for a new-ID robustness test; they are not new evidence.

## Episode-jackknife estimand
The controlled implementation must reconstruct the exact frozen SOL/T4/10 final prediction series for P02, P03 and P08 using only preregistered immutable 0069 identities. Before any robustness inference, reconstructed full-window aggregate metrics must reproduce the immutable 0069 references within the preregistered numerical tolerance; otherwise 0070 is `INVALID_EXECUTION`.

For every eligible final prediction row with positive `Y_10`, assign that row to the earliest qualifying unique SOL `T4_LONG_SIDEWAYS` onset in the strictly future interval `(t, t+10]`. Assignment is deterministic; ties use chronological order. The expected final unique-onset count is frozen to 7 from closed 0069.

Create seven leave-one-unique-onset-out (LOEO) folds. Fold `i` removes every positive warning row assigned to onset `i`; all other eligible rows remain unchanged. There is no retraining, reorientation, rescreening, recalibration or threshold change inside a fold. Recompute ROC-AUC, PR-AUC, prevalence and PR-AUC lift on the remaining rows.

For the primary P02 track define `retention_i = LOEO_PR_AUC_LIFT_i / frozen_0069_PR_AUC_LIFT`.

## Prospective PASS rule
A scientific PASS requires all of the following after valid execution:
1. Exact frozen-identity/full-window reproduction passes before jackknife inference.
2. Exactly 7 final unique onsets are present and all seven required LOEO folds are mathematically defined.
3. P02 has `PR_AUC_LIFT > 0` and `ROC_AUC > 0.50` in every LOEO fold.
4. P02 median retention across the seven folds is `>= 0.75`.
5. At least 6 of 7 P02 folds have retention `>= 0.50`.
6. At least one member of the dependent P03/P08 corroborative cluster has positive PR-AUC lift in every defined LOEO fold and median retention `>= 0.50` relative to its own frozen 0069 lift.

The classification enum will be frozen as:
- `PASS_LOCKED_EPISODE_ROBUSTNESS_REPLICATION`
- `FAIL_LOCKED_EPISODE_ROBUSTNESS_REPLICATION`
- `MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_EPISODE_SUPPORT`
- `INVALID_EXECUTION`

No threshold may be weakened after seeing 0070 evidence.

## Evidence tier and data boundary
0070 remains `RESEARCHER_EXPOSED_DEVELOPMENT_NOT_INDEPENDENT_OOS`. The available raw market history ends at 2026-08-02 and the frozen T4 event definition can require up to 240 future sessions for label maturity, so this section does not falsely relabel the available tail as an independent forward OOS sample.

The preregistration will pin:
- immutable 0069 `PRIMARY_RESULT.json` blob `df00901c77d8d334d61c7c65a14b8d127e9ca8b6`;
- immutable 0069 `EVIDENCE.json` blob `6266e6a11205e21592766546342ca5bca1dd97f0` for frozen selected parameters/screened identities;
- market evidence blob `64ebf5c6deaf3f34dbeac715378f196ff0f4fafe` and payload SHA256 `d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193`;
- 0047 loader blob `059b55961e279dab41ba29b5b017de0922e4f33c`;
- 0062 feature builder blob `cac8e946998c836d10842b9388e1e3ef345a8c0b`;
- frozen event/model mechanics inherited from 0067/0069.

No equity, weights, DTB3, cash engine or portfolio controller input is needed or allowed in this section.

## Execution design
Lifecycle:
`OWNER-FIRST -> DESIGN -> PREREGISTRATION -> IMPLEMENTATION -> NONHISTORICAL QUALIFICATION -> CONTROLLED BOUNDARY -> ZERO-RESULT PREFLIGHT -> ONE CONTROLLED DEVELOPMENT-HISTORY ATTEMPT -> RESULT -> IMMUTABLE CLOSEOUT`.

Before the controlled attempt:
- implementation and jackknife logic must pass deterministic synthetic tests;
- qualification must demonstrate exact episode assignment, seven-fold construction, metric calculation, retention gates, fail-closed identity mismatch and no evidence/history reads;
- exact merged-boundary zero-result preflight must pass.

At execution:
- durable `RUN_ATTEMPT.marker` must be persisted before the first pinned evidence/market-content read;
- each permitted historical/evidence artifact may be read at most once;
- network fetches are zero;
- no same-ID rerun, rescue, retune or alternate fold definition is allowed after attempt consumption;
- immutable result/evidence/execution artifacts and final `RUN_ONCE.marker` are create-only and hash-bound.

## No economics and no production authority
0070 evaluates signal concentration/episode robustness only. It does not evaluate controllers, CAGR, NAV, MDD, transaction costs, PBO, leverage, position sizing or order logic. The 0069 controller `KeyError` is outside this section and may not be repaired here.

At all stages:
- `production_authorized = false`
- `signature_authorized = false`
- `order_submission_authorized = false`
- Canonical BRRK-0011 = NO CHANGE
- Phase 6 = NO CHANGE

## Terminal interpretation
A PASS means only that the already-known DEVELOPMENT-history SOL long-sideways warning is not obviously dominated by a single one of its seven final event onsets under the frozen jackknife rule. It is **not** independent OOS confirmation and is not a trading authorization.

A FAIL means the closed 0069 predictive finding is too episode-concentrated for this preregistered robustness criterion. An INCONCLUSIVE result means the required episode-level measurement cannot be formed without relaxing support. An execution-integrity breach is `INVALID_EXECUTION`, never scientific FAIL/PASS.
