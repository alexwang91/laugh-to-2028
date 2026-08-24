# 0076 Stage3 PREREGISTRATION — single cross-sectional momentum long/short baseline

Research ID: `BRRK-CRYPTO-CROSS-SECTIONAL-LS-0076`

Lifecycle stage: `3/10 PREREGISTRATION`.

Parent Stage2 merge: `3d2a91558a1829314541f66304a5c463b164ef1c`.

Controlled attempt: `0/1`; controlled scientific/history reads: `0`; scientific engine calls: `0/1`; scientific source-network fetches: `0`; scientific values exposed: `false`.

This document freezes the complete numerical/data/analysis semantics before implementation and before any 0076 controlled scientific/history read. 0076 uses DEVELOPMENT history only and never claims independent OOS evidence.

## 1. Frozen route, hypothesis and candidate count

The Stage2 route is irrevocably fixed to:

`SEPARATELY_JUSTIFIED_BASELINE_FAMILY -> CROSS_SECTIONAL_MOMENTUM_SINGLE_BASELINE`.

Exactly one candidate is permitted. The scientific hypothesis is that a simple point-in-time cross-sectional 60-session price-momentum ranking may produce positive, economically implementable, beta-neutral relative-value returns across crypto perpetuals after realistic funding and trading costs.

No reversal, carry, funding-selection, basis, volatility, liquidity, network, residual-momentum, composite, ensemble, alternate lookback, alternate rebalance cadence, alternate sign or post-result candidate may be evaluated under 0076.

Declared candidate/trial count = exactly `1`.

## 2. Frozen source contract and zero-result cache identities

The only admissible controlled market source is the pre-existing zero-scientific-value Binance public archive staging cache created for 0075 Stage6. Reuse is source-byte/cache reuse only. It transfers no 0075/0084 factor result, lifecycle credit or scientific conclusion.

Pinned parent identities:

- official source host/family: `data.binance.vision` public archive;
- parent authorized-object manifest path: `research/brrk_crypto_cross_sectional_factor_atlas_0075/AUTHORIZED_OBJECT_MANIFEST.json`;
- manifest Git blob: `74b119149e55c6c7a4fc641840b07c24bb27644a`;
- manifest SHA-256: `2f70384dd84a601b69528ef3d770e0fa9c714b3e0888bec009e93b5067ecebf8`;
- parent symbol-universe path: `research/brrk_crypto_cross_sectional_factor_atlas_0075/STAGE6_SYMBOL_UNIVERSE.json`;
- symbol-universe Git blob: `45c07672c6404593279333ec1995c0ae0203eed3`;
- symbol-universe SHA-256: `85337b0681d4e61fc60eef62f4f05b2ea6e43f7da9e7648b4d94032794f95dbd`;
- staging evidence blob: `7d60ae77439e6baad385a7114c5a487f0faaa3f2`;
- staging workflow run: `32646565505` = terminal `SUCCESS`;
- artifact id/name: `9495175701` / `0075-stage6-authorized-payloads-v1`;
- declared retention: `90` days;
- parent candidate symbols: `652`;
- parent authorized opaque payload objects: `53,541`;
- parent hash verification: `53,541/53,541`;
- parent offline ZIP structural readability: `53,541/53,541`;
- scientific values exposed during staging: `false`;
- controlled scientific/history reads used during staging: `0`.

0076 does **not** authorize all parent objects for scientific parsing. Stage6 must deterministically derive and persist an exact 0076 sub-manifest from the pinned parent manifest using object-path identity only, selecting only:

1. USD-M monthly daily perpetual kline objects for eligible `*USDT` symbols; and
2. USD-M monthly `fundingRate` objects for those symbols;
3. source months `2021-01` through `2026-07`, inclusive.

Paired checksum/object hashes remain binding. Stage6 must persist exact selected object paths, hashes and count before Stage7. Stage7 may verify identities/availability/readability but may not parse any scientific rows. Stage8 source-network fetches are exactly `0`; if the bound artifact is unavailable or an authorized object cannot be read, same-ID network refetch/substitution is forbidden.

## 3. Time, decision and execution chronology

All source timestamps normalize to UTC. Rebalance decisions occur at **Monday 00:00 UTC calendar date `t`**, with execution at the close of that Monday daily bar.

At a Monday rebalance `t`:

- every signal/universe/beta/liquidity input may use data only through close `t-1` (Sunday UTC);
- no Monday close or later information may affect the position executed at Monday close;
- positions are established at Monday close and held with fixed contract notional weights until the next Monday close;
- daily mark-to-market between rebalances uses realized perpetual close-to-close returns and funding cash flows without intraperiod re-optimization;
- the last holding interval is included only if the full next-Monday close and all required realized data exist.

