# CRYPTO MULTI-STRATEGY RESEARCH PROGRAM 0071–0082

Status: `PROGRAM ROADMAP ONLY / NO SUCCESSOR RESEARCH ID AUTHORIZED BY THIS FILE`

Date: 2026-08-17

Authoritative repository: `alexwang91/laugh-to-2028`

## 0. Purpose and governing principle

This document defines the prospective research program that follows immutably closed `BRRK-SOL-LONG-SIDEWAYS-EARLY-WARNING-EPISODE-ROBUSTNESS-0070` **only after 0070 has completed RESULT merge and separate IMMUTABLE CLOSEOUT**.

The program objective is not to maximize the historical Sharpe ratio of one increasingly complicated crypto predictor. The objective is to construct and independently validate multiple economically distinct return/risk-control sleeves, then test whether they improve a portfolio after costs, tail risk, concentration, multiple-testing and execution constraints.

The program is explicitly serial and gated. A downstream research ID may not use an upstream result until the upstream ID has reached immutable terminal closeout. A downstream ID may be skipped or terminated if its prerequisite fails. No PASS is guaranteed.

Every research ID uses the same formal lifecycle as 0069/0070:

`OWNER-FIRST -> DESIGN -> PREREGISTRATION -> IMPLEMENTATION -> NONHISTORICAL QUALIFICATION -> CONTROLLED BOUNDARY -> ZERO-RESULT PREFLIGHT -> ONE CONTROLLED DEVELOPMENT-HISTORY ATTEMPT -> RESULT -> IMMUTABLE CLOSEOUT`

The single controlled historical/development-history attempt is irreversible. A durable `RUN_ATTEMPT.marker` must be persisted before the first permitted history/evidence-content read. After durable attempt creation, same-ID rerun, rescue, retune, threshold relaxation, alternate universe, alternate cost model, alternate objective, alternate controller or result-informed semantic change is forbidden.

All research remains non-production by default:

- `production_authorized=false`
- `signature_authorized=false`
- `order_submission_authorized=false`

No research PASS in 0071–0082 by itself grants trading authority.

---

## 1. Evidence basis and why these sleeves exist

The program is motivated by several distinct empirical/economic mechanisms rather than by indicator accumulation:

1. Liu and Tsyvinski, *Risks and Returns of Cryptocurrency* (NBER 24877; Review of Financial Studies 2021) documents strong crypto-specific time-series momentum.
2. Liu, Tsyvinski and Wu, *Common Risk Factors in Cryptocurrency* (NBER 25882; Journal of Finance 2022) finds market, size and momentum factors capture important cross-sectional expected-return structure.
3. Schmeling, Schrimpf and Todorov, *Crypto Carry* (BIS Working Paper 1087, revised 2025) documents large and volatile spot-futures carry, links it to leveraged demand and limited arbitrage capital, and reports that high carry predicts higher future crash risk.
4. Cong, Li and Wang, *Tokenomics: Dynamic Adoption and Valuation* (NBER 27222; Review of Financial Studies 2021) provides an economic basis for treating network adoption/transaction demand as state information rather than assuming every on-chain metric is a direct trading alpha.
5. Bailey and López de Prado, *The Deflated Sharpe Ratio* (Journal of Portfolio Management 2014) motivates correcting performance inference for multiple testing, selection bias and non-normal returns.
6. Bailey, Borwein, López de Prado and Zhu, *The Probability of Backtest Overfitting* (Journal of Computational Finance 2015) motivates explicit PBO/CSCV accounting when selecting among strategy variants.

References are rationale only. They do not establish that any proposed sleeve passes in this repository.

---

## 2. Global program map and hard dependencies

