# BRRK-BETA-HANDOFF-EVENT-STUDY-0047 — Exact Design Freeze

Date: 2026-08-11  
Status: **DESIGN FROZEN / NOT PREREGISTERED / NOT RUN**  
Governance mode for any later result-bearing continuation: `PROGRAM_GOVERNED_V1`  
Proposed research stage: `STAGE_1_INFORMATION_TEST`  
Proposed objective type: `MECHANISM_TEST`  
Proposed research domain: `RELATIVE_VALUE`

This document freezes the scientific architecture for a new BTC-to-Beta handoff anatomy study. It is **design only**. It does not create a preregistration, runner, dataset release, result, portfolio candidate, allocation rule, production decision, Phase-6 change, signing authority or order-submission authority.

The study asks a deliberately narrower question than portfolio optimization:

> After the existing canonical BTC trend has entered a positive phase, is there a repeatable, duration-aware transition in which ETH or SOL becomes a durable relative leader, and what causal information is present around that transition?

The study does **not** ask how much capital to allocate after a handoff. `60% / 80% / 100%` winner concentration, dynamic BRRK target construction, CAGR comparison, cash credit and portfolio economics are forbidden under 0047 and belong to separately preregistered later research.

---

## 1. Binding repository evidence and why 0047 exists

### 1.1 BRRK Opportunity-Cost Audit 0042

0042 is diagnostic-only evidence. It explicitly identified that winner-cap return counterfactuals were unavailable inside that audit and required a separate preregistered strategy experiment. It also identified BTC share of gross on alt-active days as a mechanism worth inspecting.

0047 must preserve that boundary: it may diagnose leadership transitions, but it may not use the final BRRK equity curve as a surface for choosing handoff definitions or feature windows.

### 1.2 BRRK-WINNER-0001 and BRRK-WINNER-ROBUSTNESS-0002

The winner lineage is result-informed motivation, not independent evidence for 0047.

`BRRK-WINNER-0001` changed only the frozen single-alt branch from BTC/winner `50/50` to `40/60` while retaining the same BRRK defensive gross. Its exposed DEVELOPMENT result increased CAGR from about `65.31%` to `69.69%`, with essentially unchanged maximum drawdown and higher turnover. The later robustness study retained positive CAGR advantage at 10 bps and 20 bps cost stress and passed its frozen robustness gates.

This supports one narrow mechanism hypothesis: once a genuine alt winner exists, the frozen BRRK/V1 construction may retain more BTC than is economically necessary. It does **not** identify when a winner has genuinely taken leadership.

### 1.3 Existing frozen V1 already contains a coarse handoff heuristic

The current frozen V1 rotation implementation already uses:

- price-trend horizons `20 / 60 / 120 / 240` sessions;
- `FAST_WEIGHTS = [0.15, 0.25, 0.30, 0.30]`;
- `SLOW_WEIGHTS = [0.10, 0.20, 0.30, 0.40]`;
- BTC fast trend as the absolute market trend gate;
- ETH and SOL absolute trend plus ETH/BTC and SOL/BTC relative trend;
- positive eligibility requirements;
- a single-alt `50/50` BTC/alt branch;
- a multi-alt branch that retains BTC and applies asset concentration caps.

Therefore 0047 may **not** claim that `absolute trend > 0` or `relative-to-BTC trend > 0` is a new discovery. The incremental question is whether leadership change has a reproducible **timing, duration, acceleration, breadth and participation anatomy** beyond the existing coarse eligibility rule.

### 1.4 Exhaustion lineage remains separate

0043/0044 provide positive evidence that continuous exhaustion state carries ranking information. 0045/0046 failed as discrete trigger translations. None of those results are reinterpreted here.

0047 is an upside/relative-leadership mechanism study, not an exhaustion rescue, not dynamic gross, and not a replacement for the future exhaustion portfolio stage.

---

## 2. External-method provenance

The design is externally hypothesis-informed as well as repository-result-informed. The following literature motivates specific methodological choices; it does not constitute evidence that the BTC→ETH/SOL mechanism is true in this dataset.

