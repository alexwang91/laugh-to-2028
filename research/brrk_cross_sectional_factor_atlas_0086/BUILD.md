# BRRK Cross-Sectional Factor Atlas 0086 — BUILD

Research ID: `BRRK-CROSS-SECTIONAL-FACTOR-ATLAS-0086`
Gate: `BUILD`
Controlled attempt: `0/1`
Controlled value reads: `0`
Scientific engine calls: `0/1`

## Build scope

This gate implements the merged SPEC_FREEZE with synthetic/nonhistorical fixtures only. It does not bind controlled source identities and does not inspect historical controlled payload values.

The implementation lives in `research/brrk_cross_sectional_factor_atlas_0086/engine.py`. The source-qualified engine class is `CrossSectionalFactorAtlas0086Engine`; future RUN must place it behind `ControlledResearchRunnerV1SourceQualified`.

## Exact implementation frozen here

- PIT eligibility requires 120 completed daily sessions including the completed decision session, a matured `t+5` close, finite positive close, and nonnegative quote volume.
- Weekly decisions use Monday UTC daily-session close.
- The liquid universe ranks each eligible symbol by median quote volume across completed sessions `t-29..t`, descending with symbol-name tie break, and takes the top 30. Cross-sections below 10 symbols are skipped as invalid support.
- `MOM60_RAW = log(close_t / close_t-60)`.
- `RVOL20_RAW` is sample standard deviation of the 20 daily log returns ending at `t`, using closes `t-20..t`.
- `LIQ30_RAW = log(median quote_volume[t-29..t])`.
- Ties use average ranks. Weekly primary IC is Pearson correlation of the two average-rank vectors, i.e. Spearman IC.
- The raw economic diagnostic is equal-weight top factor tercile minus bottom factor tercile. Each selected leg has unit gross weight, so the raw long-short book has gross 2. The persisted overall IC sign multiplies both the spread and all diagnostic weights; negative IC therefore uses bottom-minus-top.
- One-way rebalance turnover across both legs is `sum(abs(w_t - w_{t-1}))` over the union of symbols, starting from zero weights. The 10 bps and 20 bps panels subtract `turnover * bps / 10000` from each aligned five-session spread observation. No result-dependent alternate accounting is allowed.
- BTC state is now frozen prospectively: `BTC_UP` iff `BTCUSDT MOM60_RAW > 0` at the Monday decision close; otherwise `BTC_NONUP`. This uses only information available at the decision session.
- Four chronological blocks use deterministic rounded index boundaries `round(i*n/4)`, `i=0..4`.
- Qualifying calendar years require at least 20 weekly observations. `BTC_UP` and `BTC_NONUP` each require at least 30.
- Leave-one-year-out diagnostics remove each qualifying calendar year in turn and require every remaining mean IC to retain the persisted sign.
- Moving-block bootstrap uses block length 8, 10,000 replicates, one deterministic RNG seeded `860086`, and fixed factor order `MOM60_RAW`, `RVOL20_RAW`, `LIQ30_RAW`. The two-sided null distribution resamples the mean-centered IC series. The 95% CI resamples the uncentered IC series. The finite-sample p-value uses the plus-one correction.
- Holm step-down adjusts exactly the three primary p-values at family-wise alpha 0.05.
- HAC lag-4 t-statistic is persisted as a Newey-West/Bartlett diagnostic and cannot override bootstrap/Holm decisions.
- G0-G9 and terminal classifications implement the merged SPEC_FREEZE literally. If any frozen support minimum fails, the Atlas returns `INCONCLUSIVE_INSUFFICIENT_SUPPORT`. With adequate support, at least one factor passing every G0-G9 yields `PASS_VALIDATED_FACTOR_ATLAS`; otherwise the valid terminal result is `FAIL_NO_ROBUST_FACTOR_FAMILY`.

## Source-qualified adapter

The BUILD adapter accepts the two namespaces already demonstrated by the 0085 incident and repair:

- `stage/payloads/data__futures__um__monthly__klines__<SYMBOL>__1d__<SYMBOL>-1d-YYYY-MM.zip`
- `payloads/data__futures__um__monthly__klines__<SYMBOL>__1d__<SYMBOL>-1d-YYYY-MM.zip`

`validate_source_keys()` operates on filenames only and does not open payload bytes. It rejects unknown namespaces, duplicate logical `(symbol, month)` objects across either namespace, and a manifest without BTCUSDT. This validation is suitable for the source-qualified runner's pre-marker interface check.

Only after the durable RUN marker and runner-owned verified payload reads may `execute()` open an inner monthly ZIP, read its single CSV member, and consume `open_time`, `close`, and `quote_volume`. Inner ZIP/CRC/runtime failures propagate to the common runner. The engine does not convert them into a scientific result mapping.

## Synthetic qualification

`research/governance/test_0086_factor_atlas_build.py` covers:

- exact factor formulas;
- both staging and GitHub artifact source namespaces;
- duplicate logical object rejection across namespaces;
- unknown source-key rejection;
- post-marker ZIP/CSV column normalization;
- exact three-test Holm family;
- valid insufficient-support classification;
- a full adequate-support synthetic Atlas with the frozen 10,000-replicate bootstrap;
- presence of all G0-G9 gates;
- source-qualified engine interface and fail-closed validation.

All fixtures are generated synthetically in the test process. No controlled historical value is opened by BUILD or its tests.

## ARM boundary

ARM must bind exact artifact/object identities, declared hashes and sizes, exact source keys, schema contract, source-qualified runner interface, expected controlled read budget, result/marker paths, and engine-call budget without payload traversal. ARM may inspect central-directory metadata and declared identity metadata only. It must not call `testzip()`, decompress an inner ZIP, parse CSV, CRC-scan payloads, or expose controlled values before a durable RUN marker.

## What did not change

- The three factor representatives, thresholds, multiplicity family, support minima, cost levels, terminal classifications, and attempt budget remain exactly as merged in SPEC_FREEZE.
- Controlled attempt remains `0/1`; controlled reads remain `0`; scientific engine calls remain `0/1`.
- 0085 remains immutable `INVALID_EXECUTION`, attempt 1/1 consumed, with no admissible Trend answer and no same-ID rerun.
- 0076 remains sealed; 0072/0073 remain paused; 0083 remains immutable FAIL.
- Phase6 PASS closeout and the common runner qualification remain unchanged.
- No production, signing, order, withdrawal, or transfer authority is granted.
