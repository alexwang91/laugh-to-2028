# BRRK Multi-Architecture Gross Controller 0065 — DESIGN FREEZE

Date: 2026-08-14
Research ID: `BRRK-MULTI-ARCHITECTURE-GROSS-CONTROLLER-0065`
Research family: `BRRK_BTC_TO_CASH_GROSS_RISK`
Research domain: `RISK_CONTROL`
Governance mode: `PROGRAM_GOVERNED_V1`
Stage: `DESIGN_ONLY`
Production authority: none

## 1. Scientific question

Does a prospectively frozen tournament of structurally different multivariate combination architectures, all using the same broad causal Tier-A signal universe and the same portfolio mapping, identify a stable outer gross-control rule that improves full-cycle net wealth/CAGR relative to the already-closed 0064 passive-cash baseline without materially worsening drawdown?

This research changes the research process, not merely one signal formula. The primary object of inference is the **combination architecture**. The design therefore freezes a representative model family set first, before any 0065 strategy economics are computed.

## 2. Why this is a new research ID

0062 was an information atlas and forbade state-to-gross translation. It closed `FAIL_NO_SIGNAL_ATLAS_FAMILY_INFORMATION` after family-level information gates. 0065 asks a different question: whether **multivariate conditional combination structure** can extract portfolio-relevant information from the complete preregistered feature universe even when no single family survives the 0062 simultaneous family-level gate.

0063 and 0064 studied idle-cash economics, not indicator combination. 0064 is now the economic baseline because it validly improved BRRK-0011 by continuously accruing already-idle cash. 0065 must compare against 0064, not silently revert to the weaker zero-carry BRRK-0011 baseline.

All prior results are researcher-exposed DEVELOPMENT history. No 0062 family, cell, parameter, 0063 zero-sweep observation, or 0064 performance result may be used to prune the 0065 feature universe or choose the 0065 winner after evaluation.

## 3. Methodological principle: architecture tournament before backtest selection

The research process is frozen in this order:

1. freeze the complete input ontology and feature identities;
2. freeze a small set of economically/statistically distinct model architectures;
3. freeze one common target and one common portfolio mapping;
4. freeze the pre-evaluation training/validation procedure and each architecture's bounded tuning budget;
5. implement all architectures and validate them only on synthetic/toy data;
6. merge a controlled-execution boundary;
7. execute all final architectures exactly once in one historical batch;
8. report every architecture's final CAGR/MDD/turnover and selection-adjusted robustness, not only the best result.

No method may be introduced after any 0065 evaluation-period portfolio result is observed.

## 4. Literature-motivated model spectrum

The tournament intentionally spans different structural assumptions rather than many near-duplicate parameterizations.

Primary methodological references motivating the spectrum include:

- Zou & Hastie (2005), Elastic Net: shrinkage and correlated-predictor grouping;
- Yuan & Lin (2006), grouped-variable selection: respecting pre-existing feature groups;
- Gu, Kelly & Xiu (2020), comparative machine-learning asset pricing: linear shrinkage, dimension reduction, nonlinear trees and interactions under chronological train/validation/test separation;
- Hamilton (1989), latent regime switching;
- Bailey et al. (2015), probability of backtest overfitting / combinatorially symmetric cross-validation;
- Bailey & Lopez de Prado (2014), Deflated Sharpe Ratio;
- White/Hansen reality-check / superior-predictive-ability framework for data-snooping-aware strategy comparison.

These references motivate method classes and validation discipline. They do not grant any architecture a favorable prior result.

## 5. Frozen feature universe

0065 uses the complete Tier-A feature construction already frozen by 0062:

- 185 causal standardized signal cells;
- 17 causal family scores;
- supported families: F01-F14, F21, F23, F24 plus F10/F11 risk families as defined by the 0062 engine;
- the six 0062 Tier-B/C unavailable families remain unavailable and cannot be substituted after outcome access;
- the 0062 latent-state family F22 remains outside the feature input matrix; 0065 may use a separately specified latent-state **combination architecture** over available 0065 inputs.