1. **Hou (2007), _Industry Information Diffusion and the Lead-lag Effect in Stock Returns_, RFS, DOI 10.1093/revfin/hhm003.** Large firms can lead smaller economically related firms because information diffuses gradually. Adopted implication: explicitly measure leader/follower timing rather than assume simultaneous response.
2. **Menzly & Ozbas (2010), _Market Segmentation and Cross-predictability of Returns_, Journal of Finance, DOI 10.1111/j.1540-6261.2010.01578.x.** Economically related groups can cross-predict because information diffusion is gradual. Adopted implication: measure BTC→alt cross-predictability and do not treat each asset in isolation.
3. **Moskowitz, Ooi & Pedersen (2012), _Time Series Momentum_, JFE, DOI 10.1016/j.jfineco.2011.11.003.** Trend persistence exists across major asset classes. Adopted implication: a leadership state should be evaluated for persistence, not one-day rank.
4. **Moskowitz & Grinblatt (1999), _Do Industries Explain Momentum?_, Journal of Finance, DOI 10.1111/0022-1082.00146.** Leadership/momentum can be a group-level rotation phenomenon. Adopted implication: treat Beta expansion as a market-internal leadership transition.
5. **Goulding, Harvey & Mazzoleni (2023), _Momentum Turning Points_, JFE, DOI 10.1016/j.jfineco.2023.05.007.** Fast and slow momentum jointly characterize turning-point states. Adopted implication: freeze both fast and slow absolute/relative trend measures rather than one speed.
6. **Liu & Tsyvinski (2021), _Risks and Returns of Cryptocurrency_, RFS, DOI 10.1093/rfs/hhaa113**, and **Liu, Tsyvinski & Wu (2022), _Common Risk Factors in Cryptocurrency_, Journal of Finance, DOI 10.1111/jofi.13119.** Crypto returns contain time-series and cross-sectional momentum structure. Adopted implication: relative leadership is a legitimate information family to test, not proof of a profitable handoff.
7. **Kurihara & Matsumoto (2026), _Price Transmission from Bitcoin to Altcoins: High-Frequency Evidence and Implications for Trading Strategy_, Asia-Pacific Financial Markets, DOI 10.1007/s10690-026-09589-z.** Cross-correlation, Granger causality, VAR and impulse-response analysis can characterize BTC→alt transmission; lower-liquidity small alts can react more slowly. Important boundary: large assets such as ETH were largely contemporaneous at minute frequency, so the paper does **not** justify a fixed daily/weekly lag for ETH/SOL.
8. **BTC/ETH lead-lag evidence (RIBAF 2019), DOI 10.1016/j.ribaf.2019.06.012.** Hourly/daily BTC↔ETH causality was largely bidirectional and not obviously exploitable. Adopted implication: absence of simple Granger directionality does not invalidate a slower leadership-regime handoff, and Granger results are descriptive rather than a hard gate.
9. **Chang & Shi (2020), DOI 10.1016/j.orl.2020.08.005.** Crypto price-discovery leadership is time-varying. Adopted implication: do not assume BTC leadership is stationary through every episode.
10. **Semi-Markov duration-dependent regime research (Economic Modelling 2023), DOI 10.1016/j.econmod.2023.106237.** State termination can depend on state age; standard Markov memorylessness can miss momentum/reversal structure. Adopted implication: `state_age` is a frozen causal variable and the proposed later 0048 model is duration-aware.
11. **Adams & MacKay (2007), _Bayesian Online Changepoint Detection_, arXiv:0710.3742.** Run length is a principled online change descriptor. Boundary: BOCPD is **not** a primary 0047 candidate and cannot affect 0047 classification. A future auxiliary BOCPD study requires an explicitly frozen implementation because its hazard/prior choices create extra degrees of freedom.

No external paper is treated as a substitute for crypto episode-level evidence.

---

## 3. Frozen scientific hypotheses and adversarial alternatives

### H1 — BTC-positive phases contain a reproducible Beta handoff opportunity

Hypothesis: after a canonical BTC-positive trend episode begins, there are recurrent dates where ETH or SOL becomes the unique durable forward winner over BTC on both fast and medium horizons.

Adversarial alternative A1: BTC, ETH and SOL are so synchronous that apparent handoffs are mostly hindsight ranking noise and do not recur across independent bull episodes.

### H2 — handoff timing is duration-dependent, not a fixed delay

Hypothesis: the probability of a handoff changes with `state_age` and causal fast/slow relative-trend structure.

Adversarial alternative A2: there is no stable relationship between time since BTC trend confirmation and subsequent Beta leadership; any fixed or duration-aware timing model is overfit.

