# BRRK-BETA-BTC-CONTINUATION-PARAMETER-GEOMETRY-0058 — DESIGN FREEZE

Date: 2026-08-12  
Status: **DESIGN FROZEN / NUMERICAL PREREG NOT YET FROZEN / NOT IMPLEMENTED / NOT RUN**

## 1. Research identity and interpretation boundary

Research ID: `BRRK-BETA-BTC-CONTINUATION-PARAMETER-GEOMETRY-0058`  
Family: `BRRK_BETA_TO_BTC_CONTINUATION`  
Purpose: governed DEVELOPMENT parameter identification for a simple causal Beta-to-BTC continuation/shelter mechanism.

0058 is a **new research ID** opened only after immutable 0057 closure. It is not a rerun, rescue, retuning or alternative implementation of the failed ETH/SOL micro-timing router.

0058 is deliberately a **calibration / parameter-geometry study**, not a final strategy-validation study. It may inspect a prospectively frozen finite parameter lattice on researcher-exposed DEVELOPMENT history only after numerical preregistration, implementation-only merge and a separately merged controlled-execution boundary. Its sole promotion authority is to freeze one deterministic representative parameter pair for a later **new research ID**. A 0058 PASS does not establish independent OOS validity, strategy eligibility or production authority.

The economic objective remains primary:

> identify whether a simple causal Beta-to-BTC mechanism has a broad, locally insensitive, after-cost terminal-wealth plateau rather than a narrow historical optimum.

The parameter-selection rule must therefore prefer **stability geometry**, not the highest historical P&L point.

## 2. Binding upstream evidence

The following exposed evidence is immutable and may inform the question but cannot be rewritten:

- 0047 established no preregistered recurrent durable BTC-to-Beta handoff structure; its exact episode clock/model lineage is closed.
- 0048 explicitly treated BTC as a defensive anchor and ETH/SOL as the Beta tier; it did not authorize Beta-to-BTC economics.
- 0053/0054/0055 closed the probability-readiness repair lineage without establishing an economically eligible ETH/SOL predictive router.
- 0056 was invalid at its unique interface attempt and produced no economic conclusion.
- 0057 validly closed `FAIL_SIMPLE_BETA_ROUTER_COST_FRAGILE`; its exact RM60 ETH/SOL router is not economically eligible, and the ETH/SOL micro-timing line is closed.
- 0057 closeout explicitly names the next admissible family as `BETA_TO_BTC_CONTINUATION_VALUE_FULL_CYCLE_EXIT` under a new research ID.

0058 therefore does **not** consume the 0057 router as the Beta sleeve, does not retune RM60, and does not test ETH-versus-SOL leadership. It moves one level up the capital hierarchy: **Beta risk versus BTC defensive anchor**.

All reusable market history through 2026-08-02 is researcher-exposed DEVELOPMENT data. No same-history 0058 or successor result may be described as independent OOS.

## 3. Frozen scientific question

> Does a simple two-parameter causal Beta-versus-BTC continuation rule exhibit a broad, connected, after-cost terminal-wealth plateau under finite-difference sensitivity analysis, such that one representative parameter pair can be selected mechanically without choosing the historical wealth maximum?

This question is about **parameter identifiability and stability**, not about proving a production strategy.

If no admissible plateau exists under the later preregistered geometry and robustness contract, 0058 must close without selecting a parameter from a sharp peak, boundary artifact or merely best-performing grid cell.

## 4. Capital hierarchy and asset universe

0058 uses exactly:

```text
BTC                                  defensive anchor
ETH + SOL                            Beta tier
cash                                 initial funding state only
leverage                             forbidden
shorting                             forbidden
```

BTC-to-cash timing is explicitly outside 0058. Cash may not be used as a post-entry risk state.

The candidate always holds either:

1. **100% BTC**, or
2. a mechanically defined **ETH/SOL Beta sleeve**.

No BNB, XRP, alt expansion, stablecoin timing or derivatives are allowed.

## 5. Frozen Beta representation

