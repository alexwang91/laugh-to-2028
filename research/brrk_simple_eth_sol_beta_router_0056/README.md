# BRRK-SIMPLE-ETH-SOL-BETA-ROUTER-0056

Status: **NUMERICAL PREREGISTRATION MERGED / IMPLEMENTATION-ONLY ON BRANCH / REAL HISTORICAL RUN FORBIDDEN**

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

## Current authority

```text
numerical preregistration     MERGED AT 85bbc8583b625da670267cbb3db4928fbe1ade6f
implementation                IMPLEMENTATION-ONLY ON BRANCH
controlled execution boundary ABSENT
historical execution          NOT RUN
result                        PREREGISTERED_NOT_RUN
actual variants evaluated     0
canonical BRRK                NO CHANGE
Phase 6                       NO CHANGE
production_authorized         false
signature_authorized          false
order_submission_authorized   false
```

After this implementation-only branch merges green, the only allowed next stage is a **separate controlled-execution boundary**. No real 0056 historical evaluation is authorized by the implementation merge itself.