Candidate source months are `2021-01` through `2026-07`. No history extension is permitted under this ID.

## 4. Point-in-time perpetual universe

At rebalance `t`, a USD-M USDT-margined perpetual symbol is eligible only if all information available through `t-1` satisfies:

1. symbol ends in `USDT` and is present in the pinned Stage6 symbol identity universe;
2. at least `180` calendar days have elapsed since its first admissible archived USD-M daily perpetual bar;
3. each of the previous `61` expected UTC daily closes needed for momentum is present, finite and positive;
4. at least `45` paired daily returns exist in the prior `60` observations for beta estimation;
5. trailing `30`-day median USD-M daily quote-volume is finite and at least `USD 1,000,000`;
6. latest admissible daily close is exactly `t-1`, so stale instruments are excluded;
7. the base symbol is not an obvious stablecoin/fiat proxy, leveraged-token wrapper, wrapped duplicate or tokenized non-crypto equity/commodity identifier under the static Stage4 denylist frozen from symbol identity only;
8. no future survival/delisting state may determine earlier membership.

At least `30` eligible symbols must exist on a rebalance date. Otherwise that rebalance is prospectively unsupported and creates no position.

Stage4 must encode the exact static denylist in version-controlled code before qualification. Stage5 must verify the denylist only against synthetic/symbol-identity fixtures, not scientific history.

## 5. Single frozen momentum score

For symbol `i` at Monday rebalance `t`:

`MOM60_i(t) = ln(close_i(t-1) / close_i(t-61))`.

Requirements:

- both closes must be finite and positive;
- no winsorization;
- no residualization;
- no sign flip;
- no alternate window;
- no skip interval beyond the causal `t-1` endpoint;
- sort descending by `MOM60`; ties use lexical symbol ascending as deterministic secondary key.

## 6. Frozen basket construction

On each supported rebalance date:

1. sort all eligible symbols by `MOM60` descending;
2. long set = highest `20%` using `floor(0.20*N)` constituents;
3. short set = lowest `20%` using `floor(0.20*N)` constituents;
4. require at least `6` symbols in each leg;
5. initialize raw weights `+0.5/n_long` on long names and `-0.5/n_short` on short names;
6. no name may enter both legs;
7. symbols between the two tails receive zero weight.

Raw portfolio gross exposure = `1.0`; raw net dollar exposure = `0.0`.

## 7. Frozen lagged beta-neutral projection

Asset beta at `t` is OLS slope over the previous `60` daily observations ending `t-1`, regressing each asset daily log return on the equal-weight return of the contemporaneously eligible cross-section for each historical day. At least `45` paired rows are required.

Let raw selected-tail weights be vector `u`, selected asset beta vector `b`, and matrix `A` have rows `[1,1,...]` and `b`. Compute the minimum-L2 equality projection:

`w* = u - A' (A A')^{-1} A u`.

Then rescale `w*` to gross exposure exactly `1.0` by dividing by `sum(abs(w*))`, preserving both equality constraints.

The rebalance is unsupported rather than repaired if:

- `A A'` is singular/non-finite;
- any originally long weight becomes `<=0`;
- any originally short weight becomes `>=0`;
- any absolute asset weight exceeds `0.10` after gross rescaling;
- absolute net dollar exposure exceeds `1e-10`;
- absolute residual beta `abs(sum(w_i * beta_i))` exceeds `1e-10`.

No optimizer, shrinkage, hedge overlay or alternate neutralization method is allowed.

## 8. Position holding and turnover

Weights are target notional fractions of portfolio NAV at Monday close. Between Monday closes, contract notionals are held fixed except for cash funding flows; there is no daily rebalance to target weights.

At the next Monday close, realized pre-trade drifted weights are computed from marked contract notionals and NAV. Target turnover is:

`turnover_t = 0.5 * sum_i(abs(target_weight_i(t) - pretrade_weight_i(t)))`.

Entry from cash uses prior risky weights all zero. Exit at the terminal supported end is included in turnover/cost accounting.

## 9. Perpetual funding and trading costs

Funding cash-flow sign convention for portfolio weight `w` and archived funding rate `f` is `-w*f`: a positive funding rate costs a long and benefits a short.

C0/C1/C2 are frozen:

- `C0_THEORETICAL`: no trading-cost deduction and no funding cash flow; diagnostic only, never sufficient for PASS.
- `C1_REALISTIC`: actual archived funding cash flow plus `10 bps` cost for each unit of absolute notional weight traded, i.e. `0.0010 * sum(abs(delta_weight))` at each rebalance/entry/exit.
- `C2_STRESSED`: adverse funding transform plus `30 bps` per unit absolute notional traded. For each realized funding contribution, negative C1 funding PnL is multiplied by `2.0`; positive C1 funding PnL is multiplied by `0.5`.

