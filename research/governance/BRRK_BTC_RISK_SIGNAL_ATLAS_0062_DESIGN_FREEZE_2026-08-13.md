# BRRK BTC Risk Signal Atlas 0062 — DESIGN FREEZE

Date: 2026-08-13
Research ID: `BRRK-BTC-RISK-SIGNAL-ATLAS-0062`
Research family: `BRRK_BTC_TO_CASH_GROSS_RISK`
Research domain: `RISK_CONTROL`
Governance mode: `PROGRAM_GOVERNED_V1`
Stage: `DESIGN_ONLY`
Production authority: none

## 1. Scientific question

Build a broad, mechanism-organized atlas of causal information that may become useful to an outer BTC-to-Cash risk controller.

The 0062 question is not "which named technical indicator backtests best?" and it is not a rescue of 0061.

The question is:

> Across prospectively frozen signal families spanning market trend, trend change, momentum, reversal/exhaustion, volatility, price structure, volume/flow, breadth, relative crypto structure, derivatives, options, on-chain state, liquidity, macro/cross-asset state, sentiment/flows and structural-regime change, which distinct information mechanisms contain temporally recurrent information about short/intermediate BTC-vs-Cash opportunity cost, future path damage, future risk and reversal/regime-transition outcomes before any state-to-gross mapping or portfolio optimization is defined?

0062 is an information-atlas stage. It does not define BTC/Cash thresholds, gross exposure, re-entry, hysteresis, trading rules, strategy NAV or portfolio economics.

## 2. Why a new ID is required

0061 is immutable `FAIL_NO_JOINT_DOWNSIDE_INFORMATION / CLOSED`. It validly rejected one specific representation/question: the unchanged equal-weight A1/A2/A3 absolute-risk state did not rank all eight clipped terminal-loss/adverse-excursion targets positively across 20/60/120/240-day horizons.

0062 is scientifically different because it changes all of the following at the architecture level:

- the candidate information universe is much broader than A1/A2/A3;
- named indicators are organized by mechanism rather than treated as isolated candidates;
- target channels include signed BTC-vs-Cash opportunity cost, future path damage, future risk and reversal/regime-transition outcomes rather than only clipped downside severity;
- information is allowed to be horizon-specific under prospectively frozen horizon groups rather than requiring one daily signal to be monotone across 20/60/120/240 days;
- 0062 seeks family-level information fingerprints, not an immediate trading rule.

0062 may use prior 0044/0045/0046/0061 outcomes only as exposed DEVELOPMENT lineage. Those outcomes cannot select an indicator, parameter, horizon, target, threshold or family winner inside 0062.

## 3. Anti-anchoring rule

No user-mentioned or researcher-mentioned named indicator receives special authority merely because it was named before design.

Specifically, RSI, MACD, Supertrend and MA20 are examples inside larger mechanism families; none is the default winner, default benchmark or mandatory final representation.

The candidate space must be constructed from mechanisms first, then canonical mathematical representations, then numerical geometry. Named-indicator familiarity is not a selection criterion.

## 4. Primitive information channels

Every allowed signal must map to at least one primitive causal information channel. The initial ontology is:

1. price level and log return;
2. high/low/close range and true range;
3. trend slope and multi-scale trend disagreement;
4. return acceleration/deceleration;
5. realized variance/semivariance and volatility-of-volatility;
6. price location inside recent support/resistance/range structure;
7. volume level, change, imbalance or price-volume interaction;
8. cross-crypto breadth, dispersion, correlation and leadership;
9. leverage/derivatives positioning and liquidation state;
10. options-implied volatility and tail/skew pricing;
11. on-chain holder cost, realized profit/loss and exchange-flow state;
12. stablecoin/crypto liquidity and market depth;
13. cross-asset/macro risk and liquidity state;
14. sentiment/attention/flow state;
15. sequential process change / latent regime state.

A representation that is merely a deterministic cosmetic transformation of another representation does not become a new information family.

## 5. Frozen signal-family atlas