0058 must not use the failed 0057 dynamic ETH/SOL router.

For signal construction, define the symmetric Beta relative-log-price state:

`z_t = 0.5 * log(ETH_t / BTC_t) + 0.5 * log(SOL_t / BTC_t)`.

Equivalently, this is the log relative price of the geometric-mean ETH/SOL Beta proxy versus BTC. ETH and SOL enter symmetrically; there is no leader selection and no hindsight winner.

For executable portfolio accounting, every transition from BTC into Beta allocates the post-cost portfolio **50% ETH / 50% SOL by value at that entry boundary**. While the Beta state persists, the two components drift naturally with market prices and are **not periodically rebalanced**. A later BTC-to-Beta re-entry resets the new Beta entry allocation to 50/50 after transaction costs.

This convention avoids hidden daily internal turnover while preserving a symmetric, causal Beta tier.

The signal proxy remains the fixed 50/50 log-relative composite regardless of subsequent sleeve weight drift. Portfolio weight drift has no feedback into the signal.

## 6. Frozen two-parameter mechanism family

The only tunable scientific parameters in 0058 are:

- `L`: integer relative-trend lookback in completed UTC daily sessions;
- `kappa`: non-negative standardized continuation threshold.

No third tunable parameter is allowed.

Let

`d_t = z_t - z_(t-1)`

and let `sigma240_t` be the trailing sample standard deviation (`ddof=1`) of the most recent 240 valid `d` observations through `t`, with denominator protection `1e-12`. The 240-session volatility normalization is inherited as a pre-existing scale convention from 0048 and is **not** a 0058 tuning coordinate.

Define the standardized Beta-versus-BTC continuation score:

`S_t(L) = (z_t - z_(t-L)) / ((sigma240_t + 1e-12) * sqrt(L))`.

The frozen state rule is:

```text
S_t(L) > kappa     -> hold Beta sleeve for the next close-to-close period
S_t(L) <= kappa    -> hold BTC for the next close-to-close period
```

`kappa` must be non-negative. Thus leaving the BTC anchor for Beta requires non-negative-to-positive standardized relative continuation evidence; 0058 cannot learn a negative threshold that systematically holds Beta while its standardized relative trend is negative.

Exact equality belongs to BTC. There is no retain-prior equality rule, hysteresis band, separate entry/exit threshold or minimum holding period.

## 7. Causal timing

0058 uses completed UTC daily closes only.

At origin `t`:

1. observe prices only through the completed close at `t`;
2. compute `z_t`, `sigma240_t` and `S_t(L)` from information available through `t`;
3. determine BTC or Beta state after close `t`;
4. debit any transaction cost caused by the state transition;
5. earn only the next close-to-close held return from `t` to `t+1`.

No same-close hindsight return, intraday information or future component weight is allowed.

The exact common evaluation origins will be frozen from the immutable daily source calendar at preregistration and must be identical for every parameter cell and every benchmark.

## 8. Transaction-cost semantics

0058 inherits executed-L1-turnover cost accounting.

`cost_rate = cost_bps / 10000`

`transaction_cost = pre_trade_NAV * executed_L1_turnover * cost_rate`.

The intended cost family is the existing project convention:

```text
primary                            5 bps per unit L1 turnover
stress 1                          10 bps per unit L1 turnover
stress 2                          20 bps per unit L1 turnover
```

The numerical preregistration must freeze exact debit ordering and transition L1 calculations. The design-level portfolio geometry is already constrained:

- initial cash -> 100% BTC or initial 50/50 Beta has L1 turnover 1;
- 100% BTC -> 50/50 ETH + 50/50 SOL has L1 turnover 2;
- drifting Beta -> 100% BTC uses actual pre-trade ETH/SOL weights and has total L1 turnover 2;
- unchanged BTC state has L1 turnover 0;
- unchanged Beta state has no internal rebalance and therefore no state-maintenance turnover.

No spread/slippage model may be added selectively after viewing 0058 output. Any more conservative execution model requires a separate prospective contract.

