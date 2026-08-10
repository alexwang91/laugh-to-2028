# BRRK-EXHAUSTION-EVENT-STUDY-0043

Status: **FROZEN DIAGNOSTIC DESIGN / NOT YET EXECUTED**  
Authority: **DIAGNOSTIC ONLY / NO PROMOTION / NO STRATEGY CHANGE**  
Issue context: #154

## Question

Can prospectively computable deterioration features distinguish a genuine BRRK local exhaustion top from an ordinary pullback / consolidation that later resumes to a new high, with useful warning information roughly one to two weeks before the local peak or confirmation shortly after it?

This study is not an allocation search and does not change canonical BRRK-0011, the frozen 40/60 winner candidate, Phase 6, P3.3, production authority, signing, or order submission.

## Epistemic boundary

The historical BRRK PNL path is already researcher-exposed. The user-identified episodes are retained only as human sanity-check anchors and may not define thresholds, event labels, feature weights, or success gates.

Retrospective event labels are allowed to use future PNL solely to classify what eventually happened after a candidate local peak. Every predictor feature evaluated at date `t` must use information available no later than `t`.

This study produces diagnostic classification evidence only. It does not produce an authorized gross-risk map. Any later `gross = f(exhaustion_score)` candidate requires a new, separately preregistered research ID.

## Canonical PNL source

- `research/results/pit_disp_0015/daily_equity.csv`
- primary series: `BRRK0011_BASELINE`
- historical evaluation window: intersection of the canonical PNL series and available governed market-data dates through `2026-08-02`

## Market-data source

Daily OHLCV is retrieved from the same Binance spot 1-day kline endpoints already encoded in `research/core/crypto_rotation_backtest.py`:

- `https://data-api.binance.vision/api/v3/klines`
- fallback `https://api.binance.com/api/v3/klines`
- interval: UTC `1d`
- assets: BTC, ETH, SOL, BNB, XRP quoted in USDT

XRP is feature-only. Volume/OHLC information is retrospective researcher-exposed DEVELOPMENT diagnostic data and is not claimed as independent OOS evidence.

## Mechanical event taxonomy

### Candidate local peak

A date is an event candidate only when all of the following hold:

1. canonical BRRK NAV on that date is the maximum over the centered `[-7,+7]` calendar-session window;
2. the prior 30-session NAV gain is at least `+5%`;
3. canonical NAV suffers at least a `-5%` pullback from that peak within the next 14 sessions.

Candidates within 21 calendar days are declustered by retaining the highest canonical NAV peak in the cluster.

### Competing-barrier outcome labels

For each candidate peak, inspect the next 60 sessions. A fresh-high barrier is fixed at `+2%` above the candidate peak. Downside severity is evaluated simultaneously at three frozen barriers: `-10%`, `-15%`, and `-20%` from the candidate peak.

For each downside barrier independently:

- `TRUE_EXHAUSTION`: downside barrier is reached before the `+2%` fresh-high barrier;
- `CONTINUATION_FALSE_TOP`: `+2%` fresh-high barrier is reached before the downside barrier;
- `AMBIGUOUS`: neither barrier is reached within 60 sessions.

The `-15%` panel is the primary descriptive panel. The `-10%` and `-20%` panels are mandatory robustness panels. No panel may be removed after results are seen.

## User anchors — sanity checks only

The following dates/regions are not training labels and do not affect the taxonomy:

- `2023-12-25` region
- `2024-03-31` region
- `2024-11-24` region
- `2025-01-26` region
- `2025-10-06` region; canonical NAV may identify `2025-10-08` as the nearby higher local peak

The audit reports the mechanically detected event nearest each anchor and its taxonomy, without forcing a match.

## Fixed observation windows

For every detected event peak `T`, feature-family scores are summarized over:

- `PRE14_7`: `T-14` through `T-7` — primary one-to-two-week warning window;
- `PRE7_0`: `T-7` through `T` — near-peak warning window;
- `POST0_7`: `T` through `T+7` — early confirmation window, descriptive only.

`POST0_7` may not be described as advance warning.

## Frozen feature families

All pre-peak feature calculations are causal at their timestamp.