The DESIGN freezes the following broad mechanism families as the 0062 search universe. Exact numerical parameter grids, source contracts, eligibility and variant counts belong to PREREGISTRATION and must be frozen before outcome access.

### F01 — Trend level / direction

Examples of canonical representation classes:

- price versus SMA/EMA/WMA/HMA families;
- moving-average slope;
- rolling linear-regression slope;
- Aroon trend state;
- Ichimoku trend-location primitives;
- Parabolic-SAR direction;
- Donchian directional state.

Economic question: is the market already in a persistent directional state?

### F02 — Trend spread / trend disagreement

Examples:

- fast-minus-slow MA spread;
- multi-horizon momentum disagreement;
- fast/slow trend composite disagreement;
- price-versus-short-trend combined with short-versus-long trend.

This family includes the general mechanism behind prior trend-disagreement evidence but does not copy a result-informed 0044/0061 weighting.

### F03 — Trend acceleration / deceleration

Examples:

- change in MA spread;
- slope-of-slope / curvature;
- MACD histogram level and change;
- PPO histogram level and change;
- TRIX / KST-style acceleration transforms;
- momentum impulse decay.

Economic question: is trend strength changing before the level itself turns?

### F04 — Trend-cross / state-transition events

Examples:

- MACD zero-line crossing;
- MACD signal-line crossing;
- price/MA crossing;
- fast/slow MA crossing;
- Aroon directional crossing;
- Ichimoku cloud transition;
- trend-state duration since crossing.

Cross events are distinct from continuous level features and must be evaluated as event/state-transition information, not only as same-day values.

### F05 — Volatility-adjusted trend guards

Examples:

- Supertrend class;
- ATR trailing stop;
- Chandelier exit class;
- Keltner directional break;
- volatility-normalized price/trend distance.

Economic question: has directional structure broken by more than the prevailing volatility scale?

### F06 — Momentum level

Examples:

- RSI family;
- ROC;
- RMI;
- TSI;
- CMO;
- Ultimate Oscillator;
- Fisher-transformed momentum where causal and numerically well-defined.

Named oscillators are not independent families solely because their formulas differ.

### F07 — Overbought / oversold location

Examples:

- RSI tail location;
- Stochastic and Stoch-RSI;
- Williams %R;
- CCI;
- Bollinger %B;
- normalized distance from rolling range/trend.

Economic question: is price locally stretched relative to its recent state?

### F08 — Momentum/price divergence and exhaustion

Examples:

- price new high without oscillator new high;
- price new low without oscillator new low;
- RSI divergence;
- MACD/PPO divergence;
- trend-price disagreement;
- multi-swing weakening / failure to confirm.

Divergence must be defined algorithmically and causally; discretionary chart annotation is forbidden.

### F09 — Breakout, breakdown and failed-break structure

Examples:

- Donchian breakout/breakdown;
- rolling-high/low distance;
- lower-high / higher-low structure;
- breakout failure / return-inside-range;
- support/resistance break persistence;
- distance below prior high and time since high.

### F10 — Volatility regime / expansion / compression

Examples:

- realized volatility at multiple scales;
- ATR/price;
- Bollinger-band width;
- Keltner width;
- short/long volatility ratio;
- volatility-of-volatility;
- range-expansion and compression-release state.

This family may predict future risk even when it has little directional-return information.

### F11 — Downside asymmetry / jump / tail clustering

Examples:

- downside versus upside semivolatility;
- negative-return share;
- large-red-day frequency;
- downside jump count/severity;
- lower-tail realized variation;
- drawdown velocity and drawdown acceleration.

### F12 — Volume confirmation / price-volume divergence

Examples:

- raw and normalized volume shock;
- OBV class;
- MFI;
- CMF/accumulation-distribution class;
- volume-price trend confirmation;
- price breakout without volume confirmation;
- price/volume divergence.

### F13 — Cross-crypto breadth

Examples:

- fraction of a frozen crypto universe above short/medium/long trend;
- advance/decline style breadth;
- breadth momentum;
- breadth divergence versus BTC;
- cross-sectional dispersion;
- correlation concentration / correlation spike.