| ID | Prospective research name | Purpose | Hard prerequisite |
|---|---|---|---|
| 0071 | `BRRK-SOL-LONG-SIDEWAYS-CONTROLLER-INTEGRATION-0071` | Convert the locked 0070 warning into an economic risk controller | 0070 immutable PASS closeout |
| 0072 | `BRRK-CRYPTO-CARRY-ATLAS-0072` | Point-in-time BTC/ETH/SOL funding/basis/carry structural atlas | 0071 closeout |
| 0073 | `BRRK-CRYPTO-DELTA-NEUTRAL-CARRY-STRATEGY-0073` | Test executable delta-neutral carry after all costs and venue stress | 0072 PASS closeout |
| 0074 | `BRRK-CRYPTO-MULTI-HORIZON-TREND-0074` | Build a simple directional trend benchmark with volatility targeting | 0073 closeout |
| 0075 | `BRRK-CRYPTO-CROSS-SECTIONAL-FACTOR-ATLAS-0075` | Point-in-time factor atlas with explicit multiple-testing control | 0074 closeout |
| 0076 | `BRRK-CRYPTO-CROSS-SECTIONAL-LS-0076` | Convert only validated 0075 factors into a long/short sleeve | 0075 PASS closeout |
| 0077 | `BRRK-CRYPTO-OPTIONS-STATE-VRP-ATLAS-0077` | Characterize IV/RV, skew, term structure and volatility state | 0076 closeout |
| 0078 | `BRRK-CRYPTO-OPTIONS-VOLATILITY-SLEEVE-0078` | Test risk-capped volatility/option structures | 0077 PASS closeout |
| 0079 | `BRRK-CRYPTO-STATE-VECTOR-INTEGRATION-0079` | Build a low-dimensional market-state vector for gating/sizing | 0078 closeout |
| 0080 | `BRRK-CRYPTO-MULTI-SLEEVE-PORTFOLIO-BASELINE-0080` | Equal-risk / inverse-vol / correlation-adjusted portfolio baselines | >=3 economically distinct validated sleeves and 0079 closeout |
| 0081 | `BRRK-CRYPTO-META-ALLOCATOR-0081` | Test regime allocator only against frozen simple baselines | 0080 PASS closeout |
| 0082 | `BRRK-CRYPTO-MULTI-STRATEGY-FINAL-ROBUSTNESS-0082` | Portfolio-level stress, concentration, cost and execution-readiness research | 0081 closeout or prospectively declared 0080 fallback |

Serialization is intentional. It reduces simultaneous hypothesis generation and ensures later decisions can cite immutable earlier results instead of silently changing them.

---

## 3. Universal lifecycle contract for every ID

### Stage 1 — OWNER-FIRST

Before introducing the governed research path:

1. Append a new entry to `config/research_registry.json`.
2. Freeze research ID, family, domain, objective, question, hypothesis, mechanism, primary target/metric, universe, allowed input families, variant budget, stopping rule, allowed/forbidden follow-up and production authority.
3. Set `created_before_result=true`, `actual_variants_evaluated=0`, and prospective provenance.
4. Register governed path prefixes.
5. Merge OWNER-FIRST before DESIGN.

No history/evidence content specific to the new experiment may be read in OWNER-FIRST.

### Stage 2 — DESIGN

DESIGN must specify, before controlled historical access:

1. economic question and falsifiable hypothesis;
2. exact upstream immutable lineage;
3. data families and point-in-time timestamp semantics;
4. universe construction;
5. signal/controller/portfolio families allowed;
6. candidate-budget ceiling;
7. chronological split and maturation semantics;
8. cost and execution model families;
9. metrics and robustness families;
10. evidence tier and limitations;
11. classification vocabulary;
12. failure/stop conditions;
13. no-drift and zero-production authority.

DESIGN may not report new historical performance.

### Stage 3 — PREREGISTRATION

Freeze all numerical/data/analysis semantics before implementation is allowed to read controlled historical evidence:

1. exact artifact/blob/SHA identities;
2. exact row/time alignment and anti-lookahead rules;
3. candidate lists and count;
4. formula definitions;
5. transaction-cost assumptions and stress multipliers;
6. rebalance convention;
7. estimator fitting/re-fitting schedule;
8. bootstrap/PBO/DSR definitions and random seeds;
9. pass/fail/inconclusive/invalid gates;
10. synthetic qualification regimes;
11. expected physical execution accounting;
12. exactly-once read and result-persistence rules.

Any change to a scientific parameter after PREREGISTRATION requires a new research ID unless it is a semantics-preserving implementation correction discovered before attempt consumption and explicitly proven not to change the frozen contract.

### Stage 4 — IMPLEMENTATION

Implement only the preregistered calculations. Requirements:

1. deterministic ordering;
2. no hidden network access;
3. input counters;
4. fit/reconstruction/rebalance counters;
5. create-only result writers;
6. explicit invalid-execution conversion for identity/accounting drift;
7. no production API path;
8. unit/synthetic fixtures covering every terminal classification.

### Stage 5 — NONHISTORICAL QUALIFICATION

Run synthetic or constructed fixtures that require zero controlled history/evidence reads. Qualification must prove:

1. exact PASS fixture;
2. each scientific FAIL fixture;
3. insufficient-support/inconclusive fixture where applicable;
4. identity/hash mismatch -> INVALID_EXECUTION;
5. missing data / NaN / alignment fault handling;
6. cost application accounting;
7. candidate/trial count accounting;
8. result branch does not exist;
9. controlled attempt remains `0/1`.

### Stage 6 — CONTROLLED BOUNDARY

Create a separate merged boundary that pins:

- exact qualified implementation head;
- exact preregistration/qualification blobs;
- all allowed controlled source blobs;
- execution interface;
- expected read/fit/candidate accounting;
- unique result branch name;
- no-rerun rule;
- zero production/signature/order authority.

### Stage 7 — ZERO-RESULT PREFLIGHT