### F1 — momentum level / decay
- RSI(14), RSI(28), and RSI 7-session slope;
- MACD(12,26,9) histogram level and 5-session histogram slope;
- BRRK-style 20/60/120/240 normalized trend components;
- aggregate fast-vs-slow trend spread;
- 7-session first difference and second difference of the BRRK-style aggregate trend.

### F2 — price-structure deterioration
- distance to 30/60/120-session rolling highs;
- sessions since 60-session high;
- price distance to MA20/MA60;
- MA20 and MA60 10-session slopes;
- continuous prior-swing-high shortfall and intervening-trough depth where available.

### F3 — volume / price-volume confirmation
- volume z-score(20) and 20-session volume trend;
- up-volume versus down-volume imbalance(20);
- OBV 20-session slope;
- 20-session price change versus OBV change divergence;
- selloff-volume expansion versus up-session volume.

### F4 — volatility / downside asymmetry
- realized volatility 10/30/60 sessions;
- short-vol acceleration (`RV10` relative to its 7-session lag and `RV30`);
- downside/upside semivolatility ratio(20);
- negative-return share(20);
- normalized ATR(20);
- canonical PNL drawdown depth and drawdown-duration interaction known at the date.

### F5 — breadth / relative-strength deterioration
- fraction of BTC/ETH/SOL/BNB/XRP with positive 20-session and 60-session trend;
- 7-session breadth slope;
- mean alt/BTC 20-session relative return;
- cross-sectional 20-session return dispersion;
- top-vs-second 20-session cross-sectional momentum spread.

### F6 — correlation / systemic-risk structure
- mean pairwise 30-session return correlation;
- mean alt-to-BTC 30-session correlation;
- 7-session change in mean pairwise correlation;
- alt beta to BTC on negative-BTC sessions over a 30-session window.

### F7 — BRRK internal deterioration / disagreement
- canonical defensive-scale proxy derived from same-date BRRK gross divided by V1 gross where defined;
- 7-session defensive-scale slope;
- slow-minus-fast BTC trend disagreement;
- fraction of long-horizon-positive assets whose short trend has already deteriorated;
- persistence count of consecutive days with fast trend below slow trend.

### F8 — recovery / hysteresis
This family is evaluated only after a detected event/trigger and is excluded from advance-top classification scores:
- sessions to reclaim the prior peak;
- breadth recovery;
- trend-slope recovery;
- volatility normalization;
- persistence before re-risk conditions recover.

## Normalization and score construction

No fitted feature weights and no hyperparameter search are permitted in this diagnostic.

For each raw deterioration-oriented feature:

1. orient it ex ante so higher means more deterioration;
2. standardize causally using its trailing 252-session mean and standard deviation with at least 60 observations;
3. clip the standardized value to `[-3,+3]`.

Within each of F1–F7, the family score is the equal-weight mean of available standardized features. The total `EXHAUSTION_SCORE` is the equal-weight mean of available F1–F7 scores. F8 is excluded from this total.

Highly similar indicators are not interpreted as independent votes; the audit reports the correlation structure and effective feature count. No data-driven deletion or reweighting is allowed after the first result under this ID.

## Diagnostics

For each severity panel and each observation window, report:

- number of TRUE_EXHAUSTION / CONTINUATION_FALSE_TOP / AMBIGUOUS events;
- ROC AUC of each F1–F7 family score and total EXHAUSTION_SCORE for TRUE vs CONTINUATION events;
- median score in each class and median class gap;
- user-anchor nearest-event mapping;
- feature/family correlation summary;
- fixed warning-threshold panel using the trailing-252 historical percentile of total score at `{70%,80%,90%}`, requiring three consecutive sessions above threshold, with lead time and false-trigger incidence reported for all three thresholds. No threshold is selected under this ID.

The study may describe whether the requested 7–14 day lead-time region appears feasible. It may not select a production threshold or alter strategy weights.

## Stop / follow-up rule

After the first complete output is released:

- no feature, horizon, event threshold, barrier, score weight, warning percentile, persistence count, or anchor may be changed under this ID;
- no economic counterfactual or gross-risk map may be run under this ID;
- any promising state/threshold must be frozen under a new research ID before portfolio economics are evaluated;
- a weak or contradictory result remains negative evidence and is not rescued by adaptive feature/threshold search.

Production/signature/order authority remain false.