The constituent universe must be frozen before outcomes and survivorship handling must be explicit.

### F14 — Relative crypto structure / leadership / dominance

Examples:

- ETH/BTC and SOL/BTC trend deterioration;
- symmetric Beta/BTC relative state;
- BTC dominance change where source is reproducibly frozen;
- high-Beta versus BTC relative breadth;
- leadership dispersion and rotation speed.

Prior failed ETH/SOL micro-timing studies do not eliminate broad relative-risk information; prior results have no 0062 parameter authority.

### F15 — Derivatives leverage / crowding

Examples where immutable causal data can be obtained:

- perpetual funding level/change/extremes;
- futures basis and basis compression;
- open-interest level/change relative to price;
- OI/market-cap or OI/volume normalization;
- liquidation intensity/asymmetry;
- long/short positioning proxies;
- funding × OI interactions.

### F16 — Options-implied risk / tail pricing

Examples where reproducible history can be frozen:

- ATM implied volatility;
- IV term structure;
- put/call skew;
- risk reversals;
- downside wing richness;
- implied-realized spread;
- options volume/open-interest stress.

### F17 — On-chain holder state

Examples where source licensing and historical reproducibility permit:

- realized-price / holder-cost distance;
- MVRV-style valuation state;
- SOPR-style realized profit/loss;
- short-term versus long-term holder state;
- exchange inflow/outflow stress;
- realized-cap / realized-profit changes;
- dormant/old-coin spending state.

No proprietary metric may enter unless the source payload and transformation are reproducibly frozen under the data contract.

### F18 — Crypto liquidity / stablecoin / market-depth state

Examples:

- stablecoin supply/change where causally timestamped;
- exchange liquidity proxies;
- spot depth/spread/order-book imbalance when historical data are reproducible;
- turnover/liquidity shocks;
- depth withdrawal preceding volatility expansion.

### F19 — Cross-asset / macro risk and liquidity

Examples:

- equity risk trend and volatility;
- USD strength;
- rates/yield changes;
- broad financial-conditions/liquidity proxies;
- credit/risk-off state;
- BTC-versus-Nasdaq or BTC-versus-liquidity divergence.

Every macro series must use information actually available at the origin timestamp; revised macro releases may not be silently treated as point-in-time data.

### F20 — Sentiment, attention and exogenous flow

Examples where timestamped history is reproducible:

- search/attention measures;
- sentiment indices;
- ETF flow where historically available and correctly timestamped;
- exchange flow/attention shocks;
- social attention intensity.

Vendor black-box scores without reproducible historical semantics are ineligible.

### F21 — Sequential change detection / structural break

Examples:

- CUSUM-style change scores;
- Bayesian online changepoint concepts;
- residual change detection;
- volatility/trend structural-break scores;
- sequential likelihood-ratio state-change measures.

The purpose is to detect that the generating process changed, not to forecast an exact market top.

### F22 — Latent regime / state-space dynamics

Examples:

- HMM regime probabilities;
- causal state-space/Kalman trend and variance state;
- Markov-switching style states where estimable without lookahead;
- entropy/persistence/Hurst-style regime descriptors.

Any fitted latent-state model must have separately frozen training/update semantics and cannot refit using future data.

### F23 — Multi-timescale disagreement

Examples:

- daily versus weekly trend disagreement;
- short momentum weakness inside long bull trend;
- short volatility expansion inside long low-vol state;
- fast bearish transition while slow trend remains positive.

This family explicitly allows the possibility that a 5–20-session defensive signal is useful even though 120–240-session terminal returns later recover.

### F24 — Conditional interactions / state context

Examples conceptually include:

- trend deterioration conditional on volatility expansion;
- momentum exhaustion conditional on long-term uptrend;
- oscillator oversold conditional on improving breadth;
- price weakness conditional on leverage crowding;
- divergence conditional on high valuation/holder profit.

However 0062 itself may only measure predeclared low-order interaction diagnostics if PREREGISTRATION gives an explicit multiplicity budget. Open-ended interaction search, tree boosting, neural networks or arbitrary feature crossing are forbidden in the atlas stage. Broad combination/conditional-state construction belongs to a later new ID after family-level evidence exists.

