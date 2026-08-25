# BRRK Cross-Sectional Factor Atlas 0086 — SPEC FREEZE

Research ID: `BRRK-CROSS-SECTIONAL-FACTOR-ATLAS-0086`
Lifecycle: `PROSPECTIVE_FIVE_GATE_LIFECYCLE_V1`
Current gate: `SPEC_FREEZE`
Controlled attempt: `0/1`
Controlled value reads: `0`
Scientific engine calls: `0/1`
Production/signature/order/withdrawal/transfer authority: `false`

## Scientific question

Do any prospectively fixed cross-sectional momentum, volatility, or liquidity factor families contain reproducible point-in-time predictive and economic structure across a liquid crypto perpetual universe after dependence-aware multiple testing and realistic/stressed costs?

0086 is an independent Factor Atlas. It is not a replacement or retry for 0075, 0076, 0084, or 0085 and inherits zero lifecycle credit, attempt credit, factor-selection credit, or scientific result from them. Factor L/S remains forbidden unless this Atlas returns a valid PASS and only passing families may become eligible for a separately governed future ID.

## Owner-first boundary

The central owner record for `BRRK-CROSS-SECTIONAL-FACTOR-ATLAS-0086` was committed to `config/research_registry.json` before this governed path was introduced. No controlled historical value was read in the owner-registration step.

## Frozen factor family

Exactly three primary factor representatives are admissible. No fourth family or alternate definition may be added after this SPEC_FREEZE.

| Family | Frozen representative | Definition at decision session t | Primary orientation |
|---|---|---|---|
| Momentum | `MOM60_RAW` | `log(close_t / close_{t-60})` | two-sided discovery with persisted sign |
| Volatility | `RVOL20_RAW` | standard deviation of daily log returns over completed sessions `t-19..t` | two-sided discovery with persisted sign |
| Liquidity | `LIQ30_RAW` | `log(median daily quote_volume over completed sessions t-29..t)` | two-sided discovery with persisted sign |

Size/market-cap and carry/funding are excluded from 0086. No qualifying point-in-time source identity for either family was frozen before this SPEC_FREEZE. They cannot be introduced later under 0086.

No residualization, volatility scaling, nonlinear transform, skip window, alternate lookback, alternate sign choice, ensemble, composite, or factor pruning is allowed.

## Frozen point-in-time universe

At each weekly decision time:

1. venue is Binance USD-M USDT perpetuals only;
2. an instrument must have at least 120 completed daily sessions before the decision session closes;
3. eligibility/ranking uses only information available through that completed decision session;
4. rank eligible instruments by trailing 30 completed-session median quote volume;
5. select the point-in-time top 30;
6. require at least 10 eligible instruments after finite-data checks or that weekly cross-section is invalid;
7. later listings, delistings, symbol changes, or future liquidity cannot alter past membership.

No survivorship-based fixed terminal universe is allowed.

## Frozen decision timing and horizon

- decision cadence: Monday UTC daily-session close only;
- factor observation: through the completed decision session `t`;
- earliest affected holding return: `t -> t+1`;
- forward outcome: fully matured 5-session return from close `t` to close `t+5`;
- incomplete final horizons are excluded mechanically and may not be padded or shortened;
- no intraday information is allowed.

## Frozen cross-sectional transforms

For each valid weekly cross-section and each factor:

1. compute the raw frozen factor value;
2. rank finite values cross-sectionally using average ranks for ties;
3. compute Spearman rank correlation with the 5-session forward return;
4. persist the observed IC sign; tests are two-sided and the sign cannot be chosen after significance is known;
5. build one diagnostic equal-weight top-minus-bottom tercile spread using the persisted factor ordering; if the observed IC sign is negative, the economically aligned spread orientation is bottom-factor minus top-factor;
6. no winsorization, z-score clipping, neutralization, sector adjustment, beta adjustment, or alternate rank method is allowed.

The tercile spread is a diagnostic economic confirmation only. It does not authorize a Factor L/S strategy or production position.

## Frozen multiple-testing family

The primary multiplicity family contains exactly three tests: `MOM60_RAW`, `RVOL20_RAW`, `LIQ30_RAW`.

- primary statistic: mean weekly Spearman IC;
- primary null: mean IC = 0, two-sided;
- dependence-aware uncertainty: moving-block bootstrap over weekly IC observations, block length 8;
- bootstrap replicates: 10,000;
- bootstrap seed: `860086`;
- family-wise correction: Holm step-down;
- FWER alpha: `0.05`;
- candidate/test count: exactly 3;
- no result-dependent removal or replacement of a test is allowed.

HAC lag-4 t-statistics are persisted diagnostics only and cannot override the frozen bootstrap/Holm decision.

## Frozen cost panels

For each factor's economically aligned equal-weight tercile spread:

- gross spread is persisted;
- realistic round-trip turnover cost: `10 bps` applied to measured one-way weight turnover on both legs under the frozen accounting implementation;
- stressed round-trip turnover cost: `20 bps` under the same accounting;
- no funding, borrow, market-impact, leverage, or options assumptions are introduced in 0086;
- if the available source cannot support truthful cost accounting, the affected economic gate is `INCONCLUSIVE`, never imputed.