The exact 0062 engine blob, market-evidence blob/payload hashes, loader blob and resulting 185/17 dimensions must be frozen in PREREGISTRATION.

**Anti-pruning rule:** all eligible 185 cells / 17 family scores remain available exactly as specified by the architecture. No feature is removed because 0062 showed a weak or negative association and no family is privileged because it appeared descriptively favorable.

## 6. Common prediction target

All supervised architectures predict the same signed target:

`Y20_BTC_FORWARD_LOG_RETURN = log(BTC_close[t+20] / BTC_close[t])`

which is exactly the negative of 0062 `T1_CASH_ADVANTAGE@20` before any portfolio mapping.

Rationale:

- it aligns directly with the economic decision of retaining versus reducing crypto gross;
- it avoids clipping positive BTC opportunity cost;
- one common target makes architecture comparisons interpretable;
- 20 sessions is long enough to avoid reducing the study to one-day noise but short enough to be relevant to defensive gross control.

No 5/10/40-day target may be substituted after evaluation results are known. They may appear only as prespecified secondary diagnostics if frozen in PREREGISTRATION.

## 7. Common causal train / validation / evaluation design

The exact eligible origin dates are determined from the frozen 0062 feature/target panel.

Conceptual split, to be converted to exact origin indices in PREREGISTRATION:

- **TRAIN:** earliest eligible common origin through 2021-12-31;
- **VALIDATION:** 2022-01-01 through the last origin whose full 20-session target is known strictly before the 0065 portfolio evaluation start;
- **PORTFOLIO EVALUATION:** the existing BRRK/0064 portfolio support, 2022-12-10 through 2026-08-02.

No label whose 20-session endpoint overlaps the portfolio evaluation period may be used to select hyperparameters.

Hyperparameters are selected once using TRAIN -> VALIDATION only. After validation closes, hyperparameters are frozen permanently. During portfolio evaluation, models may be refit on expanding past data at a frozen cadence, but no hyperparameter is retuned.

The refit data at date `t` may include only origins whose 20-session target endpoint is strictly earlier than `t`.

## 8. Frozen architecture set

Eight final architectures will be evaluated. Their exact numerical hyperparameter grids and deterministic seeds belong to PREREGISTRATION, but the structural model class is frozen here.

### A01 — FAMILY_ELASTIC_NET

Inputs: 17 family scores.

Model: elastic-net linear regression.

Hypothesis: the signal is mostly additive and family-level aggregation removes redundant within-family noise. Shrinkage protects against correlated families and low signal-to-noise.

Interpretation: family coefficients give the cleanest linear economic attribution.

### A02 — RAW_ELASTIC_NET

Inputs: all 185 signal cells.

Model: elastic-net linear regression.

Hypothesis: useful information may exist in a minority of cell geometries even when the equal-weight family score dilutes it. Elastic net is used specifically because the cells are numerous and highly correlated.

No cell may be manually selected before fitting.

### A03 — PCR_RIDGE

Inputs: all 185 cells.

Model: training-only standardization -> principal-components reduction -> ridge regression.

Hypothesis: the indicator atlas is driven by a much lower-dimensional latent market-state manifold. PCA compresses correlated indicators without outcome-based feature selection; ridge then maps the latent factors to the common target.

### A04 — THEORY_QUADRATIC_HESSIAN_RIDGE

Inputs: 17 family scores plus all 17 squared terms plus a frozen low-order cross-family interaction graph.

Model: ridge-regularized second-order response surface.

Purpose: explicitly test curvature / second-derivative structure rather than relying on opaque nonlinear learners.

Frozen conceptual interaction graph:

1. trend level x volatility regime;
2. trend acceleration x volatility regime;
3. volatility-adjusted trend break x downside-tail state;
4. momentum level x cross-crypto breadth;
5. overbought/stretch x divergence/exhaustion;
6. breakdown/failed-break x volume confirmation;
7. relative crypto leadership x breadth;
8. sequential change detection x multi-timescale disagreement;
9. trend level x relative crypto leadership;
10. downside-tail state x volume confirmation.

The fitted quadratic coefficient matrix/Hessian is a required diagnostic. No new pair may be added after evaluation.

### A05 — GAM_SPLINE_RIDGE

Inputs: 17 family scores.

Model: fixed-degree causal spline basis per family followed by ridge regression; additive only, no cross-family interactions.

Hypothesis: each family may have smooth nonlinear thresholds/saturation, but interactions may be unnecessary. This separates **nonlinearity alone** from **interaction effects**.

### A06 — SHALLOW_GBDT

Inputs: 17 family scores.

Model: shallow gradient-boosted regression trees with tightly bounded depth/leaf complexity and deterministic seed.

Hypothesis: economically relevant rules may be threshold-like and conditional. Shallow trees can express nonlinear interactions while limiting degrees of freedom. Deep trees and open-ended boosting are forbidden.

### A07 — HMM_REGIME_MIXTURE_RIDGE

Inputs: a frozen small set of theory-defined meta-factors derived by equal-weight averaging of the 17 family scores for latent-state inference, plus the 17 family scores for state-conditional ridge prediction.

Meta-factor blocks:

- TREND/STRUCTURE: F01-F05, F09, F21, F23;
- MOMENTUM/EXHAUSTION: F06-F08;
- VOL/TAIL: F10-F11;
- BREADTH/FLOW/RELATIVE: F12-F14, F24.

Model: causal Gaussian HMM fitted only on past meta-factor observations; posterior regime probabilities feed a mixture of state-specific ridge regressions.

Hypothesis: the mapping from the same indicators to future returns changes across latent market regimes.

### A08 — STACKED_ENSEMBLE

Inputs: validation predictions from A01-A07 only.

Model: non-negative sum-to-one linear stacking weights selected from validation-period out-of-sample predictions and then frozen before portfolio evaluation.

Hypothesis: model uncertainty is material; structurally different architectures may contain complementary signal. The stack may reduce architecture-specific estimation error.

The stack may not add a new base learner after evaluation begins.

## 9. Common forecast-to-gross mapping

Every architecture uses the same deterministic mapping so that portfolio differences are attributable to the forecast architecture rather than bespoke trading thresholds.

At each refit date, on the model's eligible training sample:

1. compute fitted/predicted target values;
2. obtain training prediction median `m` and robust scale `s = 1.4826 * MAD`;
3. current forecast standardized score is `z = (prediction - m)/s`; if `s` is zero/non-finite, `z=0`;
4. outer risky-gross multiplier is `g_raw = clip(1 + 0.25*z, 0, 1)`.

Thus:

- positive/ordinary forecasts do not lever above the baseline (`g <= 1`);
- negative forecasts progressively reduce risk;
- the mapping contains no architecture-specific threshold;
- no shorting is possible.

Any optional smoothing or refit cadence must be frozen in PREREGISTRATION and must be identical across A01-A08.

## 10. Portfolio economics

0065 evaluates an **outer sleeve multiplier** applied to the already-costed BRRK-0011 portfolio return path, with 0064 passive-cash economics carried forward unchanged.

Let:

- `r_base[t]` = reconstructed net BRRK-0011 daily return;
- `G_base[t]` = absolute gross from frozen BRRK-0011 weights;
- `g[t]` = architecture-specific outer multiplier in [0,1];
- total cash after overlay = `1 - g[t] * G_base[t]`;
- cash yield model = 0064 primary: 50% realized DTB3, minus 100 bps/year continuous cash-account spread/fee;
- outer overlay trading cost = a preregistered bps charge on changes in the outer multiplier, separate from already-embedded BRRK-0011 internal strategy costs.