## 6. Named-indicator catalog is not a candidate budget

The DESIGN intentionally names many familiar indicators to prevent anchoring on the most recently discussed examples. This list is an ontology aid, not permission to run every textbook parameterization.

No named indicator is eligible merely because it exists in technical-analysis literature or software libraries.

Before any historical outcome is accessed under 0062, PREREGISTRATION must freeze:

- which family representations are actually evaluated;
- why each representation is mathematically non-redundant enough to consume a candidate slot;
- exact parameter geometry and candidate count;
- exact source and causal timestamp semantics;
- exact target/horizon eligibility;
- the family-level multiplicity procedure.

Unfrozen indicators are `NOT_EVALUATED`, not silent reserves that can be introduced after seeing results.

## 7. Data-source tiers

0062 is intentionally broader than the existing price-only daily wrapper. Data are partitioned before preregistration into source tiers.

### Tier A — Existing/frozen market-internal data

Potentially includes causal OHLCV and cross-crypto price/volume information already available in repository evidence, subject to exact hash binding in PREREGISTRATION.

Families primarily supported here: F01–F14, F21–F23 and limited F24 diagnostics.

### Tier B — New crypto-native external data

Potentially includes derivatives, options, on-chain, stablecoin, ETF-flow and market-liquidity histories.

Families primarily supported here: F15–F18 and crypto-specific portions of F20.

Every Tier-B source must be captured/frozen before any outcome-based screening. A missing/unreproducible source produces an explicit `DATA_UNAVAILABLE` track outcome and may not be replaced post hoc by a convenient substitute.

### Tier C — New cross-asset / macro / sentiment data

Potentially includes equities, rates, USD, volatility indices, financial conditions, credit, flows and timestamped attention/sentiment series.

Families primarily supported here: F19–F20.

Point-in-time semantics and publication lags are mandatory. Revised macro values cannot be treated as contemporaneously known unless a true vintage series is used.

The numerical/data preregistration may split Tier A/B/C into independently governed tracks or child research IDs if immutable-data availability, licensing or support makes one giant execution scientifically unsafe. Such a split must happen before any 0062 historical target/association output.

## 8. Target-channel atlas

0062 does not reuse one target for every mechanism. It freezes distinct scientific target channels. Exact horizons, formulas, support thresholds and co-primary structure belong to PREREGISTRATION.

### T1 — Signed BTC-versus-Cash terminal opportunity cost

Purpose: measure whether Cash or BTC is preferable over the forward horizon without clipping BTC gains to zero.

Positive values represent Cash advantage / BTC underperformance; negative values represent BTC opportunity cost of being defensive.

### T2 — Forward path damage

Candidate concepts to formalize before execution:

- origin-relative maximum adverse excursion;
- drawdown-threshold incidence;
- drawdown velocity/severity;
- time-under-water or time-below-origin where causally meaningful.

This channel recognizes paths such as 100 -> 65 -> 105 as economically damaging even if terminal return later becomes positive.

### T3 — Future risk intensity

Candidate concepts:

- future realized volatility;
- future downside semivolatility;
- future large-negative-return/jump incidence;
- future tail-loss quantile/proxy.

A signal can therefore be useful for risk sizing even if it has no stable directional-return forecast.

### T4 — Reversal / exhaustion / regime-transition outcomes

Purpose: distinguish normal continuation/pullback from genuine deterioration or transition.

This channel may use frozen event-taxonomy concepts only if definitions are prospectively bound and prior labels are treated as exposed DEVELOPMENT history.

### T5 — Recovery / re-entry information

Purpose: characterize when defensive information stops being valid and the cost of delayed re-entry.

0062 may measure recovery-information diagnostics, but it may not translate them into a trading rule or optimize a re-entry threshold.

## 9. Horizon architecture

The DESIGN rejects the assumption that every daily risk signal must predict the same sign at all long horizons.

