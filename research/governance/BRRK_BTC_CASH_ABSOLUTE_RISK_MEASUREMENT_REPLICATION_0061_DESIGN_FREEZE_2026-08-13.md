# BRRK-BTC-CASH-ABSOLUTE-RISK-MEASUREMENT-REPLICATION-0061 — Design Freeze

Date: 2026-08-13

Status: **DESIGN-ONLY / NO NUMERICAL PREREGISTRATION / NOT IMPLEMENTED / NOT RUN**

## 1. Identity and question

Research ID: `BRRK-BTC-CASH-ABSOLUTE-RISK-MEASUREMENT-REPLICATION-0061`

Family: `BRRK_BTC_TO_CASH_GROSS_RISK`

Role: **measurement-corrected replication / pure mechanism diagnostic**.

0061 is a new-ID replication of the unresolved 0060 question. It is not a same-ID rerun, rescue or reconstruction of 0060.

Frozen question:

> Does the same fixed causal BTC absolute-risk state used by 0060 contain recurrent monotone information about subsequent BTC downside severity and cash-relative terminal underperformance across the same 20/60/120/240-day horizon family, when the already-identified resampled-correlation degeneracy is removed without changing the state, targets, dataset, horizons or success direction?

No portfolio allocation or economic-performance claim is authorized by this study.

## 2. Binding 0060 evidence

0060 is immutable at `INVALID_EXECUTION / CLOSED / NO SCIENTIFIC CONCLUSION`.

Binding facts from live repository:

- scientific execution HEAD: `fe210187472c2bcdfb51573b4cc544c187ade079`;
- immutable 0060 scientific-engine blob: `b901774b6849c9bcf6fbbf9887022142bf74a42d`;
- durable attempt marker was persisted before measurement;
- exactly one market-content read, source-loader call and scientific-engine call occurred;
- no `PRIMARY_RESULT.json`, `EXECUTION.json` or final run marker was persisted;
- binding controlled error: `lcb.terminal_loss_20 must be finite numeric`;
- 0060 establishes neither mechanism success nor mechanism failure;
- unpersisted in-memory statistics have zero authority and may not be reconstructed or used for design selection;
- corrected execution requires a new research ID.

Therefore 0061 may correct only the identified measurement interface.

## 3. Frozen diagnosis

The frozen 0060 architecture combines:

1. `TERMINAL_LOSS_h=max(0,-log(BTC_(t+h)/BTC_t))`, which creates a point mass at exact zero;
2. moving-block resampling;
3. recomputation of Spearman correlation inside each resample;
4. nonfinite replicate correlation when a resampled coordinate is constant;
5. whole-bootstrap failure if any replicate is nonfinite.

Thus one degenerate resample can convert an otherwise measurable question into execution invalidity.

0061 freezes this principle before any historical execution:

> A resample-level loss of rank variance is sampling information, not a protocol failure, provided the full shared panel contains finite nonconstant state and target coordinates.

If a required coordinate is constant on the **full** shared panel, that is a valid scientific no-information result rather than execution invalidity.

## 4. Predictor representation — unchanged

0061 must delegate state construction to the immutable 0060 engine blob:

`research/brrk_btc_cash_absolute_risk_diagnostic_0060/engine.py` @ `b901774b6849c9bcf6fbbf9887022142bf74a42d`.

Unchanged scientific representation:

- trend horizons 20/60/120/240;
- FAST weights 0.15/0.25/0.30/0.30;
- SLOW weights 0.10/0.20/0.30/0.40;
- A1 = BTC trend disagreement plus persistence;
- A2 = BTC price-structure deterioration;
- A3 = BTC volatility/downside asymmetry;
- causal normalization = trailing 252, min 60, sample std ddof1, clip [-3,+3];
- joint state `S=(A1+A2+A3)/3` with strict required-coordinate validity.

No feature may be added, removed, selected or reweighted under 0061.

## 5. Target representation — unchanged

All eight 0060 targets remain co-primary:

