# BRRK-SIMPLE-ETH-SOL-BETA-ROUTER-0056

Status: **INVALID_EXECUTION / CLOSED / NO ECONOMIC CONCLUSION**

0056 is a new direct portfolio-economics mechanism study. It is not a rerun or rescue of 0048, 0053, 0054 or 0055.

## Frozen candidate

Exactly one candidate exists:

```text
z_t = log(SOL_t / ETH_t)
RM60_t = z_t - z_(t-60)
RM60_t > 0  -> hold SOL next period
RM60_t < 0  -> hold ETH next period
RM60_t = 0  -> retain prior holding
first-origin exact-zero fallback -> ETH
```

Signal information ends at the completed UTC daily close at origin `t`; the selected asset receives only the next close-to-close `t -> t+1` return. No same-period return is used to choose the target.

The Beta sleeve is fully invested in exactly one of ETH or SOL. BTC, cash timing, CORE4, leverage, shorting and probability models are outside 0056.

## Frozen data and evaluation window

```text
source slice          BRRK-LEADERSHIP-ROTATION-0048-EXPOSED-HIST-V1
payload SHA256        d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193
source common rows    2183 daily UTC rows
source window         2020-08-11 through 2026-08-02
first signal origin   2020-10-10
last signal origin    2026-08-01
terminal close        2026-08-02
held periods          2122
contamination         RESEARCHER_EXPOSED_HISTORY
independent OOS       false
```

No network fetch, replacement dataset, synthetic fill or post-2026-08-02 history is allowed.

## Frozen benchmarks

- `B0_STATIC_ETH`: one initial 100% ETH entry, then buy-and-hold.
- `B1_STATIC_SOL`: one initial 100% SOL entry, then buy-and-hold.
- `B2_STATIC_50_50`: one initial 50/50 ETH/SOL allocation, then both sleeves compound independently with **no periodic rebalancing**.

All arms start from NAV 1.0 and share the identical 2122 held periods.

## Frozen costs

Executed L1 turnover is charged before the next held return:

`cost = pre_trade_NAV * executed_L1_turnover * cost_bps / 10000`.

```text
primary cost          5 bps / unit L1
stress costs          10 and 20 bps / unit L1
initial entry L1      1
full ETH<->SOL switch 2
unchanged holding L1  0
```

There is no inherited 5% rebalance band in 0056. Router trading occurs only when the frozen RM60 sign rule changes the target.

## Primary economic objective

Primary endpoints are net terminal wealth and net CAGR. CAGR uses the exact 2122-calendar-day span and annualization `365.25 / 2122`.

At 5 bps the router must strictly beat **all three** static benchmarks. The same strict all-three dominance is required independently at both 10 bps and 20 bps.

`max(B0,B1,B2)` is a comparison envelope, not an executable hindsight-switching portfolio.

## Frozen chronological robustness

The 2122 evaluation origins are split mechanically into four contiguous equal-count blocks:

```text
T1  2020-10-10..2022-03-24   531 periods
T2  2022-03-25..2023-09-06   531 periods
T3  2023-09-07..2025-02-17   530 periods
T4  2025-02-18..2026-08-01   530 periods
```

At 5 bps, `B_STAR` is the single static benchmark with the largest **full-horizon** terminal wealth. Exact ties resolve B0 -> B1 -> B2. The router must have positive block relative log growth versus this same `B_STAR` in at least 3 of 4 blocks. Blocks use the global no-reset NAV paths; there are no artificial block-entry costs or block-start rebalancings.

## Frozen dependence-aware inference

At 5 bps only, define aligned daily paired log-growth differentials:

`d_(b,t) = log(g_router,t) - log(g_b,t)` for each static benchmark `b`.

The bootstrap is frozen as:

```text
ordinary moving blocks     60 ordered daily periods
replicates                 10000
seed                       1844716895
seed derivation            first 8 hex digits 6df4255f of SHA256(research_id)
block starts               0..2062 inclusive
blocks drawn/replicate     36
final length               truncate concatenation to 2122 rows
pairing                     identical sampled row indices for B0/B1/B2
quantile                    Type 7 / NumPy linear
```

For each replicate `r`, compute `T_r = max_b(mu_b - mu_star_(b,r))`. Let `q95` be its 95th percentile and define simultaneous one-sided lower bounds `LCB_b = mu_b - q95`. The dependence-aware gate requires **all three `LCB_b > 0`**.

No bootstrap replicate retrains, retunes or recomputes the signal path.

## Frozen classification hierarchy