PREREGISTRATION must freeze a small, economically interpretable horizon geometry covering at least:

- very short reaction;
- short daily adjustment;
- intermediate swing/regime;
- longer recovery/opportunity-cost context.

The geometry must be selected before outcome access and cannot be pruned to favorable horizons after execution.

Family eligibility may differ by target/horizon for economic reasons, but these mappings must be frozen prospectively. A family cannot search all targets/horizons and later report only the best cell.

## 10. Information fingerprint, not one-number ranking

The primary 0062 output is a family-level information fingerprint.

For every evaluated family/representation, the lossless result should preserve prospectively frozen statistics across eligible target channels/horizons, including at minimum:

- effect direction and magnitude;
- temporal recurrence/stability;
- dependence-aware uncertainty;
- support/effective-sample diagnostics;
- redundancy with other representations inside the same family;
- missingness/source coverage;
- researcher-exposure status.

0062 must not collapse the atlas into an unconstrained leaderboard such as "top 10 indicators by historical Sharpe".

## 11. Multiplicity and anti-data-mining architecture

The broad atlas is only scientifically useful if family multiplicity is controlled.

The DESIGN freezes these principles; the exact statistical machinery must be preregistered before execution:

1. hierarchical evaluation: information family first, representation second, numerical geometry third;
2. no historical argmax parameter selection as authority;
3. broad parameter plateaus are preferred over isolated peaks;
4. dependence-aware simultaneous or hierarchical error control across tested families/targets is mandatory;
5. temporal recurrence is mandatory for promotion eligibility;
6. multiple highly correlated named indicators do not count as independent confirmations;
7. one favorable horizon/cell cannot rescue a family that fails its frozen family-level gate;
8. a negative family result remains preserved and closes same-ID rescue;
9. any later composite must be a new research ID with a new frozen feature budget;
10. researcher-exposed DEVELOPMENT evidence can never become independent OOS by relabeling or resampling.

Candidate statistical tools for preregistration include blocked/resampled max-statistic control, hierarchical false-discovery control, family-level omnibus tests, or other dependence-aware simultaneous inference. The choice itself must be frozen before historical output.

## 12. Representation geometry rule

Where a mechanism has numerical tuning parameters, PREREGISTRATION must use systematic low-dimensional geometry rather than folklore constants whenever feasible.

Examples:

- RSI lookback/threshold family;
- MACD fast/slow/signal geometry;
- Supertrend ATR-length/multiplier geometry;
- moving-average fast/slow geometry;
- Donchian/range lookback geometry;
- volatility short/long geometry;
- divergence lookback/separation geometry.

A single textbook default such as RSI-14, MACD-12/26/9 or Supertrend-10/3 may be included as a reference point but receives no privileged authority.

Geometry must be sufficiently coarse and bounded to test stability without turning 0062 into a combinatorial optimizer. Exact grids and total variant budget are preregistration items.

## 13. Redundancy analysis

0062 must explicitly quantify redundancy because many named indicators are transformations of the same primitive path.

Within-family and cross-family diagnostics may include prospectively frozen rank-correlation/redundancy matrices, effective-rank measures, cluster structure or residual incremental-information tests.

Redundancy diagnostics have no post-hoc permission to prune/reweight inside the same execution unless pruning rules were preregistered. Their primary purpose is to inform a later new-ID conditional-state design.

## 14. What 0062 is allowed to establish

A valid 0062 outcome may establish only:

- that one or more prospectively frozen information families show stable/recurrent information for specified target channels/horizons;
- that some families are redundant or complementary at the information level;
- that a family merits a separately governed geometry/refinement or conditional-combination study;
- that a family/data source fails and should be closed under its frozen specification.

A PASS does not authorize a BTC-to-Cash gross map.

## 15. What 0062 cannot establish

0062 cannot establish or authorize:

- an optimal BTC/Cash trading threshold;
- an optimal gross exposure level;
- a re-entry/hysteresis rule;
- portfolio CAGR/MDD improvement;
- production deployment;
- leverage or shorting;
- signing or order submission;
- modification of canonical BRRK-0011 or Phase 6;
- independent OOS evidence from researcher-exposed history.