### H3 — relative acceleration, breadth and participation characterize expansion beyond the existing V1 eligibility rule

Hypothesis: durable handoff opportunities are accompanied by changes in fast-vs-slow relative trend, cross-Beta breadth and candidate-asset participation.

Adversarial alternative A3: the existing V1 conditions (`absolute trend > 0` and `relative trend > 0`) exhaust the useful information; added anatomy is redundant.

### H4 — BTC→alt transmission may be present but is not required to be a one-way daily lag

Hypothesis: pooled episode-preserving transmission diagnostics may show BTC-leading structure, but large-cap ETH/SOL can also be contemporaneous or bidirectional.

Adversarial alternative A4: simple daily BTC→ETH/SOL Granger causality is absent. This result must be preserved if observed and **does not** by itself convert a duration/relative-leadership study into a failure or a pass.

### H5 — a one-switch hindsight oracle defines opportunity-set size only

Hypothesis: some BTC-positive episodes contain economically meaningful value in choosing a single BTC→ETH/SOL switch.

Adversarial alternative A5: even perfect one-switch hindsight adds little relative to BTC-only. If so, later portfolio research has a low economic ceiling.

The oracle is descriptive only and cannot define labels, choose features, select horizons, select the later model, or enter a 0047 hard PASS gate.

---

## 4. Frozen universe, data boundary and contamination status

Primary universe:

```text
BTC / ETH / SOL
```

`BNB` is excluded from the primary 0047 competing-risk target because the owner-defined Beta Expansion question is specifically BTC→ETH/SOL. The prior winner lineage containing BNB remains valid evidence but is not used to expand the primary 0047 universe after results.

Frozen market source semantics:

```text
Binance spot BTCUSDT / ETHUSDT / SOLUSDT UTC daily klines
fields = open, high, low, close, volume, quote_volume, trades
history start = 2020-08-01
history end   = 2026-08-02 inclusive
```

The later preregistration must register this as **DEVELOPMENT / RESEARCHER_EXPOSED_HISTORY**. No claim of independent OOS evidence is permitted. No observation after `2026-08-02` may enter the 0047 historical result.

The implementation must use one common contiguous daily index across BTC/ETH/SOL. Duplicate dates, missing dates inside the required common history, nonpositive closes, negative trade counts or nonfinite required fields fail closed.

The exact raw market frame used by a later run must be deterministically serialized and SHA256-bound before result metrics are emitted.

---

## 5. Frozen canonical BTC-positive episode definition

0047 reuses the exact frozen V1 trend mathematics rather than inventing a new BTC bull definition.

For close series `P_t`, define log return `r_t = log(P_t) - log(P_{t-1})` and, for each horizon `h`:

```text
momentum_h(t) = log(P_t / P_{t-h})
scale_h(t)    = rolling_std_h(r) * sqrt(h)
component_h(t)= tanh(momentum_h(t) / scale_h(t))
```

Exact horizons:

```text
H = [20, 60, 120, 240]
```

Exact fast and slow weights:

```text
FAST = [0.15, 0.25, 0.30, 0.30]
SLOW = [0.10, 0.20, 0.30, 0.40]
```

`TREND_FAST` and `TREND_SLOW` are the corresponding weighted sums and are valid only when all four components are valid.

A **BTC-positive episode** is every maximal contiguous run of common daily sessions satisfying:

```text
BTC_TREND_FAST >= 0
```

Rules:

- a negative or NaN BTC fast trend terminates the episode;
- no persistence filter;
- no bridging across 1–N negative days;
- no minimum-return filter;
- no manual bull-market anchors;
- no event deletion because an episode looks unimportant in hindsight.

`state_age(t)` is the 1-based count of common daily sessions since the start of the current BTC-positive episode.

This is the exact causal `BTC_LEAD` risk-set clock proposed for later duration-aware modeling. It does not assert that BTC is always the best asset on every positive-trend day.

---

## 6. Frozen causal anatomy panel

Every causal predictor on date `t` may use information no later than the end of UTC date `t`.

### 6.1 Absolute trend

For each `a ∈ {BTC, ETH, SOL}`:

```text
ABS_FAST_a = TREND_FAST(P_a)
ABS_SLOW_a = TREND_SLOW(P_a)
```

