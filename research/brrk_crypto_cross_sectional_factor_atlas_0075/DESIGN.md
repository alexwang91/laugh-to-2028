# 0075 Stage 2 DESIGN — Cross-Sectional Factor Atlas

Research ID: `BRRK-CRYPTO-CROSS-SECTIONAL-FACTOR-ATLAS-0075`

Lifecycle stage: `2/10 DESIGN`.

Parent Stage1 merge: `f162c21cfccfe8a7801f78c4e07e357cdf20f93e`.

Controlled attempt budget at DESIGN: `0/1`; controlled historical/evidence reads: `0`; scientific engine calls: `0`; scientific source-network fetches: `0`.

## Economic question

Determine whether prospectively defined, point-in-time-valid cross-sectional factor families contain reproducible ranking information across a tradable crypto universe. This stage defines the bounded research architecture only. It does not evaluate factor returns, IC, significance, rankings, winners, or deployable long/short economics.

## Point-in-time universe design

Stage3 PREREGISTRATION must freeze, before any controlled history read:

- minimum listing age;
- minimum liquidity/ADV and capacity criterion;
- venue count/quality requirements;
- market-cap or other point-in-time capacity screen if used;
- stale-price and missingness policy;
- delisting/dead-asset treatment;
- token migration, redenomination and fork treatment;
- exclusion rules for stablecoins, wrapped duplicates and non-comparable instruments;
- timestamp normalization and as-of availability semantics.

Universe membership at rebalance `t` may use only information available by `t`. Future survival, later venue availability, revised metadata, or end-of-sample inclusion may not determine historical membership.

## Bounded factor-family ceiling

Only the roadmap families below may enter Stage3 candidate definitions. Stage3 must freeze exact formulas, controls, lookbacks, rebalance cadence, quantile construction, trial counts and family multiplicity before controlled history.

### Price

- momentum;
- short-term reversal;
- residual momentum;
- drawdown/recovery state.

### Risk

- realized volatility;
- residual/idiosyncratic volatility;
- market beta;
- prospectively defined downside beta/tail risk.

### Market structure

- funding;
- basis;
- OI/OI change;
- liquidity/spread;
- volume surprise.

### Network/economic state

Allowed only where the definition and availability timestamp are point-in-time valid and semantically comparable:

- transaction/network activity;
- fees/economic usage;
- supply growth/issuance;
- holder concentration;
- TVL/economic activity.

No additional family may be introduced after controlled history exposure under 0075.

## Frozen analysis architecture

For every preregistered factor, Stage3 must instantiate the roadmap order prospectively:

1. determine point-in-time universe at rebalance `t`;
2. obtain only feature values available by `t`;
3. apply frozen stale/missing filter;
4. winsorize using a frozen cross-sectional rule;
5. standardize or rank using a frozen rule;
6. if allowed, residualize only against prospectively frozen controls;
7. form frozen quantiles or equivalent cross-sectional buckets;
8. allow forward returns to enter analysis only after full maturity;
9. calculate spread, monotonicity and Spearman rank IC;
10. assess IC stability across prospectively declared time/regime partitions;
11. calculate turnover/capacity proxies;
12. apply family-wise multiple-testing correction across declared hypotheses;
13. apply leave-year/theme/size-bucket robustness where supported;
14. persist every tested factor definition and full trial count;
15. qualify factors for 0076 only under frozen Stage3 robustness gates.

## Residualization and controls

Stage3 may use a bounded control set consisting only of prospectively defined market beta, size, volatility and theme/sector controls where point-in-time semantics are valid. It must freeze whether residualization occurs per factor and the exact estimation chronology. Final-history performance may never decide whether a factor is residualized.

## Multiple testing and trial accounting

The Stage1 registry ceiling remains the governing upper bound: total declared factor variants may not exceed `64` without a new prospective research ID. Stage3 must assign every factor definition to a declared family, count every evaluated variant, freeze family-wise multiplicity treatment, and persist failed/null variants as well as any qualified variants.

No pruning, regrouping, family reassignment, threshold rescue, candidate replacement, or uncounted exploratory variant is allowed after controlled history exposure.

## Robustness families

Stage3 must prospectively freeze numerical requirements for, at minimum:

- yearly stability;
- bull/bear and high/low-volatility stability where supported;
- liquidity-regime stability;
- leave-year-out robustness;
- leave-theme-out robustness where theme definitions are point-in-time valid;
- leave-size-bucket-out robustness;
- turnover/capacity diagnostics;
- missingness and universe-composition stress;
- multiplicity-adjusted evidence.

## Terminal meaning

`PASS` for 0075 means one or more preregistered factor definitions satisfy all prospectively frozen atlas robustness and multiplicity requirements. It means only that those definitions may become immutable inputs to 0076.

`PASS` does not establish a deployable long/short strategy, portfolio alpha, production authority, or independent OOS evidence.

Failure to support qualified factors, invalid controlled execution, or insufficient support must remain terminal under the later frozen Stage3 classification rules. Result-informed rescue is forbidden.

## Stage3 freeze checklist

Before Stage3 can merge it must freeze exact:

- source families and point-in-time identities;
- universe eligibility thresholds and exclusions;
- factor formulas and lookbacks;
- rebalance cadence;
- stale/missing/winsorization/ranking rules;
- residualization controls and chronology;
- quantile/bucket definitions;
- forward-return horizons and maturity barrier;
- regime definitions;
- turnover/capacity formulas;
- multiplicity method and family mapping;
- robustness gates and minimum support;
- trial count within the Stage1 ceiling;
- terminal classifications;
- Stage8 exactly-once budgets and marker-before-read execution requirements.

## Exactly-once and evidence scope

No controlled scientific/history payload may be opened during Stage2. No scientific engine may run. No source-network fetch may occur as part of a later controlled attempt. The later Stage8 attempt must follow durable `RUN_ATTEMPT.marker` before every authorized controlled content read, exactly one scientific engine invocation where the frozen design requires it, create-only result persistence, and final `RUN_ONCE.marker` sealing.

Researcher-exposed historical evidence remains DEVELOPMENT history and must never be described as independent OOS.

## Production authorization

`production_authorized=false`

`signature_authorized=false`

`order_submission_authorized=false`