Run only on exact merged-boundary HEAD. It may inspect Git identities but must read zero controlled scientific/history payload content. It must verify:

1. exact HEAD and pinned blob identity;
2. result branch absent;
3. `RUN_ATTEMPT.marker`, `PRIMARY_RESULT`, `EVIDENCE`, `EXECUTION`, `RUN_ONCE` absent;
4. controlled-history reads=0;
5. network fetches=0;
6. attempt consumed=0;
7. production authority=false.

### Stage 8 — ONE CONTROLLED DEVELOPMENT-HISTORY ATTEMPT

Requires explicit user authorization after preflight PASS.

Ordered execution:

1. rerun zero-result identity-only preflight;
2. create durable `RUN_ATTEMPT.marker` with boundary SHA/workflow ID/attempt=1;
3. push marker to unique result branch and verify remote durability;
4. only then read each permitted controlled input at its preregistered maximum count;
5. execute the frozen computation once;
6. persist `PRIMARY_RESULT.json`, `EVIDENCE.json`, `EXECUTION.json` create-only;
7. hash-bind result bundle to attempt marker;
8. marker-only finalize with zero scientific reread;
9. persist `RUN_ONCE.marker`;
10. verify zero production authority.

Once step 3 succeeds, attempt is `1/1 consumed` even if later scientific or execution output is FAIL/INCONCLUSIVE/INVALID.

### Stage 9 — RESULT

Open a result-only PR. No recomputation. Standing CI must pass on exact PR head. Result PR records the persisted classification and execution accounting. Merge only immutable output.

### Stage 10 — IMMUTABLE CLOSEOUT

Separate closeout PR after RESULT merge. It records:

- terminal classification;
- attempt 1/1 consumed;
- scientific/economic evidence within scope;
- failed gates and limitations;
- exact execution accounting;
- no-rerun/no-retune/no-rescue/no-recomputation;
- zero production authority;
- exact legal next step/new-ID dependency.

---

## 4. Universal data and anti-leakage contract

Every ID must preregister these rules as applicable:

1. **Point-in-time universe:** membership is determined only from information available at rebalance time. Delisted/dead assets remain in historical universe where they were then tradable.
2. **Timestamp normalization:** source event time, exchange time and calculation time are separately represented. No future-effective metadata may leak backward.
3. **As-of joins:** every feature at decision time `t` uses observations whose publication/availability timestamp is `<= t`.
4. **Maturity barrier:** labels/returns requiring future sessions are not considered mature until the full horizon exists.
5. **No revised-history substitution:** if source revisions exist, point-in-time snapshots are preferred; otherwise revision risk is explicitly classified.
6. **Corporate/token events:** redenominations, migrations, forks, token swaps, staking rewards and delistings require preregistered treatment.
7. **Stable/wrapped duplicates:** excluded from directional cross-sectional universe unless the ID explicitly studies them.
8. **Venue survival:** exchange data are not selected only from venues surviving to the end of sample.
9. **Missingness is information:** no forward fill beyond preregistered maximum staleness.
10. **No network fetch during controlled attempt:** inputs must be pinned before the boundary.

---

## 5. Universal portfolio/economic accounting

For every strategy-producing ID, calculate in this order:

1. decision-time signal/controller state;
2. target exposure before risk scaling;
3. volatility/risk scaling if allowed;
4. gross/net exposure caps;
5. turnover from previous executable position;
6. execution price convention;
7. explicit fees;
8. spread/slippage;
9. funding/basis cash flows if applicable;
10. borrow/collateral/opportunity cost if applicable;
11. hedge/rebalance cost if applicable;
12. net period PnL;
13. NAV path;
14. exposure and turnover diagnostics;
15. drawdown/tail diagnostics;
16. annualized and regime metrics;
17. bootstrap/multiple-testing diagnostics;
18. concentration diagnostics;
19. cost break-even;
20. final frozen classification.

Cost scenarios are always separated:

- `C0_THEORETICAL`: mechanical gross reference only; never sufficient for PASS.
- `C1_REALISTIC`: preregistered base fee/spread/slippage/financing assumptions.
- `C2_STRESSED`: pessimistic cost and execution conditions.
- sensitivity: `0.5x / 1x / 2x / 3x` base variable cost where meaningful.

A strategy that exists only at C0 cannot PASS economic validity.

---

## 6. Universal economic metrics

Where meaningful, persist all of:

- total and annualized return/CAGR;
- annualized volatility;
- Sharpe and Sortino;
- maximum drawdown and Calmar;
- downside deviation;
- gross/net/average exposure;
- turnover and rebalance/switch count;
- transaction-cost drag and financing drag;
- cost break-even multiplier;
- worst 1/5/10/20-session loss;
- expected shortfall/tail diagnostics defined in preregistration;
- recovery time;
- bull/bear/sideways and high/low-vol regime metrics;
- best/worst year and month;
- asset/venue/regime/trade PnL contribution concentration;
- leave-best-year/asset/regime-out sensitivity;
- marginal portfolio Sharpe, drawdown and tail contribution when a portfolio benchmark exists.