### 6.2 Relative trend versus BTC

For `a ∈ {ETH, SOL}` define ratio series:

```text
Q_a = P_a / P_BTC
REL_FAST_a = TREND_FAST(Q_a)
REL_SLOW_a = TREND_SLOW(Q_a)
```

### 6.3 Frozen fast/slow relative acceleration proxy

For each Beta asset:

```text
REL_ACCEL_a = REL_FAST_a - REL_SLOW_a
```

This is not an independently tuned indicator. It is the deterministic fast-minus-slow spread from the already frozen V1 time scales, motivated by fast/slow turning-point literature.

### 6.4 Frozen Beta breadth/diffusion

Define each Beta asset as causally participating when both its absolute fast trend and relative fast trend are positive:

```text
PARTICIPATING_a(t) = 1[ABS_FAST_a(t) > 0 and REL_FAST_a(t) > 0]
```

Then:

```text
BETA_BREADTH(t) = (PARTICIPATING_ETH(t) + PARTICIPATING_SOL(t)) / 2
```

Possible values are exactly `0.0 / 0.5 / 1.0`.

No market-wide altcoin breadth universe is introduced under 0047.

### 6.5 Frozen participation/liquidity confirmation

The 2026 BTC→alt transmission paper motivates trade count as a simple liquidity/activity proxy. For each Beta asset:

```text
LOG_TRADES_a(t) = log(1 + trades_a(t))
MED60_a(t)      = median(LOG_TRADES_a over t-59 ... t), min_periods=60
TRADE_SURPRISE_a(t) = LOG_TRADES_a(t) - MED60_a(t)
```

No volume/trade-count candidate tournament is allowed. `quote_volume` is retained in the raw evidence frame for reproducibility but is not a second primary participation feature.

### 6.6 State age

```text
STATE_AGE(t) = 1,2,3,... within each BTC-positive episode
```

No log transform, spline, age bins or fitted nonlinear transformation is selected under 0047. Raw age distributions are reported. A later 0048 preregistration must freeze any transformation before fitting.

### 6.7 Existing V1 eligibility/score as benchmark only

The exact frozen V1 ETH/SOL score and eligibility state may be reconstructed as a benchmark because it is already existing repository logic. It cannot be presented as a new 0047 feature edge and cannot be modified.

---

## 7. Frozen realized durable-handoff target

0047 separates **causal predictors** from an explicitly hindsight-defined **realized future target**.

For asset `x ∈ {BTC, ETH, SOL}` and horizon `h ∈ {20,60}`, define forward log return from date `t`:

```text
F_h_x(t) = log(P_x[t+h] / P_x[t])
```

where `t+h` means exactly `h` positions later on the common contiguous daily index. No interpolation is allowed.

For Beta asset `a` and the other Beta asset `b`, define a **durable handoff opportunity of cause a** on date `t` iff all conditions hold:

```text
1. t is inside a BTC-positive episode
2. F20_BTC(t) > 0
3. F60_BTC(t) > 0
4. F20_a(t) > F20_BTC(t)
5. F60_a(t) > F60_BTC(t)
6. F20_a(t) > F20_b(t)
7. F60_a(t) > F60_b(t)
```

Interpretation: BTC itself must remain positively realized over both the fast and medium forward horizons, while one and the same Beta asset is the unique winner over BTC and over the competing Beta asset at both horizons.

This construction deliberately prevents three common hindsight errors:

- a Beta asset is not called an expansion winner merely because it loses less than BTC in a future decline;
- a one-day or one-horizon rank reversal is not called durable leadership;
- ETH and SOL cannot both be labeled as the primary cause on the same date because the pairwise winner inequalities are strict.

If exact `t+60` is unavailable because of the frozen dataset end, the date is **right-censored / target-unavailable**, not negative.

### 7.1 Episode-level first handoff

For each BTC-positive episode, the **primary handoff event** is the earliest target-available date satisfying the durable handoff target for ETH or SOL.

After the first primary handoff in an episode, later ETH↔SOL switches do not create additional primary events under 0047. They may be reported in a non-gating secondary table only.

An episode with no primary handoff before target availability ends is `NO_DURABLE_HANDOFF / CENSORED_AS_APPLICABLE`.

### 7.2 Handoff opportunity spell