Cost-sensitivity multipliers on the C1 `10 bps` variable trading cost are exactly `0.5x`, `1x`, `2x`, `3x`, with actual C1 funding unchanged for this sensitivity diagnostic. Cost break-even multiplier is the largest nonnegative variable-cost multiplier at which full-history net cumulative return is `>=0`, solved analytically from gross-before-variable-cost and total absolute traded notional where defined.

No borrow cost is charged because both long and short legs are implemented as USD-M perpetual positions, not borrowed spot. `BORROW_AVAILABILITY_STRESS = NOT_APPLICABLE_BY_FROZEN_INSTRUMENT_DESIGN`; this is not a post-result waiver. Funding and perpetual-source availability are the applicable financing/executability constraints.

## 10. Daily NAV and economic metrics

The scientific engine must persist daily C0/C1/C2 NAV paths and at least:

- cumulative return and CAGR;
- annualized volatility using `sqrt(365)`;
- annualized Sharpe using zero risk-free rate and daily net returns;
- Sortino with zero target return;
- maximum drawdown and Calmar;
- worst `1/5/10/20`-day compounded return;
- 5% expected shortfall of daily returns;
- gross/net exposure and residual beta;
- turnover per rebalance and annualized turnover;
- funding PnL, variable trading-cost drag and total cost drag;
- cost break-even multiplier;
- selected-asset and absolute PnL contribution concentration;
- capacity/participation diagnostics described below.

No leverage or return smoothing is permitted.

## 11. Capacity and concentration

Capacity diagnostic normalizes portfolio NAV to `USD 1,000,000` at each rebalance only for participation measurement. For each traded asset, participation proxy is absolute target notional change divided by its trailing-30-day median USD-M daily quote volume available at `t-1`.

PASS support requires:

- `95th` percentile participation across all asset/rebalance trades `<= 1%`;
- maximum participation `<= 5%`.

Concentration uses signed asset cumulative C1 PnL contributions. Let absolute contribution share be `abs(asset_contribution)/sum(abs(all_asset_contributions))`. PASS requires maximum absolute contribution share `<= 35%` and C1 cumulative return after removing the single largest absolute-contribution asset remains `>0`.

## 12. Regime and leave-out partitions

Frozen partitions use only lagged information:

- calendar year;
- market trend: 60-session equal-weight eligible-universe return through `t-1` `>=0` bull, `<0` bear;
- market volatility: equal-weight universe 20-session realized volatility above/below its expanding historical median available through `t-1`;
- market liquidity: cross-sectional median trailing-30-day quote volume above/below its expanding historical median available through `t-1`.

A partition is supported only with at least `26` realized weekly holding intervals. Calendar-year robustness requires at least `13` realized weekly intervals in that year. Leave-one-year-out is required only when at least `3` calendar years meet that support rule.

Theme leave-out is `NOT_EVALUATED` because no point-in-time theme taxonomy is frozen. This status is preregistered and cannot change after history exposure.

## 13. Dependence-aware inference

Primary inferential series is the C1 daily net return series.

Moving-block bootstrap:

- block length: `20` daily observations;
- replicates: exactly `4,000`;
- deterministic seed: `760076`;
- bootstrap unit: contiguous daily return blocks with circular start indexing;
- primary one-sided p-value: fraction of bootstrap mean-return draws `<=0`, with plus-one correction `(count+1)/(4000+1)`;
- 95% bootstrap confidence interval uses empirical `2.5%` and `97.5%` quantiles.

PSR uses benchmark Sharpe `0`, daily observations and sample skew/kurtosis. DSR uses declared trial count exactly `1`; with one candidate there is no multiple-candidate search correction beyond the single-trial PSR/DSR formula.

CSCV/PBO = `NOT_EVALUATED_SINGLE_CANDIDATE` and must not be fabricated from parameter variants.

## 14. Minimum scientific support

A valid economic classification other than support-based INCONCLUSIVE requires all:

- at least `730` valid C1 daily return observations;
- at least `104` completed supported weekly holding intervals;
- at least `3` supported calendar years with `>=13` weekly intervals each;
- median eligible universe size across supported rebalances `>=30`;
- median long and short constituent count each `>=6`;
- at least one supported bull and one supported bear partition, each `>=26` weekly intervals.

If these fail after otherwise valid execution, classification is `INCONCLUSIVE_INSUFFICIENT_SUPPORT`, not FAIL and not a trigger to change the universe/window.

## 15. Frozen PASS gates

After minimum support passes, 0076 `PASS` requires every gate:

G0. Execution accounting is valid; exactly one candidate is persisted; scientific engine calls exactly `1`; Stage8 scientific source-network fetches exactly `0`; every authorized controlled object is read no more than once.