## 9. Parameter-domain governance

0058 is explicitly allowed to evaluate a **finite preregistered parameter lattice** because parameter geometry is its scientific target. This is not a one-candidate strategy-validation ID.

However, the lattice itself must be frozen before any 0058 economic output and may not be chosen from a preliminary surface.

The numerical preregistration must bind:

- exact `L` minimum, maximum and spacing;
- exact `kappa` minimum, maximum and spacing;
- total lattice cell count;
- treatment of cells lacking full finite-difference neighborhoods;
- exact common data window shared by all cells.

Domain justification must be data-independent with respect to 0058 economics. In particular:

- the `L` domain must be anchored to already-existing project time scales rather than a pilot wealth scan; the pre-existing 20/60/120/240 daily trend family supplies admissible scale anchors;
- `kappa` is dimensionless because of volatility normalization, so its later frozen domain must be stated directly in standardized units rather than derived from observed winning thresholds;
- no adaptive grid refinement around a profitable region is allowed after the first 0058 output;
- no Bayesian optimization, random search, evolutionary search or second-stage local zoom is allowed.

One preregistered lattice, one execution, one geometry result.

## 10. Economic surface

For every preregistered parameter cell `theta = (L, kappa)` and every frozen cost level `c`, the implementation will produce an after-cost candidate terminal wealth `W_c(theta)` on the identical full-cycle evaluation window.

Define the geometry surface:

`J_c(theta) = log(W_c(theta))`.

Net terminal wealth / log terminal wealth is the optimization-relevant quantity. CAGR is a monotone transformation on the common horizon and will be reported. Maximum drawdown is a required diagnostic but is **not** the surface optimized or differentiated.

No Sharpe, Sortino, Calmar or model-fit metric may replace terminal wealth as the parameter-geometry objective.

## 11. Discrete first- and second-order sensitivity

Because `L` is integer-valued and portfolio switching makes the economic surface piecewise/discrete, 0058 does **not** pretend analytic differentiability.

All derivatives are finite-difference diagnostics on the frozen lattice.

Let grid indices be `(i,j)` for increasing `L` and `kappa`. Coordinates are normalized by one grid step so different physical units do not dominate the geometry.

For interior cells, the preregistration will freeze central first differences analogous to:

`D_L J[i,j] = (J[i+1,j] - J[i-1,j]) / 2`

`D_k J[i,j] = (J[i,j+1] - J[i,j-1]) / 2`.

Second differences will include:

`D_LL J[i,j] = J[i+1,j] - 2*J[i,j] + J[i-1,j]`

`D_kk J[i,j] = J[i,j+1] - 2*J[i,j] + J[i,j-1]`

and a symmetric central cross-difference for `D_Lk`.

The later preregistration must freeze:

- gradient norm convention;
- Hessian / curvature norm convention;
- all numerical tolerances;
- edge-cell policy;
- non-finite-cell policy.

These thresholds may not be selected after looking at the realized surface.

## 12. Plateau principle

0058 seeks a **broad stable plateau**, not an argmax.

A cell can belong to an admissible plateau only if it satisfies prospectively frozen local-sensitivity requirements. At minimum, preregistration must require both:

1. low local gradient magnitude;
2. low local curvature / Hessian magnitude.

The plateau must additionally be a connected set on the two-dimensional lattice under a prospectively frozen adjacency rule and must satisfy a minimum connected-size/interior-support requirement.

A one-cell spike, boundary-only ridge or isolated historical maximum cannot qualify as a plateau.

The preregistration must also freeze how cost robustness enters plateau eligibility. The intended design principle is **cost-coherent stability**: a parameter region should not be called stable merely because the 5 bps surface is flat if the same neighborhood becomes sharply unstable or economically nonviable at 10/20 bps.

No plateau threshold may be relaxed after result exposure.

## 13. Deterministic plateau and representative selection

If multiple admissible connected plateau components exist, selection may not use the component with the highest historical terminal wealth.

The numerical preregistration must freeze a deterministic non-P&L ranking rule. The design requires the following hierarchy in substance:

1. prefer the component with the largest admissible connected support;
2. resolve exact support ties by a fixed data-independent ordering;
3. select a representative **geometric medoid / center** of the chosen component under normalized lattice distance;
4. resolve exact medoid ties by a fixed lexicographic rule.

The representative parameter is therefore chosen for centrality inside the stable region, **not** because it is the best-returning cell.

The historical argmax cell must be reported for audit if the result schema permits, but it has zero selection or promotion authority.

## 14. Benchmarks and economic relevance

0058 calibration must not certify a beautifully flat but economically useless plateau.

The preregistration must freeze executable static benchmarks on the same evaluation window. At design level the comparison family is:

- `B0_STATIC_BTC`: one initial 100% BTC entry, then buy-and-hold;
- `B1_STATIC_BETA`: one initial 50/50 ETH/SOL entry, then both components drift with no rebalance;
- `B2_STATIC_BTC_BETA`: one initial fixed BTC/Beta allocation frozen prospectively in preregistration, then buy-and-hold/drift with no timing.

The exact B2 starting weights must be frozen before 0058 output and must not be selected from the calibration surface.

The later preregistration must define an economic-relevance gate for the **mechanically selected plateau representative**, not for the ex-post best lattice cell. Failure of that representative gate closes 0058 even if some other grid point is profitable.

## 15. Temporal and dependence-aware robustness

Parameter stability on one full-history aggregate is not sufficient by itself.

Before execution, preregistration must freeze:

- a deterministic chronological partition or other dependence-respecting temporal robustness diagnostic;
- the minimum temporal consistency required of the selected representative and/or plateau;
- a paired dependence-aware uncertainty method for representative-versus-benchmark economic uplift if used as a hard gate;
- block length, replicate count, seed, quantile convention and simultaneous-inference semantics if bootstrap is used.

These inferential settings cannot be changed after any 0058 surface is visible.

0058 may not choose a parameter because it is excellent in one bull episode while unstable elsewhere unless that behavior still satisfies the prospectively frozen temporal contract.

## 16. Required immutable output shape

A key lesson from the 0057 review is that aggregate MDD alone is insufficient for human audit.

The later result schema must preserve enough immutable output to inspect the selected economic path **without recomputation**. At minimum, after the unique execution it must retain:

- the complete preregistered parameter lattice identity;
- terminal wealth / CAGR / MDD / turnover / switch count for every lattice cell at every frozen cost level, or an equivalently lossless machine-readable surface table;
- first-difference and curvature/Hessian diagnostics needed to reproduce plateau membership from the frozen surface;
- plateau membership and component identity;
- deterministic selected representative and the exact selection trace;
- historical argmax location marked **DESCRIPTIVE_ONLY / NO_SELECTION_AUTHORITY**;
- daily representative NAV path;
- daily representative drawdown path;
- daily NAV and drawdown paths for the frozen static benchmarks;
- state path (BTC versus Beta) for the selected representative;
- transaction-cost and turnover path sufficient for audit.

The representative daily path must be persisted during the unique execution. Closeout must not rerun portfolio economics merely to draw a chart later.

## 17. 0058 classifications and promotion boundary

Exact machine classification strings and numerical gates are deferred to preregistration, but the design-level meanings are fixed.

A valid 0058 outcome must fall into one of these conceptual classes:

- **NO_STABLE_PARAMETER_PLATEAU** — no admissible broad connected low-gradient/low-curvature region exists;
- **STABLE_PLATEAU_NOT_COST_ROBUST** — apparent geometry does not survive the frozen cost-coherence contract;
- **STABLE_PLATEAU_NOT_ECONOMICALLY_RELEVANT** — a plateau exists but its mechanically selected representative fails the frozen economic-relevance gate;
- **STABLE_PLATEAU_NOT_TEMPORALLY_OR_DEPENDENCE_ROBUST** — geometry/economics exist but fail frozen robustness requirements;
- **PASS_PARAMETER_FREEZE_ELIGIBLE** — one deterministic representative pair is eligible to be frozen for a later new-ID fixed-rule economic study;
- **INVALID_EXECUTION** — integrity/protocol failure under the future exactly-once contract.