Raw Sharpe alone is never a program PASS criterion.

---

## 7. Universal multiple-testing and robustness contract

Every ID that compares candidates must count all variants, including failed/invalid candidates that reached evaluation.

Preregister as applicable:

1. raw candidate count;
2. family-wise candidate count;
3. selection rule independent of final test segment;
4. Probabilistic Sharpe Ratio;
5. Deflated Sharpe Ratio using the declared trial count and return non-normality;
6. CSCV/PBO when the strategy matrix supports it;
7. moving/block bootstrap for serial dependence;
8. parameter-neighborhood stability rather than isolated optimum;
9. leave-year/regime/asset/venue-out diagnostics;
10. no post-result candidate addition.

Exact numerical gates, block lengths, bootstrap replicate counts and seeds are frozen in each ID's PREREGISTRATION before its controlled attempt. The roadmap intentionally does not retroactively tune those numbers from downstream results.

---

# 8. 0071 — SOL LONG-SIDEWAYS CONTROLLER INTEGRATION

Prospective ID: `BRRK-SOL-LONG-SIDEWAYS-CONTROLLER-INTEGRATION-0071`

## Research question

Does the immutably validated 0070 `P02_RAW_ELASTIC_NET_LOGIT|SOL|T4_LONG_SIDEWAYS`, lead exactly 10 sessions, have incremental **economic risk-control value** when converted into a prospectively frozen SOL exposure controller after realistic/stressed costs, without changing the signal, target, horizon, feature set, model, hyperparameters or 0070 episode definition?

P03/P08 remain one dependent corroborative cluster and may only be used if DESIGN/PREREGISTRATION prospectively defines a corroboration gate; they may not be counted as two independent signals.

## Allowed controller families

DESIGN may choose a bounded candidate set only from these six families:

1. `BINARY_RISK_OFF`: fixed signal-state/percentile threshold -> base exposure or risk-off exposure.
2. `LINEAR_DERISK`: monotone continuous exposure reduction as risk rises.
3. `PIECEWISE_DERISK`: preregistered fixed risk bands with monotone exposures.
4. `VOL_ADJUSTED`: controller multiplied by preregistered volatility-target scaling/cap.
5. `DRAWDOWN_AWARE`: preregistered additional reduction when portfolio drawdown state and warning coexist.
6. `HYSTERESIS`: separate enter/exit risk thresholds to reduce churning.

No family may retrain P02. No controller may optimize on final-period Sharpe.

## Ordered calculation

1. Verify exact 0070 terminal artifacts and hashes.
2. Reconstruct the locked P02 risk score exactly once under pinned code/data identities.
3. Verify exact 0070 full-window signal reproduction before economics.
4. Construct the preregistered SOL base benchmark exposure.
5. Construct each controller exposure deterministically using only information available at each decision time.
6. Apply signal availability lag and trading convention.
7. Apply exposure caps and, if permitted, volatility targeting using lagged realized volatility only.
8. Compute turnover from executable prior exposure.
9. Apply C0/C1/C2 costs and cost multipliers.
10. Compute controller NAVs and benchmark NAV.
11. Compute return, vol, Sharpe, Sortino, MDD, Calmar, downside/tail, exposure, turnover and switch metrics.
12. Compute bear-protection / bull-participation / sideways metrics under prospectively fixed regime definitions.
13. Compute cost break-even.
14. Compute PnL concentration and leave-best-period diagnostics.
15. Run preregistered block bootstrap / DSR / PBO where mathematically admissible.
16. Apply a prospectively frozen **Pareto/non-inferiority** decision rule: controller selection must balance net return retention, drawdown/tail improvement and turnover/cost, not maximize one observed Sharpe.
17. Persist all candidates, not only the winner.
18. Classify PASS/FAIL/INCONCLUSIVE/INVALID_EXECUTION.

## Mandatory limitations

0071 is still development-history economic evidence. A PASS means the frozen warning has reproducible economic controller value under the preregistered historical experiment; it is not independent live proof and creates no production authority.

---

# 9. 0072 — CRYPTO CARRY ATLAS

Prospective ID: `BRRK-CRYPTO-CARRY-ATLAS-0072`

Purpose: establish structural, point-in-time facts before attempting a carry strategy. The initial universe is BTC/ETH/SOL, subject to preregistered data-quality/venue-availability gates.

## Variables

- perpetual funding rate and annualized funding;
- spot-perpetual basis;
- spot-dated-futures annualized basis;
- term-structure slope/curvature where contracts support it;
- cross-venue basis/funding dispersion;
- open interest and OI change;
- volume/liquidity/spread state;
- realized volatility;
- liquidation intensity if point-in-time data qualify;
- price trend/attention proxy only if prospectively frozen.