- terminal_loss_20/60/120/240;
- adverse_excursion_20/60/120/240.

Semantics remain:

`TERMINAL_LOSS(t,h)=max(0,-log(BTC_(t+h)/BTC_t))`

`ADVERSE_EXCURSION(t,h)=max_(u=1..h) max(0,-log(BTC_(t+u)/BTC_t))`.

A signed BTC-vs-Cash target is explicitly outside 0061 because it is a different scientific target and would require another research ID.

No horizon or target family may be dropped.

## 6. Data — unchanged

0061 may use only the same exposed DEVELOPMENT dataset bound by 0060:

- slice: `BRRK-LEADERSHIP-ROTATION-0048-EXPOSED-HIST-V1`;
- wrapper: `research/brrk_beta_handoff_0047/evidence/MARKET_EVIDENCE.json`;
- wrapper blob: `64ebf5c6deaf3f34dbeac715378f196ff0f4fafe`;
- payload SHA256: `d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193`;
- common rows: 2183;
- window: 2020-08-11 through 2026-08-02;
- consumed information: completed BTC daily close only;
- independent OOS: false.

No refetch, provider substitution, row extension, alternate payload, gap fill or frequency change is permitted.

## 7. Full-sample and temporal association — unchanged

The shared-origin concept remains identical across all eight targets.

Full-sample G2 remains ordinary average-tie Spearman:

`rho_k = Spearman(S,Y_k)`.

All required full-sample associations must be strictly positive.

Temporal recurrence remains ordinary Spearman inside the same four chronological equal-as-possible blocks. A block with a constant required coordinate simply does not count as a positive block; it does not invalidate execution.

The later preregistration must inherit the 0060 support and temporal gate architecture without outcome-driven relaxation.

## 8. Sole scientific correction — fixed-score dependence inference

Only the dependence-aware G4 inference is changed.

### 8.1 Full-panel midrank scores

For the final shared panel of size N:

1. compute average-tie ranks of `S` and each target `Y_k` once on the full panel;
2. center each rank vector by its full-panel mean;
3. divide each centered vector by its full-panel population RMS `sqrt(mean(centered_rank^2))`;
4. denote the standardized fixed scores by `U_i` and `V_(i,k)`.

If a full-panel RMS is zero/nonfinite, the required coordinate is scientifically constant and the study returns a valid no-information FAIL before bootstrap.

For a nonconstant full panel define:

`A_k = mean_i(U_i * V_(i,k))`.

By construction `A_k` equals the ordinary average-tie Spearman `rho_k` on the full shared panel, up to frozen numerical tolerance. Implementation-only tests must prove this identity before historical execution.

### 8.2 Moving-block resampling

The dependence bootstrap resamples aligned rows of the fixed-score vector `[U_i,V_(i,1),...,V_(i,8)]`.

For replicate b with row indexes `I_b`:

`A_(b,k)=mean_(j in I_b)(U_j*V_(j,k))`.

Ranks are not recomputed inside the replicate and no replicate-specific correlation denominator exists. Therefore a resample containing only tied/zero target observations remains a finite sampling observation whenever the full-panel scores are valid.

### 8.3 Simultaneous lower bounds

Retain the same one-sided all-target family-wise structure:

`M_b=max_k(A_k-A_(b,k))`

`LCB_k=A_k-q95(M_b)`.

All required simultaneous LCBs must be strictly positive for the dependence gate to pass.

The later numerical preregistration must freeze the exact block length, replicate count, seed and quantile convention before implementation. The design intent is to inherit the 0060 dependence geometry rather than weaken it because 0060 was invalid.

## 9. Valid scientific failure versus execution invalidity

0061 must persist valid scientific failure rather than overuse `INVALID_EXECUTION`.

Valid FAIL conditions include:

- insufficient shared support;
- full-panel state constant;
- any full-panel required target constant;
- any required full-sample association nonpositive;
- insufficient temporal recurrence;
- finite simultaneous LCBs not all positive.