Only the final PASS class can create parameter-freeze eligibility.

Even a PASS does **not** mean `PASS_STRATEGY`, does not authorize production and does not establish independent OOS evidence.

## 18. Mandatory stop rules

After any valid 0058 surface is exposed, the same ID may not:

- expand or shift the `L` range;
- change `L` spacing;
- expand or shift the `kappa` range;
- change `kappa` spacing;
- zoom into a profitable region;
- change volatility normalization;
- replace the symmetric Beta proxy;
- change Beta internal rebalancing semantics;
- add separate entry/exit thresholds or hysteresis;
- add minimum holding time;
- add drawdown, CORE4, BTC trend, funding, OI, macro, sentiment or other state variables;
- change cost levels or turnover accounting;
- change gradient/Hessian definitions or tolerances;
- change plateau connectivity/minimum size;
- choose a different plateau because it made more money;
- replace the medoid/center rule with historical argmax;
- change benchmarks, temporal partition or bootstrap to rescue a failure.

Any such continuation requires a **new research ID** and must explicitly treat all 0058 surface information as exposed DEVELOPMENT evidence.

## 19. Successor-study firewall

If 0058 ends `PASS_PARAMETER_FREEZE_ELIGIBLE`, the selected `(L*, kappa*)` must be committed immutably in closeout.

The next stage is **not** a second execution under 0058. It must be a new registered research ID for an exactly fixed Beta-to-BTC rule with parameter count one pair and variant budget one.

That successor may test full-cycle economic eligibility under its own prospectively frozen gates, but:

- it may not change `(L*, kappa*)` using 0058 or successor results;
- it must treat all history through 2026-08-02 as researcher-exposed DEVELOPMENT;
- same-history confirmation cannot be labeled independent OOS;
- genuine OOS validation requires future observations not consumed by calibration.

If 0058 does not PASS, no representative parameter may be rescued from the surface merely because it was the historical best cell.

## 20. Explicit exclusions

0058 does not evaluate:

- 0057 RM60 ETH/SOL router economics as a candidate sleeve;
- ETH-versus-SOL leader prediction;
- probability calibration;
- neural networks, tree models, boosting or ensembles;
- BTC-to-cash timing;
- stablecoin/cash shelter;
- leverage or shorting;
- per-asset Beta concentration;
- winner oracle / hindsight asset selection;
- adaptive parameter search;
- production trading.

## 21. Governance sequence

The only legal 0058 order is:

```text
design freeze
-> design merge
-> numerical/data preregistration of the complete finite lattice and geometry gates
-> prereg merge
-> implementation-only with synthetic contracts
-> implementation merge
-> controlled execution boundary
-> boundary merge
-> exactly one DEVELOPMENT parameter-geometry execution
-> immutable closeout
```

No real 0058 parameter surface may be computed before the controlled execution boundary merges.

After a durable 0058 attempt marker exists, same-ID recomputation, retuning, rescue and threshold relaxation are forbidden under the repository's exactly-once policy.

## 22. Production and canonical isolation

Nothing in 0058 changes the live/canonical system:

```text
Canonical BRRK-0011                    NO CHANGE
Phase 6                                NO CHANGE
production gross cap                   1.0
production_authorized_components       []
production_authorized                  false
signature_authorized                   false
order_submission_authorized            false
```

0058 is research-only.

## 23. Design-freeze completion criterion

This design stage is complete only when this document is merged through a formal design PR while remaining free of numerical preregistration, central registry owner creation, implementation, workflow, historical parameter surface, result artifact and run marker.

After design merge, the only legal continuation is a separate numerical/data preregistration that freezes the exact lattice, derivative/curvature conventions, plateau thresholds, benchmark weights, temporal/dependence gates, result taxonomy and immutable output schema **before any 0058 economics are run**.