## Ordered calculation

1. Freeze venue/instrument contract metadata point-in-time.
2. Normalize timestamps and contract units.
3. Construct synchronized spot reference prices without future venue inclusion.
4. Calculate perpetual funding cash-flow convention exactly as the venue defined it at that time.
5. Calculate dated-futures annualized basis using time-to-expiry known at `t`.
6. Calculate cross-venue dispersion and term structure.
7. Build liquidity/OI/volatility/crowding states.
8. Measure carry persistence, transition, mean reversion and dispersion by asset/venue/regime.
9. Test whether extreme carry co-occurs with leverage/crowding and prospectively defined future crash-risk outcomes.
10. Perform asset/venue leave-one-out robustness.
11. Apply multiple-testing correction across the declared atlas hypotheses.
12. Persist the complete atlas and candidate count.
13. PASS only if a prospectively defined structural carry mechanism is reproducible across sufficient assets/venues/regimes; no trading profitability is claimed in 0072.

---

# 10. 0073 — DELTA-NEUTRAL CARRY STRATEGY

Prospective ID: `BRRK-CRYPTO-DELTA-NEUTRAL-CARRY-STRATEGY-0073`

Only immutable 0072 PASS structures may enter candidate definitions.

## Allowed structures

- long spot / short perpetual;
- long spot / short dated future;
- prospectively fixed cross-venue hedge only when custody/transfer assumptions are modeled;
- no unbounded leverage;
- no unhedged directional carry masquerading as market-neutral alpha.

## Ordered calculation

1. Pin 0072 validated carry definitions and venue/instrument universe.
2. Construct hedge ratio and delta-neutral target.
3. Apply venue-specific contract multiplier and margin rules.
4. Apply fees/spread/slippage to both legs.
5. Apply funding receipts/payments exactly at funding timestamps.
6. Apply dated-futures convergence/roll mechanics.
7. Apply borrow, collateral yield/opportunity cost and hedge rebalance cost.
8. Apply margin reserve and conservative liquidation buffer.
9. Compute net carry PnL and residual beta.
10. Reject candidates breaching preregistered directional-beta tolerance.
11. Calculate C1/C2 performance and cost break-even.
12. Stress funding flip, basis compression, volatility spike, cross-venue spread blowout, withdrawal freeze, collateral haircut and stablecoin depeg.
13. Calculate asset/venue concentration and remove-largest-venue sensitivity.
14. DSR/PBO/bootstrap under frozen candidate set.
15. Classify economic PASS only on net, stressed and concentration-aware evidence.

---

# 11. 0074 — MULTI-HORIZON TREND BENCHMARK

Prospective ID: `BRRK-CRYPTO-MULTI-HORIZON-TREND-0074`

Initial assets: BTC/ETH/SOL. This is intentionally a simple benchmark, not a model-complexity contest.

## Horizon families

DESIGN must freeze a small economic family set such as fast/medium/slow rather than search dozens of near-identical windows. Exact windows and variant budget are preregistered.

Allowed signal forms are limited to simple, auditable trend forms such as past-return sign, moving-average spread or breakout normalized by volatility/ATR. The final allowed forms must be frozen before controlled history.

## Ordered calculation

1. Point-in-time asset eligibility.
2. Lagged trend signal per preregistered horizon family.
3. Normalize signal if allowed by DESIGN.
4. Combine horizon votes using a frozen rule, not final-performance weighting.
5. Estimate lagged realized volatility.
6. Apply volatility target and absolute exposure cap.
7. Apply rebalance cadence and turnover.
8. Apply C0/C1/C2 costs.
9. Calculate per-asset and portfolio NAV.
10. Evaluate whipsaw, trend-crash and gap periods.
11. Evaluate horizon-family neighborhood robustness.
12. Leave-one-asset and leave-regime-out.
13. DSR/PBO/bootstrap for declared variants.
14. Select only by frozen rule; persist all candidates.

---

# 12. 0075 — CROSS-SECTIONAL FACTOR ATLAS

Prospective ID: `BRRK-CRYPTO-CROSS-SECTIONAL-FACTOR-ATLAS-0075`

## Point-in-time tradable universe

PREREGISTRATION must freeze minimum listing age, minimum liquidity/ADV, market-cap or capacity criterion, venue count/quality, stale-price policy, delisting treatment and exclusions. Stablecoins, wrapped duplicates and obviously non-comparable instruments are excluded unless explicitly studied.

## Factor families

Price:
- momentum;
- short-term reversal;
- residual momentum;
- drawdown/recovery state.

Risk:
- realized volatility;
- residual/idiosyncratic volatility;
- market beta;
- downside beta/tail risk if prospectively defined.