Starting at the primary event date, define the primary cause's opportunity spell as consecutive target-available sessions for which the same cause continues to satisfy all seven durable-target conditions. Report spell duration descriptively.

No minimum spell length is added because dual-horizon consistency is already part of the target definition.

---

## 8. Frozen anatomy outputs

0047 must emit an episode table containing at least:

```text
episode_id
episode_start
episode_end
episode_length
first_target_available_date
last_target_available_date
primary_handoff_date or null
primary_handoff_cause = ETH / SOL / null
handoff_state_age or null
handoff_opportunity_spell_length or null
first_ETH_abs_fast_positive_age
first_SOL_abs_fast_positive_age
first_ETH_rel_fast_positive_age
first_SOL_rel_fast_positive_age
first_ETH_existing_V1_eligible_age
first_SOL_existing_V1_eligible_age
oracle_choice
oracle_switch_date
oracle_log_wealth_uplift_vs_BTC
```

Aggregate outputs must include:

- number of total BTC-positive episodes;
- number of target-eligible episodes;
- number and share of episodes containing a durable handoff;
- number of distinct episodes with ETH cause;
- number of distinct episodes with SOL cause;
- handoff state-age median, IQR, minimum and maximum;
- ETH/SOL observable-follow lag distributions;
- handoff opportunity-spell duration distribution;
- causal feature trajectories around handoff dates on an exact event-time grid `-60 ... +20` sessions when available;
- exact missing/censored counts rather than silently dropping observations.

No episode receives multiple votes in episode-level prevalence statistics.

---

## 9. Frozen leader/follower transmission diagnostics

These diagnostics characterize mechanism. They do not define the durable handoff target and do not enter the 0047 hard PASS gate.

### 9.1 Cross-correlation

Use daily log returns:

```text
r_BTC, r_ETH, r_SOL
```

Within BTC-positive episodes, compute episode-preserving BTC/ETH and BTC/SOL return cross-correlations for integer lags exactly:

```text
-14 ... +14 sessions
```

A pair contributes at lag `k` only if both observations belong to the same BTC-positive episode. Report each episode and pooled episode-preserving estimates. Do not concatenate across episode boundaries as if adjacent.

### 9.2 Pooled episode-preserving VAR(7)

Fit a single common-coefficient daily return VAR with exactly seven lags:

```text
R_t = c_episode + A1 R_{t-1} + ... + A7 R_{t-7} + e_t
R_t = [r_BTC, r_ETH, r_SOL]'
```

Only rows for which `t` and all seven lagged rows are inside the same BTC-positive episode are eligible. Episode intercepts are nuisance fixed effects. There is no lag-order search.

If the pooled companion matrix is unstable, report the instability as negative/descriptive evidence. Do not change the lag order after observing it.

### 9.3 Granger/Wald diagnostics

Using the frozen pooled VAR(7), report joint zero-lag-coefficient tests for:

```text
BTC -> ETH
BTC -> SOL
ETH -> BTC
SOL -> BTC
ETH -> SOL
SOL -> ETH
```

Because episode counts are limited and rows are serially dependent, naive daily IID significance is not an 0047 promotion gate. Where covariance estimation permits, report episode-cluster-robust Wald statistics; otherwise report coefficient sets and bootstrap uncertainty with the limitation explicit.

### 9.4 Generalized impulse responses

For a one-residual-standard-deviation BTC return shock, report generalized impulse responses of ETH and SOL returns for horizons exactly `0 ... 14` sessions using the frozen VAR coefficients and residual covariance. Generalized rather than Cholesky-ordered IRFs avoid an arbitrary contemporaneous ordering assumption.

Episode-bootstrap uncertainty is required; no alternative shock size or horizon may be selected after output review.

---

## 10. Frozen hindsight one-switch oracle — opportunity bound only

For every BTC-positive episode, define a descriptive full-gross oracle starting already invested `100% BTC` at episode start.

Permitted actions:

```text
NO SWITCH
or exactly one switch BTC -> ETH
or exactly one switch BTC -> SOL
```

The candidate switch date may be any common daily session in the episode after the episode start. After switching, the oracle holds that Beta asset through the episode end. No switch-back and no ETH↔SOL second switch is allowed.

Cost convention for the one full switch:

```text
5 bps per absolute weight change
BTC 1 -> 0 plus ALT 0 -> 1 gives L1 turnover 2.0
switch cost = 2.0 * 5 bps = 10 bps
```