If an earlier scientific gate fails, later gates may be persisted as `NOT_EVALUATED_DUE_TO_PRIOR_GATE` with a frozen reason code. A bootstrap result need not be manufactured after an earlier binding scientific failure.

`INVALID_EXECUTION` is reserved for integrity/protocol failures such as wrong immutable input identity, unauthorized data/code path, invalid source values, implementation drift, result-schema corruption, extra variants or exactly-once state-machine violation.

A degenerate bootstrap replicate alone may not cause `INVALID_EXECUTION` under 0061.

## 10. Mandatory implementation-only adversarial tests

Before any real historical execution, synthetic/toy tests must cover at least:

1. ordinary continuous coordinates: fixed-score observed statistic equals Spearman;
2. heavy ties in state;
3. heavy ties in target;
4. zero-inflated target with majority exact zeros;
5. a contiguous synthetic 240-row exact-zero target region;
6. repeated selection of one moving block;
7. a replicate with constant target score;
8. a replicate with constant state score;
9. full-panel target constant -> valid scientific FAIL;
10. full-panel state constant -> valid scientific FAIL;
11. earlier-gate failure -> downstream inference may be skipped while result remains valid;
12. deterministic bootstrap seed;
13. simultaneous max-error across exactly eight targets;
14. no target/horizon selection path;
15. no real historical loader/network path inside implementation-only tests.

Real historical target values may not be inspected to decide whether the correction is sufficient.

## 11. Alternatives explicitly rejected under 0061

These alternatives are recorded now to prevent outcome-driven switching later:

- map undefined replicate Spearman to zero: rejected as an ad hoc replicate substitution rule;
- Kendall tau-a: tie-safe but rejected because it changes the primary association metric more than necessary;
- signed BTC-vs-Cash return target: scientifically distinct and deferred to a separate ID;
- shorter dependence block or fewer replicates: rejected as post-invalidity weakening;
- stationary/circular bootstrap or parametric time-series model: not selected because they change more of the dependence architecture than necessary;
- any portfolio-control mapping: outside this pure measurement replication.

Chosen correction: **full-panel fixed-midrank-score moving-block inference plus gate short-circuit semantics**.

## 12. Hypothesis and interpretation

Primary hypothesis: the unchanged BTC absolute-risk state contains positive, recurrent and dependence-robust information about the unchanged eight future downside targets.

Adversarial hypothesis: once measured validly, the state may show no joint information, isolated-horizon behavior, temporal instability or dependence-sensitive apparent information.

0061 is not designed to make the hypothesis pass. It is designed to obtain a valid measurement of the unresolved 0060 question.

A PASS would create eligibility only for a separate new-ID state-to-risk-control study. It would not validate any allocation rule or economic performance.

A valid FAIL closes same-ID rescue, feature changes, horizon selection, target selection and inference weakening.

## 13. Stage order

0061 must follow:

1. DESIGN
2. DESIGN merge
3. numerical/data PREREGISTRATION
4. PREREGISTRATION merge
5. IMPLEMENTATION-ONLY
6. IMPLEMENTATION merge
7. CONTROLLED-EXECUTION BOUNDARY
8. BOUNDARY merge
9. exactly one historical execution attempt
10. immutable CLOSEOUT

## 14. Current stage boundary

At this stage:

```text
0061 DESIGN                         FROZEN
0061 DESIGN merge                   ABSENT
0061 numerical preregistration      ABSENT
0061 central registry owner         ABSENT
0061 implementation                 ABSENT
0061 controlled execution boundary  ABSENT
0061 historical execution           NOT RUN
0061 result                         ABSENT
0061 actual variants evaluated      0
```

No 0061 historical state/target association, bootstrap statistic, rho, LCB or portfolio-performance result has been computed by this design stage.

The only allowed next step is a separate DESIGN merge. After that merge, numerical/data preregistration may freeze the exact shared-panel support threshold, rank-score floating-point tolerance, temporal gate, moving-block length, replicate count, seed, quantile rule, classification precedence, result schema and exactly-once contract.