```text
G0 integrity failure
 -> INVALID_EXECUTION

G0 pass, G1 5bps all-static dominance fail
 -> FAIL_NO_SIMPLE_BETA_ROUTER_ECONOMIC_UPLIFT

G0-G1 pass, G2 10/20bps cost survival fail
 -> FAIL_SIMPLE_BETA_ROUTER_COST_FRAGILE

G0-G2 pass, G3 3-of-4 temporal gate fail
 -> FAIL_SIMPLE_BETA_ROUTER_TEMPORALLY_CONCENTRATED

G0-G3 pass, G4 simultaneous bootstrap LCB fail
 -> FAIL_SIMPLE_BETA_ROUTER_ECONOMIC_UPLIFT_NOT_DEPENDENCE_ROBUST

G0-G4 all pass
 -> PASS_SIMPLE_BETA_ROUTER_ECONOMIC_ELIGIBILITY
```

MDD, turnover, switch count, holding durations, calendar-year returns and longest underperformance interval are mandatory diagnostics but have no rescue authority.

## Stop rule

A valid 0056 result permanently closes this ID to rerun, retuning or rescue.

If 0056 fails, stop the ETH/SOL micro-timing line. Do not open a 30d/90d/MACD/EMA/RSI/ML/CORE4-overlay rescue under this line. Any continuation moves under a **new research ID** to the Beta-to-BTC continuation-value problem.

If 0056 passes, any fixed BTC-anchor + routed-Beta integration also requires a new research ID. 0056 itself never changes BTC allocation or canonical BRRK.


## Implementation-only boundary

The implementation branch now contains a pure deterministic engine and synthetic-only contract tests. The engine has **no filesystem market loader, no network fetch, no `run_once.py`, no result writer and no controlled-execution authority**. It accepts already-materialized ETH/SOL close frames; the later controlled-run layer must independently verify the frozen 0047 market-evidence identity before calling it.

Synthetic tests cover the exact RM60 sign/zero semantics, next-period timing, L1 cost debits, no-rebalance B2 accounting, 5/10/20 bps panel, fixed 531/531/530/530 global blocks, project-standard `np.random.default_rng` moving-block bootstrap, G0-G4 classification precedence and mandatory diagnostics. A full 2183-row **synthetic** UTC calendar is allowed only to test mechanics; any synthetic classification has zero scientific authority and is never persisted as a research result.

Real `MARKET_EVIDENCE.json` loading and any historical 0056 evaluation remain forbidden until a separate controlled-execution boundary merges.

## Controlled-execution boundary

The separate controlled-run layer is now frozen on this branch. It binds the merged preregistration, dataset declaration, implementation boundary, scientific engine, synthetic contract test, immutable 0048 source engine/declaration, and the exact 0047 `MARKET_EVIDENCE.json` git blob plus payload SHA256.

Runtime state is staged and create-only:

```text
preflight       repeatable / zero result
start-attempt   create RUN_ATTEMPT.marker and permanently close same-ID recomputation authority
evaluate        requires durable attempt marker; load the frozen market evidence and call the frozen 0056 portfolio engine exactly once
finalize        hash verification only; market loader and portfolio engine calls forbidden
```

Frozen runtime artifacts are `RUN_ATTEMPT.marker`, `PRIMARY_RESULT.json`, `EXECUTION.json`, and `RUN_ONCE.marker`. This boundary branch contains none of them. A complete result+execution bundle with only the final marker missing may use marker-only recovery; any interruption after the attempt marker but before a complete result/execution bundle forbids automatic same-ID remeasurement.

The result schema permits only the preregistered 0056 portfolio-economic outputs and diagnostics. It rejects probability/predictive metrics, hindsight winner/oracle metrics, BTC/cash integration, CORE4, leverage and shorting. The classification must mechanically match frozen G0-G4 precedence.

Synthetic/fault run `31602817149` passed the implementation contracts, controlled-run fault contracts and zero-result guard. It did not evaluate the real 0056 historical payload.

## Immutable 0056 closeout

Unique run `31604126017` at scientific HEAD `186a7f7d57c957c98798ecd828533ffe20dedb83` closed **`INVALID_EXECUTION`** at G0 because the source loader is tz-naive while the frozen 0056 validator requires tz-aware UTC. No terminal wealth, CAGR or G1-G4 result exists. 0056 cannot be repaired or rerun; corrected evaluation requires a new research ID.

## Current authority

```text
numerical preregistration     MERGED AT 85bbc8583b625da670267cbb3db4928fbe1ade6f
implementation                MERGED AT 9417bc3370613f1818d11aebf91bf733ac5ecbcc
controlled execution boundary MERGED AT 186a7f7d57c957c98798ecd828533ffe20dedb83
historical execution          UNIQUE RUN 31604126017 / COMPLETE
result                        INVALID_EXECUTION / CLOSED
actual variants evaluated     1
canonical BRRK                NO CHANGE
Phase 6                       NO CHANGE
production_authorized         false
signature_authorized          false
order_submission_authorized   false
```

After this controlled-execution boundary merges green, the only allowed next action is the unique staged DEVELOPMENT execution from the exact merged boundary HEAD: zero-result preflight, durable attempt marker, exactly one real evaluation, durable result/execution bundle, then marker-only finalization. No real 0056 historical evaluation is authorized while this boundary remains unmerged.
