# AUDIT-0017-PIT-ALPHA-ATTRIBUTION — 2026-08-04

Status: **VALID NO-TRADING-CHANGE AUDIT / DOMINANT FAILURE MECHANISM IDENTIFIED**

This audit changed no PIT-ALPHA-0016 target weight, universe rule, signal, rank, Top-N, BTC core, concentration cap, rebalance band or transaction cost assumption.

## Question

Why did the preregistered own-trend + relative-strength rank beat 98% of random-priority placebo portfolios while the realized Top-2 portfolio still produced only 12.25% CAGR, -69.12% maximum drawdown and turnover near 350?

## Primary answer

**The rank contains information, but strict daily Top-2 replacement converts that information into unstable one-day positions. Within-alt name switching accounts for 83.4% of all turnover. The return distribution is strongly right-skewed: most entries lose modestly, while a small number of persistent trends create the positive mean. The portfolio repeatedly replaces incumbents before those rare winners can compound.**

The failure is therefore not primarily capacity, BTC beta adjustment or the total size of the alt sleeve. It is the combination of:

1. a rapidly changing eligible/ranked cross-section;
2. daily relative-rank replacement;
3. one-day median holding periods;
4. frequent small losing entries;
5. rare large winners that require longer persistence;
6. substantial tail losses and volatility/compounding drag.

## Universe and rank instability

Across 1,920 evaluation days:

- mean daily eligible-set Jaccard similarity: **0.630**;
- median: **0.652**;
- approximately **2.98 additions and 2.98 removals per day**;
- monthly first-to-last eligible-set Jaccard: mean **0.249**, median **0.222**.

The investable positive-trend set is therefore not stable through a month. Only about one quarter of the union of beginning- and end-of-month eligible names remains common on average.

## Actual holding behavior

- holding spells: **653**;
- distinct alt symbols held: **113**;
- median holding duration: **1 day**;
- mean duration: **3.28 days**;
- 75th percentile: **3 days**;
- 95th percentile: **11 days**;
- positive-contribution spells: only **41.96%**;
- median re-entries per symbol: **2**;
- maximum: **49 re-entries for TRXUSDT**.

The strategy is not functioning as medium-horizon trend following at the position level. It is functioning as a high-frequency daily leaderboard replacement system built from medium-horizon signals.

## Turnover decomposition

Total L1 turnover reconstructed from exact held weights: **350.62**.

| Component | Turnover | Share |
|---|---:|---:|
| BTC weight changes | 25.18 | **7.18%** |
| Change in total alt-sleeve size | 33.01 | **9.41%** |
| **Within-alt name switching** | **292.43** | **83.41%** |

Additive transaction cost at 5 bps was approximately **17.53 percentage points** over the full sample.

The dominant turnover source is not risk-off exposure control. It is replacing one eligible alt with another because their daily relative rank changes.

## Rank persistence and return asymmetry

For 651 observable entries:

| Horizon | Still eligible | Still Top-2 | Median forward return | Mean forward return |
|---:|---:|---:|---:|---:|
| 1 day | 79.88% | 51.46% | **-0.58%** | -0.28% |
| 3 days | 71.74% | 42.09% | **-0.50%** | -0.17% |
| 7 days | 65.13% | 33.64% | **-1.50%** | +0.65% |
| 14 days | 58.83% | 25.19% | **-1.57%** | +2.63% |
| 30 days | 52.07% | 19.35% | **-2.43%** | **+4.83%** |

The signal has a strong right-tailed payoff profile:

- the median selected asset loses at every measured horizon;
- the mean becomes increasingly positive at 7–30 days;
- about half of entries remain broadly trend-eligible after 30 days, but fewer than one fifth remain in the daily Top-2.

This is the central incompatibility. A daily strict Top-2 rule exits an incumbent when another name marginally outranks it, even though the incumbent often remains in a valid positive own-and-relative trend. That behavior systematically shortens exposure to the rare large winners that generate the rank's positive mean.

## Fixed-V1 overlap

- mean fraction of PIT alt exposure invested in an active fixed-V1 alt: **15.65%**;
- days with any overlap: **28.70%**;
- mean daily net return on overlap days: **+0.1439%**;
- mean daily net return on non-overlap days: **+0.0396%**;
- compounded return over overlap-day observations: **+55.84%**;
- compounded return over non-overlap-day observations: **+17.78%**.

This does not justify hard-coding ETH/SOL/BNB; that would reintroduce the selection bias the PIT test was designed to remove. It does show that the fixed V1 portfolio spent more time in persistent, higher-quality trends, while the broad daily rank frequently rotated through less durable names.

## Tail loss and volatility drag

Worst daily losses were not caused by transaction cost. They were genuine market/tail events:

- 2021-05-19: **-21.15%**, with FTT the largest alt contributor;
- 2023-09-23: **-11.66%**, FLM largest contributor;
- 2023-07-21: **-10.22%**, AGLD contribution about -10.47%;
- several broad BTC-led selloffs produced additional 9–12% daily losses.

The largest drawdown ran from November 2021 to an October 2023 trough:

- maximum drawdown: **-69.12%**;
- approximately 710 calendar days to trough;
- additive gross return across the full drawdown/recovery episode: **+55.79%**;
- transaction cost: **11.42 percentage points**;
- compounded net return by the eventual recovery date: only **+3.56%**.

The difference between positive additive return and near-flat compounded wealth demonstrates severe volatility/sequence drag. Costs matter, but tail losses and unstable compounding are at least as important.

## 2024 versus 2025

| Year | Net return | Total turnover | Name-switch turnover | New spells | Median hold | Fixed-V1 overlap days |
|---|---:|---:|---:|---:|---:|---:|
| 2024 | **+231.91%** | 88.13 | 78.07 | 181 | 2 days | **60.66%** |
| 2025 | +10.77% | 63.30 | 50.22 | 110 | 2 days | **25.75%** |
| 2026 to Aug 2 | -11.06% | 5.29 | 0.00 | 4 | 1 day | 0% |

The 2024 success coincided with much greater overlap with the persistent major-asset trends that fixed V1 also held. In 2025 the strategy continued paying substantial name-switch turnover, but overlap with those durable trends fell sharply. In 2026, name switching was no longer the main issue; the loss was dominated by the BTC core during a defensive/negative market period.

## Cohort observations

Listing age showed a useful but non-monotonic warning:

- 240–364 day entries: median 30-day return **-10.77%**;
- 365–729 day entries: **-6.85%**;
- 730–1459 day entries: approximately **-0.25%**;
- 1460+ day entries: **+1.40%**.

Younger names have worse median outcomes, but some produce very large positive outliers. This audit does **not** authorize changing the 240-day threshold: doing so now would be post-result parameter selection.

Currently BREAK symbols also had lower 7-day Top-2 persistence than currently trading symbols (17.3% versus 37.0%). Current status cannot be used as a historical filter because it is future information.

## Capacity is not the primary failure

At a hypothetical $1 million NAV, alt position notional as a fraction of completed-day quote volume was:

- median: **0.189%**;
- 95th percentile: **0.956%**;
- 99th percentile: **1.252%**;
- maximum: **1.395%**.

This is only a coarse volume proxy, not an execution guarantee. However, at the tested scale, capacity is not the dominant reason for poor backtest economics. Turnover, tail risk and holding logic dominate first.

## Causal diagnosis

Evidence supports the following ordered diagnosis:

1. **Primary:** daily cross-sectional name replacement creates one-day median holdings and 83.4% of turnover.
2. **Primary:** the signal's payoff is right-skewed; rare persistent winners require longer holding than strict Top-2 membership.
3. **Secondary:** tail events and volatility drag destroy compounding even when additive gross return is positive.
4. **Secondary:** broad-universe selection spends too little time in the durable trends represented by fixed-V1 overlap.
5. **Not primary:** capacity at $1 million NAV.
6. **Not sufficient alone:** transaction costs. Removing costs would help, but would not solve -69% drawdown or unstable compounding.

## Authorized next hypothesis

The audit supports exactly one next structural hypothesis:

> **Use Top-2 relative rank for entry, but do not replace an incumbent merely because it falls out of Top-2. Continue holding it while it remains own-trend-positive and relative-to-BTC-trend-positive; replace only when it becomes ineligible, BTC enters risk-off, or a vacancy exists.**

This is an `entry-rank / eligibility-exit` state machine:

- keeps the validated ranking mechanism as the entry selector;
- uses the already frozen eligibility condition as the exit rule;
- directly targets the 83.4% name-switch problem;
- gives right-tail winners time to compound;
- introduces no rank-buffer threshold, minimum-hold parameter or monthly calendar parameter.

It must receive a new experiment ID and preregistration. It is not a tuned amendment to PIT-ALPHA-0016.

## Prohibited interpretations

- Do not hard-code ETH/SOL/BNB from the overlap result.
- Do not raise the minimum listing age from this audit.
- Do not optimize a Top-K exit threshold.
- Do not choose a minimum holding period from the observed duration table.
- Do not claim transaction cost alone explains the failure.
- Do not alter PIT-ALPHA-0016; it remains a rejected portfolio specification with a validated ranking mechanism.

## Decision

1. **AUDIT-0017 identifies daily name replacement as the dominant mechanical failure.**
2. **The next eligible experiment is an entry-rank / eligibility-exit state machine under a new ID.**
3. **BRRK-0011 remains the canonical research baseline.**
4. **No live or shadow allocation changes are authorized by this audit.**