The design requires `g[t]=1` to reconstruct the 0064 primary path within numerical tolerance.

No leverage, shorting, signal change, risk-asset re-ranking, asset-weight optimization or production authorization is allowed.

## 11. Tournament evaluation and multiplicity control

The final historical run must persist results for **all eight architectures**, even if an early architecture looks poor or excellent.

Required primary economics per architecture:

- full evaluation-period terminal wealth;
- calendar-span CAGR;
- max drawdown;
- average gross and cash fraction;
- outer turnover and outer transaction cost;
- number and duration of meaningful de-risking episodes;
- four fixed contiguous chronological block relative log-growth values versus 0064;
- annual calendar returns where support permits.

Selection is explicitly a multiple-comparison problem. PREREGISTRATION must freeze a dependence-aware simultaneous correction across the eight final architecture return-difference series. A candidate can be called a robust winner only if its simultaneous one-sided lower confidence bound versus 0064 is strictly positive.

The report must also include a backtest-overfitting diagnostic across the frozen architecture set (e.g. CSCV/PBO or an equivalently preregistered selection-risk diagnostic) and a Deflated-Sharpe-style diagnostic where numerically well-defined. These are diagnostics, not substitutes for net wealth/CAGR.

## 12. Success hierarchy

Primary scientific priority:

1. full-cycle net terminal wealth / CAGR versus 0064;
2. max drawdown and bear-period damage;
3. temporal recurrence across fixed blocks;
4. simultaneous dependence-aware robustness across the eight-method tournament;
5. cost, turnover and architecture-complexity realism.

A descriptive best CAGR is always reported but is **not** automatically the scientific winner.

### Robust architecture pass

At least one architecture must satisfy all frozen gates, including:

- exact input/implementation identity;
- causal train/validation/evaluation separation;
- net terminal wealth and CAGR strictly above 0064;
- no material drawdown inferiority under the preregistered tolerance;
- temporal recurrence;
- simultaneous one-sided LCB > 0 after correcting across all eight architectures;
- bounded-turnover/cost realism;
- no exactly-once or persistence violation.

### Tournament fail

If all eight architectures are evaluated validly and none survives the full gate sequence, classify the tournament as no robust multivariate architecture improvement. Individual attractive CAGRs remain descriptive DEVELOPMENT evidence only.

## 13. Anti-overfit / anti-rescue rules

After the unique 0065 evaluation attempt begins, permanently forbidden under the same ID:

- adding/removing an architecture;
- changing the target horizon;
- pruning or privileging a feature/family based on 0065 results;
- changing the interaction graph;
- changing hyperparameter grids;
- changing forecast-to-gross mapping;
- changing cash-yield realization or cash fee;
- changing outer transaction-cost semantics;
- changing train/validation/evaluation boundaries;
- changing refit cadence;
- changing multiplicity/bootstrap/PBO procedures;
- rerunning a failed architecture separately;
- creating a post-hoc ensemble from observed evaluation winners.

A valid observed result closes the 0065 ID to same-ID recomputation, retuning and rescue.

## 14. Governance sequence

Required order:

1. DESIGN merge;
2. owner-first numerical/data PREREGISTRATION;
3. preregistration merge;
4. IMPLEMENTATION-ONLY with synthetic/toy tests only;
5. implementation merge;
6. CONTROLLED-EXECUTION BOUNDARY;
7. boundary merge;
8. exactly one authorized historical tournament execution containing all eight architectures;
9. immutable CLOSEOUT.

Before the controlled boundary merges, no 0065 evaluation-period portfolio CAGR, NAV, architecture ranking or result-derived feature selection may be computed.

## 15. Authority

`production_authorized=false`

`signature_authorized=false`

`order_submission_authorized=false`

Canonical BRRK-0011: no change.

0064 scientific closeout: no change.

Phase 6: no change.