The Atlas cannot tune a rebalance schedule or holding horizon to improve costs.

## Frozen support minima

A factor is scientifically evaluable only if all apply:

- at least 104 valid weekly IC observations overall;
- at least 4 chronological blocks can each be formed with at least 20 valid observations;
- at least 3 calendar years each contain at least 20 valid weekly observations;
- `BTC_UP` and `BTC_NONUP` states each contain at least 30 valid weekly observations;
- every evaluated weekly cross-section contains at least 10 eligible instruments.

BTC state uses only information available at the decision session and its exact implementation must be frozen in BUILD before ARM. BUILD may only encode the preregistered state rule and may not inspect controlled values to choose it.

## Frozen per-factor PASS gates

A factor passes the Atlas only if every gate passes in one valid controlled execution:

- `G0_EXECUTION`: all identity, causality, finite-statistic, read, candidate-count, persistence, source-interface, and exactly-once invariants pass;
- `G1_SUPPORT`: all frozen support minima pass;
- `G2_MULTIPLE_TESTING`: Holm-adjusted two-sided primary p-value `< 0.05` within the exact three-test family;
- `G3_BOOTSTRAP`: moving-block-bootstrap 95% confidence interval for mean IC excludes zero;
- `G4_SIGN_FRACTION`: at least 55% of weekly IC observations share the persisted overall IC sign;
- `G5_CHRONOLOGY`: at least 3/4 chronological blocks share the overall IC sign and no block mean has opposite-sign magnitude >= 0.025;
- `G6_CALENDAR`: at least three qualifying calendar years share the overall IC sign;
- `G7_BTC_STATE`: both qualifying BTC states share the overall IC sign;
- `G8_LEAVE_ONE_YEAR_OUT`: every eligible leave-one-calendar-year-out mean IC retains the overall IC sign;
- `G9_ECONOMIC`: the 10 bps net tercile spread shares the IC-implied economic sign and the 20 bps stressed spread does not reverse that sign.

0086 terminal PASS requires at least one of the three factors to pass all G0-G9 gates. No tie-break chooses a preferred factor inside 0086; every independently passing factor is persisted.

## Frozen terminal classifications

- `PASS_VALIDATED_FACTOR_ATLAS`: valid execution and at least one frozen factor passes every G0-G9 gate.
- `FAIL_NO_ROBUST_FACTOR_FAMILY`: valid execution, adequate support, and zero factors pass every frozen gate.
- `INCONCLUSIVE_INSUFFICIENT_SUPPORT`: valid execution but frozen support or truthful economic accounting is insufficient to decide the exact Atlas.
- `INVALID_EXECUTION`: any marker-ordering, manifest/hash, source identity, schema/timestamp, point-in-time membership, read-count, candidate-count, non-finite, network, persistence, source-interface, or exactly-once invariant fails.

`INVALID_EXECUTION` answers zero scientific questions. If the common source-qualified runner causes a new INVALID_EXECUTION, all new controlled science pauses until runner repair and requalification. 0086 does not create a replacement retry chain.

## Trial budget and stopping rule

- factor candidates: exactly 3;
- universes: exactly 1;
- horizons: exactly 1 (`FWD5`);
- rebalance schedules: exactly 1 (Monday UTC close);
- feature representations: exactly 1 raw rank representation per family;
- controlled attempts: maximum `1/1` and only after separate user authorization;
- RUN must use `ControlledResearchRunnerV1SourceQualified`;
- durable `RUN_ATTEMPT.marker` must precede every controlled payload read;
- scientific engine may execute at most once;
- create-only result persistence and `RUN_ONCE` sealing are mandatory;
- once RUN begins, no same-ID rerun, retune, rescue, source substitution, candidate replacement, family addition, history extension, threshold change, seed change, or recomputation is allowed.

## BUILD and ARM boundaries

BUILD may use only synthetic/nonhistorical fixtures. It must freeze the exact PIT universe algorithm, factor formulas, Monday decision calendar, BTC state rule, rank/tercile accounting, turnover-cost accounting, Holm implementation, bootstrap implementation, support checks, terminal classifier, and source-qualified runner adapter. BUILD must not open controlled historical values.

ARM may inspect only permitted identities/metadata and must bind exact controlled artifact/object identities, declared hashes and sizes, expected source keys, schema contract, source-qualified runner interface, expected controlled read budget, result path, marker path, and engine-call budget. Pre-marker `testzip()`, decompression, CRC traversal, payload parsing, or controlled value reads are forbidden. After ARM, source substitution is forbidden.

## What did not change

- `workflow run                         31381953131 / attempt 1` remains immutable.
- CAPTURE-0001 remains sealed/no-retry.
- CAPTURE-0002 remains permanently claimed/no-refetch.
- 0070/0071/0083/0072/0073/0074/0075/0076/0084/0085 terminal states remain immutable.
- 0085 remains `INVALID_EXECUTION` with attempt 1/1 consumed and no admissible Trend scientific result.
- Phase6 PASS closeout remains unchanged.
- No production, signing, order, withdrawal, or transfer authority is granted.