The no-switch BTC path and each candidate path share the same already-held BTC starting condition, so no common initial-entry cost is added.

Report the best choice and log-wealth uplift versus BTC-only for each episode.

Hard firewall:

- oracle results do not define the durable target;
- oracle results do not select features or feature windows;
- oracle results do not select 0048 model form;
- oracle results do not select 0049 winner concentration;
- oracle uplift is not an 0047 hard PASS gate;
- oracle output is explicitly labeled `HINDSIGHT_OPPORTUNITY_BOUND / NOT_TRADABLE / NOT_OOS`.

A later portfolio stage may define an `Oracle Capture Ratio`, but only in a new preregistered research ID.

---

## 11. Dependence-aware uncertainty

Daily rows are not independent samples.

The primary independent-ish unit for uncertainty is the complete BTC-positive episode. Where bootstrap uncertainty is reported:

```text
resampling unit = complete BTC-positive episode
replicates       = 10,000
seed             = 470047
```

Resampling retains every eligible row inside each selected episode. Event-time trajectories, handoff prevalence, cause shares, state-age summaries, spell summaries, cross-correlations and IRFs must not use naive IID daily bootstrap confidence intervals.

Overlapping 20/60-day target horizons are explicitly acknowledged as serially dependent. No bar-count-based effective sample-size claim is permitted without a separate derivation.

---

## 12. Frozen primary metric and stage gates

The proposed primary metric for the later formal 0047 preregistration is:

```text
EPISODE_LEVEL_DURABLE_HANDOFF_PREVALENCE
= target-eligible BTC-positive episodes containing a primary durable handoff
  / target-eligible BTC-positive episodes
```

A later valid 0047 run may receive:

```text
PASS_DURATION_AWARE_HANDOFF_MODEL_STAGE_ELIGIBLE
```

only if all of the following are true:

1. at least **5** distinct target-eligible BTC-positive episodes exist;
2. at least **3** distinct episodes contain a primary durable handoff;
3. episode-level durable handoff prevalence is at least **0.50**;
4. ETH is the primary handoff cause in at least **1** distinct episode;
5. SOL is the primary handoff cause in at least **1** distinct episode;
6. all primary events, censoring, cause assignments and episode boundaries are produced mechanically from the frozen definitions with zero manual relabeling;
7. no feature/horizon/universe/episode/target/oracle/VAR/lag/bootstrap definition changes after any 0047 output is observed;
8. canonical BRRK, winner lineage, exhaustion lineage, Phase 6, production authorization, signing and order submission remain unchanged.

Interpretation of a PASS is deliberately narrow:

> The exposed history contains enough recurrent, cross-episode and cross-cause durable handoff opportunities to justify a separately preregistered duration-aware handoff-model study.

A PASS does **not** prove predictability, does not prove CAGR improvement, does not authorize allocation, and does not admit an Edge Registry entry automatically.

Fail/insufficient states:

- fewer than 5 target-eligible episodes → `INSUFFICIENT_EPISODE_DIVERSITY`;
- episode diversity is sufficient but fewer than 3 handoff episodes or prevalence <0.50 → `FAIL_NO_RECURRENT_DURABLE_HANDOFF_STRUCTURE`;
- recurrent handoff passes but only one cause is ever observed → `INSUFFICIENT_COMPETING_RISK_DIVERSITY` for the proposed three-outcome ETH/SOL/no-handoff 0048 architecture. The evidence may justify only a differently scoped future research ID, not same-ID rescue;
- any post-result alteration of frozen scientific definitions invalidates the run rather than becoming a second 0047 result.

The 0.50 prevalence and minimum episode/cause diversity are prospective modeling-sufficiency gates, not estimates of future probability.

---

## 13. Explicit non-gating diagnostics

The following must be reported but cannot replace the primary metric or rescue a failed hard gate:

- cross-correlation peak lag;
- Granger/Wald p-values;
- VAR stability;
- generalized IRF shape;
- oracle uplift;
- existing V1 eligibility timing;
- causal feature event-time plots/tables;
- participation/trade-surprise behavior;
- handoff-age concentration;
- late ETH↔SOL switches after the primary event.

In particular, a strong oracle does not rescue absent recurrence, and significant Granger causality does not create a durable handoff event.