Market structure:
- funding;
- basis;
- OI/OI change;
- liquidity/spread;
- volume surprise.

Network/economic state, only where point-in-time definitions are valid:
- transaction/network activity;
- fees/economic usage;
- supply growth/issuance;
- holder concentration;
- TVL/economic activity where semantically comparable.

## Ordered calculation for every factor

1. determine universe at rebalance `t`;
2. obtain only point-in-time available feature values;
3. apply preregistered stale/missing filter;
4. winsorize using cross-sectional rule frozen before history;
5. standardize/rank;
6. optionally residualize against frozen controls (market beta, size, volatility, theme/sector);
7. form Q1–Q5 or other preregistered quantiles;
8. calculate forward returns only after maturity;
9. compute Q5-Q1 return, monotonicity and Spearman rank IC;
10. compute IC distribution/stability by year, bull/bear, high/low vol and liquidity regime;
11. compute turnover/capacity proxies;
12. apply family-wise multiple-testing correction;
13. evaluate leave-year/theme/size-bucket robustness;
14. persist every tested factor definition and trial count;
15. qualify factors for 0076 only under prospectively frozen robustness rules.

Atlas PASS does not imply a deployable long/short strategy.

---

# 13. 0076 — CROSS-SECTIONAL LONG/SHORT SLEEVE

Prospective ID: `BRRK-CRYPTO-CROSS-SECTIONAL-LS-0076`

Only factors immutably qualified in 0075 may be used; no new factor discovery is allowed.

## Ordered calculation

1. pin 0075 factor definitions and point-in-time universe engine;
2. build frozen composite score using preregistered equal/rank/simple fixed weights unless DESIGN justifies a bounded alternative;
3. form long and short baskets;
4. neutralize gross/net market beta under frozen tolerance;
5. apply per-asset, theme and liquidity caps;
6. apply borrow availability and borrow cost to short legs;
7. apply turnover/fees/slippage;
8. calculate capacity and participation-rate sensitivity;
9. compute net portfolio NAV and factor attribution;
10. test factor crowding/correlation and residual market exposure;
11. leave-factor/asset/theme/year/regime-out;
12. DSR/PBO/bootstrap;
13. cost break-even and stressed borrow-unavailable scenario;
14. classify PASS only if relative-value alpha survives realistic and stressed implementation.

---

# 14. 0077 — OPTIONS STATE / VRP ATLAS

Prospective ID: `BRRK-CRYPTO-OPTIONS-STATE-VRP-ATLAS-0077`

Initial underlying universe: BTC/ETH; SOL only if prospectively qualified option-liquidity/history gates are satisfied.

## Variables

- ATM implied volatility;
- realized volatility under frozen horizon match;
- IV-RV / variance risk premium proxy;
- 25-delta or prospectively defined skew;
- term structure;
- vol-of-vol;
- open interest/volume/spread/liquidity;
- jump/tail proxies where definable without lookahead.

## Ordered calculation

1. normalize option contract metadata and expiry calendar;
2. reject stale/illiquid quotes under frozen filters;
3. construct forward/discount convention;
4. derive moneyness/delta consistently;
5. build IV surface points/summaries without future interpolation;
6. align IV horizon to subsequent RV measurement horizon;
7. calculate VRP/skew/term-structure state;
8. characterize persistence and regime transitions;
9. relate option state to prospectively defined subsequent volatility/tail outcomes;
10. maturity/liquidity/venue robustness;
11. multiple-testing correction;
12. atlas PASS only; no naked short-vol profitability claim in 0077.

---

# 15. 0078 — OPTIONS / VOLATILITY SLEEVE

Prospective ID: `BRRK-CRYPTO-OPTIONS-VOLATILITY-SLEEVE-0078`

Only 0077 validated structures may be used.

No uncontrolled naked short-vol strategy is permitted.

## Ordered calculation

1. pin 0077 state definitions and eligible option universe;
2. define bounded option structure and max-loss/risk budget;
3. construct delta/vega exposure at decision time;
4. apply quote-side execution, fees and slippage;
5. perform preregistered delta-hedge cadence if required;
6. include hedge slippage and gap risk;
7. calculate option expiry/exercise/settlement exactly;
8. calculate net VRP/convexity PnL;
9. apply tail hedge or hard loss cap where frozen;
10. stress volatility gap, skew explosion, liquidity withdrawal and hedge failure;
11. separate carry income from jump/tail losses;
12. DSR/PBO/bootstrap and concentration;
13. classify only after stressed net economics.

---

# 16. 0079 — CRYPTO STATE VECTOR INTEGRATION

Prospective ID: `BRRK-CRYPTO-STATE-VECTOR-INTEGRATION-0079`

Purpose: build a low-dimensional information layer, not a new unrestricted predictor search.

Candidate state dimensions, subject to frozen data availability:

- trend: bull / neutral / bear;
- volatility: calm / elevated / crisis;
- leverage/crowding: low / normal / crowded;
- liquidity: expanding / stable / contracting;
- flow/network state: accumulation / neutral / distribution;
- options/tail state: normal / defensive / stressed.

## Ordered calculation

1. pin only inputs validated or separately justified by prior IDs;
2. normalize each dimension with expanding/rolling point-in-time statistics;
3. discretize or continuously scale using frozen thresholds;
4. prohibit outcome-aware relabeling of states;
5. test state persistence and transition matrix;
6. measure conditional behavior of already-frozen sleeves under states;
7. adjust for multiple state comparisons;
8. reduce dimensions only by preregistered deterministic rule;
9. output a state vector suitable for 0080/0081 gating, not direct production signals.

---

# 17. 0080 — MULTI-SLEEVE PORTFOLIO BASELINES

Prospective ID: `BRRK-CRYPTO-MULTI-SLEEVE-PORTFOLIO-BASELINE-0080`

May start only when at least three economically distinct sleeves have immutable valid results. Economically distinct means different primary return mechanism, not merely different parameterizations of momentum.

## Mandatory baseline allocators

1. `EQUAL_RISK`: equal ex-ante risk contribution subject to caps.
2. `INVERSE_VOL`: risk budget inversely proportional to lagged sleeve volatility.
3. `CORRELATION_ADJUSTED`: penalize redundant sleeve exposure using lagged correlation/covariance under frozen estimator.
4. `REGIME_GATED_SIMPLE`: deterministic state gates from 0079; no ML.

## Ordered calculation

1. align immutable sleeve returns on common executable calendar;
2. apply lagged volatility/covariance estimates;
3. generate risk weights with no future information;
4. apply sleeve/portfolio risk caps;
5. calculate rebalance turnover and allocator-level costs;
6. construct portfolio NAV;
7. calculate risk contribution by sleeve;
8. calculate correlation-spike and sleeve-failure stress;
9. marginal Sharpe/MDD/tail contribution per sleeve;
10. concentration and leave-one-sleeve-out;
11. compare simple allocators using frozen rule;
12. establish the benchmark that 0081 must beat.

---

# 18. 0081 — META ALLOCATOR

Prospective ID: `BRRK-CRYPTO-META-ALLOCATOR-0081`

The meta allocator is forbidden until 0080 has frozen simple baselines. Complexity has no presumption of superiority.

DESIGN may allow only a bounded set of allocator families. ML, if allowed at all, must be compared against 0080 baselines on identical inputs, costs and risk budgets.

## Ordered calculation

1. pin immutable sleeves and 0080 baselines;
2. pin 0079 state inputs;
3. define allocator candidates and total trial budget;
4. fit only within preregistered rolling/walk-forward training windows;
5. produce next-period sleeve risk budgets;
6. enforce no-short/no-leverage or other frozen allocator constraints;
7. calculate allocator turnover/cost;
8. compute portfolio NAV and risk contributions;
9. compare against each 0080 simple baseline on identical sample/support;
10. require incremental net value, not merely higher in-sample Sharpe;
11. DSR/PBO/bootstrap with total allocator trial count;
12. leave-regime/sleeve-out and correlation-spike stress;
13. reject meta complexity if it fails to beat the frozen simple baseline robustly.

A valid result may be `PASS_SIMPLE_BASELINE / META_REJECTED`; that is scientifically acceptable.

---

# 19. 0082 — FINAL MULTI-STRATEGY ROBUSTNESS / EXECUTION READINESS RESEARCH

Prospective ID: `BRRK-CRYPTO-MULTI-STRATEGY-FINAL-ROBUSTNESS-0082`

This is research/shadow-readiness, not production authorization.

## Ordered calculation

1. pin the final immutable sleeve set and allocator choice from 0080/0081;
2. reproduce the complete portfolio exactly;
3. verify per-sleeve and portfolio accounting identities;
4. apply C1/C2 and 2x/3x cost stress;
5. exchange/venue failure stress;
6. stablecoin/collateral depeg or haircut stress;
7. funding flip/basis compression stress;
8. borrow unavailable/short recall stress;
9. option liquidity/hedge-gap stress;
10. volatility shock and correlation-to-one stress;
11. stale/missing data and delayed-execution stress;
12. strategy/sleeve disablement stress;
13. PnL concentration and leave-best-period/asset/venue/sleeve-out;
14. portfolio DSR/PBO/bootstrap under declared selection history;
15. capacity/participation-rate sensitivity;
16. turnover and operational event-count accounting;
17. drawdown/recovery/tail diagnostics;
18. persist explicit limitations and evidence tier;
19. terminal research classification;
20. preserve `production_authorized=false`, `signature_authorized=false`, `order_submission_authorized=false` unless a completely separate production-governance process later exists.