G1. C1 full-history CAGR `>0` and annualized Sharpe `>=0.50`.

G2. C1 bootstrap one-sided p-value for mean daily return `<=0.05` and the 95% bootstrap lower confidence bound for mean daily return is `>0`.

G3. PSR and one-trial DSR are both `>=0.95`.

G4. C2 stressed full-history CAGR `>0` and annualized Sharpe `>0`.

G5. Cost break-even multiplier is `>=2.0x` the C1 variable trading cost.

G6. At least `60%` of supported calendar years have positive C1 cumulative return, and both supported bull and bear partitions have positive C1 cumulative return.

G7. Every supported leave-one-year-out omission has positive C1 cumulative return; median leave-one-year-out Sharpe is at least `50%` of full-history C1 Sharpe.

G8. Mechanical neutrality holds on every traded rebalance within the `1e-10` net-dollar and residual-beta tolerances; no selected asset breaches the `0.10` absolute-weight cap.

G9. Capacity participation requirements in Section 11 both pass.

G10. Maximum absolute asset PnL contribution share is `<=35%` and remove-largest-contributor C1 cumulative return remains `>0`.

G11. C1 maximum drawdown is greater than `-50%` and worst 7-calendar-day compounded C1 return is greater than `-25%`.

No single metric, including raw Sharpe, can override a failed gate.

## 16. Terminal classifications

Exactly one terminal scientific classification is persisted:

- `PASS_CROSS_SECTIONAL_MOMENTUM_LS_BASELINE`: valid exactly-once execution, minimum support passes, and G0-G11 all pass.
- `FAIL_NO_ROBUST_CROSS_SECTIONAL_MOMENTUM_LS_ECONOMICS`: valid exactly-once execution and minimum support passes, but at least one G1-G11 gate fails.
- `INCONCLUSIVE_INSUFFICIENT_SUPPORT`: identities/accounting are valid but Section 14 support is insufficient or a preregistered required statistic is mathematically undefined because support is insufficient.
- `INVALID_EXECUTION`: any identity/hash/read-count/lookahead/source/universe/candidate-count/neutralization/cost/funding/persistence/exactly-once drift.

Disappointing performance is FAIL, not INCONCLUSIVE. Execution defects are INVALID, not FAIL. No post-result rescue or alternate baseline is allowed.

## 17. Stage4/Stage5 implementation-completeness obligations

Before Stage6, implementation and nonhistorical qualification must demonstrate on synthetic fixtures a complete end-to-end callable that accepts staged-object-equivalent rows and executes all of:

1. source/path/schema validation;
2. point-in-time universe construction;
3. MOM60 score;
4. deterministic ranking/tails;
5. rolling beta computation;
6. exact beta-neutral projection and unsupported-state handling;
7. fixed-notional between-rebalance accounting;
8. funding cash flows;
9. C0/C1/C2 costs;
10. daily NAV/metrics;
11. bootstrap/PSR/DSR;
12. regime and leave-year-out diagnostics;
13. capacity/concentration diagnostics;
14. G0-G11 evaluation;
15. all four terminal classifications;
16. create-only result serialization interface;
17. execution counters proving exactly one scientific-engine entrypoint call and no hidden second call.

Stage5 must include a synthetic case that reaches PASS and cases reaching FAIL, INCONCLUSIVE and INVALID_EXECUTION. Stage7 cannot PASS if Stage8 would require any new adapter/harness/scientific implementation.

## 18. Exactly-once controlled execution budget

Stage8 budget is exactly one controlled attempt. After Stage7 PASS and fresh exact-scope contemporaneous user authorization:

1. rerun identity-only zero-result preflight;
2. durably create and remotely verify `RUN_ATTEMPT.marker` before first controlled scientific content read;
3. read each Stage6-authorized nested payload object at most once;
4. invoke the single frozen scientific engine entrypoint exactly once;
5. perform scientific source-network fetches exactly zero times;
6. persist `PRIMARY_RESULT.json`, `EVIDENCE.json`, `EXECUTION.json` create-only;
7. hash-bind the bundle to the attempt marker;
8. finalize with zero scientific reread;
9. create `RUN_ONCE.marker`.

Attempt becomes permanently `1/1 consumed` when the durable attempt marker is remotely verified, regardless of later PASS/FAIL/INCONCLUSIVE/INVALID outcome.

After marker durability: no rerun, retune, rescue, alternate universe, alternate lookback, source substitution, history extension, candidate replacement or recomputation.

## 19. Production authority

`production_authorized=false`

`signature_authorized=false`

`order_submission_authorized=false`

## 20. Exact next step

After Stage3 merge, Stage4 must implement this exact one-candidate contract only. No controlled scientific/history payload may be opened during implementation or qualification.