---

## 14. Explicitly forbidden under 0047

0047 may not:

- test BTC/winner `40/60`, `20/80`, `0/100` or any other portfolio mix;
- optimize CAGR, Sharpe, Calmar, MDD or turnover;
- modify V1/BRRK target weights or concentration caps;
- use BRRK final equity performance to choose episode/target/feature definitions;
- fit a hazard model, HMM, semi-Markov transition model, classifier, tree, boosting model or neural network;
- tune a handoff probability threshold;
- select a fixed `N days after BTC` delay from results;
- add BNB or other alts to the primary cause universe after seeing ETH/SOL results;
- select alternate 20/60 target horizons after output review;
- use BOCPD as a rescue candidate;
- create an Edge Registry PASS from descriptive DEVELOPMENT evidence alone;
- alter exhaustion 0043/0044/0045/0046 results;
- alter Phase 6, Phase 7, leverage, shorting, production, signing or order-submission authority.

---

## 15. Frozen downstream separation

If and only if 0047 satisfies its stage gates, a **new research ID** may preregister a duration-aware handoff model.

The currently intended later architecture, not yet preregistered, is:

```text
0048-style study:
  discrete-time competing-risk duration-aware model
  outcomes: NO_HANDOFF / ETH_HANDOFF / SOL_HANDOFF
  causal inputs drawn from the frozen information families above
  whole-episode held-out / leave-one-episode-out assessment
  no random daily-row train/test split
```

Portfolio translation remains one additional stage later:

```text
0049-style study:
  baseline BRRK / static winner benchmark / dynamic handoff portfolio
  winner concentration candidates frozen before economics
  net CAGR primary economics target
  transaction cost + cash conventions frozen before run
  oracle capture reported only as a bound
```

Exhaustion gross reduction remains a separate later stage. No combined lifecycle strategy is authorized by 0047.

---

## 16. Method-compliance checklist frozen into the design

Every later 0047 PR and run handoff must explicitly answer each item `YES / NO / NOT_APPLICABLE`:

```text
[ ] leader→follower→new-leader question preserved
[ ] canonical BTC-positive episode definition reused; no new bull threshold
[ ] fast + slow BTC absolute trend present
[ ] fast + slow ETH/BTC and SOL/BTC relative trend present
[ ] relative fast-minus-slow acceleration present
[ ] Beta breadth/diffusion present
[ ] trade-count participation confirmation present
[ ] state_age present
[ ] cross-correlation -14..+14 present
[ ] pooled episode-preserving VAR(7) present
[ ] bidirectional Granger/Wald panel present
[ ] generalized BTC-shock IRF 0..14 present
[ ] episode clustering preserved; no random daily split
[ ] 10,000 complete-episode bootstrap / seed 470047 used where uncertainty is reported
[ ] one-switch oracle isolated as hindsight opportunity bound only
[ ] BOCPD not used as primary or rescue candidate
[ ] no portfolio weights / 60-80-100 winner test under 0047
[ ] no final BRRK CAGR used for 0047 feature/label selection
[ ] exposed DEVELOPMENT history stated explicitly
[ ] zero production/signing/order authority
```

Any `NO` on a required item blocks a valid 0047 result until an implementation-only correction is made **before** any result release. After a valid result exists, scientific-definition changes require a new research ID.

---

## 17. Current lifecycle at this design freeze

```text
research_id proposed                  BRRK-BETA-HANDOFF-EVENT-STUDY-0047
design                                FROZEN BY THIS DOCUMENT
formal preregistration                NOT CREATED
PROGRAM_GOVERNED_V1 registry row      NOT CREATED
0047 dataset slice                    NOT REGISTERED
runner                                NOT CREATED
raw-data digest                       NONE
actual variants evaluated             0
historical result                     NONE
hazard model                          FORBIDDEN UNDER 0047
portfolio economics                   FORBIDDEN UNDER 0047
canonical BRRK change                 NONE
Phase-6 change                        NONE
production_authorized                 false
signature_authorized                  false
order_submission_authorized           false
```

The exact next lifecycle step after this design freeze is merged is a **separate preregistration-only PR**. That PR must copy these scientific definitions without modification, register typed lineage and the exposed DEVELOPMENT data slice, freeze one diagnostic protocol, set actual variants evaluated to zero, and still contain no runner or result.