---

## 20. Profit-concentration contract

Every economic ID must report at minimum:

- largest year share of total positive PnL;
- largest month share;
- largest asset share;
- largest venue share where applicable;
- largest regime share;
- top-N trade/event contribution where trade-level decomposition exists;
- result after removing best year;
- result after removing best asset/venue/sleeve where mathematically meaningful.

A PASS rule must reject a result whose economic claim is prospectively defined as excessively dependent on one isolated historical contributor.

---

## 21. Capacity and execution contract

Where executable volume matters:

1. use point-in-time ADV/open-interest/liquidity estimates;
2. freeze participation-rate scenarios;
3. model spread/slippage as size-sensitive if data permit;
4. cap exposure before calculating performance;
5. report capacity at which economic edge decays to zero;
6. distinguish exchange matching liquidity from transferable/custodial capital;
7. model settlement/transfer delays where cross-venue arbitrage is claimed;
8. never assume unlimited borrow, margin or instant collateral mobility.

---

## 22. Program stop rules

The program is allowed to stop, skip or branch only through a new prospectively registered ID. Examples:

- 0071 FAIL: do not reinterpret 0070; continue to 0072 only if the program owner prospectively decides independent carry research remains valuable.
- 0072 FAIL: 0073 may not be run from result-informed altered carry definitions; a new ID is required for a changed carry hypothesis.
- 0075 FAIL: 0076 is gated off.
- 0077 FAIL: 0078 is gated off.
- fewer than three independent valid sleeves: 0080/0081 cannot claim a diversified multi-strategy portfolio.
- 0081 fails to beat 0080: retain the simple baseline; do not tune the meta allocator after result.
- any `INVALID_EXECUTION` after attempt consumption: close immutably; no same-ID rescue.

A failed hypothesis is a valid research outcome. The roadmap must not force continuation by relaxing gates.

---

## 23. Program progress accounting

Each research ID has exactly 10 formal lifecycle stages. No partial credit is assigned inside a stage.

For reporting:

- active-ID completion = completed formal stages / 10;
- program-ID completion = immutably closed IDs / planned eligible IDs;
- gated/skipped IDs are reported explicitly, not counted as successful;
- no subjective percent-complete estimates;
- no time-to-terminal-result ETA is inferred from GitHub status.

---

## 24. Immediate serial execution plan after 0070

The exact legal order from the current 0070 result state is:

1. merge 0070 immutable RESULT bundle only after exact-head standing CI is green;
2. create separate 0070 IMMUTABLE CLOSEOUT branch/PR with no scientific reread or recomputation;
3. merge closeout only after exact-head standing CI is green;
4. only then register 0071 OWNER-FIRST in `config/research_registry.json`;
5. create 0071 DESIGN PR;
6. after DESIGN merge, create numerical/data/analysis PREREGISTRATION;
7. after PREREGISTRATION merge, implement only frozen semantics;
8. qualify nonhistorically with zero controlled-history reads;
9. merge separate CONTROLLED BOUNDARY;
10. run exact merged-boundary ZERO-RESULT PREFLIGHT;
11. stop and request explicit authorization for irreversible attempt 1/1;
12. after authorization, create durable attempt marker before any controlled read and execute exactly once;
13. result-only PR;
14. separate immutable closeout;
15. proceed to 0072 OWNER-FIRST only if permitted by the immutable 0071 terminal state and this roadmap's dependency rules.

Repeat the identical 10-stage lifecycle for every subsequent eligible ID.

---

## 25. What this roadmap does not authorize

This document does **not** itself:

- register OWNER-FIRST for 0071 or any later ID;
- authorize a historical/development-history attempt;
- authorize network acquisition during a controlled attempt;
- authorize production, signatures or orders;
- authorize hidden parameter search;
- turn Reddit/X/community ideas into evidence;
- guarantee that 0071–0082 will all be run;
- override an immutable FAIL/INCONCLUSIVE/INVALID result;
- permit same-ID rescue.

Community sources may generate hypotheses before OWNER-FIRST, but scientific claims and formal priors must be grounded in pinned data, prospectively frozen analysis and reproducible primary evidence.

---

## 26. Terminal program objective

A successful research program would not mean that every sleeve has high standalone Sharpe. It would mean that the repository has prospectively tested whether several **economically different** mechanisms—risk timing, derivative carry, directional trend, cross-sectional relative value and volatility state/option risk premia—survive realistic implementation and whether their combination adds marginal portfolio value without hidden dependence on one market regime, asset, venue or backtest-selection process.

The preferred final architecture is therefore:

`validated sleeves -> simple risk-allocation baselines -> optional meta allocator -> portfolio-level stress/robustness -> immutable research closeout`

not:

`more indicators -> more parameter search -> highest historical Sharpe`.