## 16. Explicitly forbidden same-ID behavior

After preregistration/output, the following are forbidden under 0062 unless already prospectively frozen:

- add a new indicator because an evaluated one failed;
- remove an unfavorable horizon;
- select only favorable target channels;
- prune or reweight a family after seeing results;
- add cross-family interactions after seeing main effects;
- switch data vendor because the first source gave an unfavorable result;
- relax support, recurrence, multiplicity or uncertainty gates;
- convert descriptive diagnostics into promotion authority;
- tune a threshold/gross map on 0062 outcomes;
- rerun, retune or rescue the same research ID after durable execution authority is consumed.

## 17. Binding prior evidence

The following prior evidence is acknowledged but has no direct 0062 parameter-selection authority:

- `BRRK-EXHAUSTION-STATE-0044`: continuous exhaustion/risk state contained meaningful DEVELOPMENT event-discrimination evidence.
- `BRRK-EXHAUSTION-TRIGGER-0045`: the first discrete WATCH/RISK translation was too insensitive/persistent for promotion.
- `BRRK-EXHAUSTION-PULSE-0046`: the attempted anti-stickiness pulse translation became too sparse and failed true-event sensitivity.
- `BRRK-BTC-CASH-ABSOLUTE-RISK-DIAGNOSTIC-0060`: invalid unique execution, no scientific conclusion.
- `BRRK-BTC-CASH-ABSOLUTE-RISK-MEASUREMENT-REPLICATION-0061`: valid `FAIL_NO_JOINT_DOWNSIDE_INFORMATION`; unchanged A1/A2/A3 clipped-downside mechanism did not pass the all-eight G2 gate.
- legacy `EXPOSURE-SMOOTH-0038-CONTINUOUS-BETA`: historical evidence that smooth exposure control can materially alter drawdown/return trade-offs, but no automatic promotion authority.

These results motivate breadth of mechanism search and separation of information from control; they do not select the 0062 winners.

## 18. Planned continuation if 0062 produces eligible information

A plausible future ladder, subject to separately governed new IDs, is:

- Signal Atlas — family-level information discovery (`0062`);
- Signal Geometry — stable parameter/representation plateaus for eligible families;
- Conditional State — incremental/complementary low-order family combinations;
- Reactive Outer Risk Controller — state-to-gross translation and real portfolio economics;
- Controller robustness — costs, whipsaw, V-reversal, missed right-tail, temporal/dependence robustness;
- genuinely future-only validation.

IDs and exact ordering after 0062 are not authorized by this DESIGN; each requires a new design decision based on preserved evidence and governance state.

## 19. Stage boundaries

At DESIGN merge, 0062 must still have:

```text
central registry owner                  ABSENT UNTIL PREREGISTRATION
numerical/data preregistration          ABSENT
frozen candidate list/grid              ABSENT
historical 0062 outcomes                NOT COMPUTED
historical 0062 target values           NOT COMPUTED
historical 0062 indicator ranking       NOT COMPUTED
historical 0062 associations            NOT COMPUTED
historical 0062 portfolio economics     FORBIDDEN
actual variants evaluated               0
RUN_ATTEMPT.marker                      ABSENT
production_authorized                   false
signature_authorized                    false
order_submission_authorized             false
```

## 20. Exact next step after DESIGN merge

Create a separate numerical/data preregistration stage.

Before any historical 0062 output, preregistration must freeze at least:

1. exact Tier A/B/C data-source contracts and point-in-time semantics;
2. which families/representations are actually executable under 0062;
3. exact candidate/parameter geometry and total variant budget;
4. target formulas and horizon geometry;
5. support/effective-sample requirements;
6. temporal recurrence architecture;
7. dependence-aware multiplicity/error-control method;
8. family-level PASS/FAIL/INCONCLUSIVE classification precedence;
9. lossless result schema and exposure accounting;
10. exactly-once execution semantics.

No implementation or real historical 0062 computation is authorized by this DESIGN alone.
