# BRRK Cross-Sectional Momentum Factor Atlas 0086 — SPEC_FREEZE

Research ID: `BRRK-CROSS-SECTIONAL-MOMENTUM-FACTOR-ATLAS-0086`

Lifecycle: `PROSPECTIVE_FIVE_GATE_LIFECYCLE_V1`

Gate: `SPEC_FREEZE` = OWNER-FIRST + DESIGN + PREREGISTRATION

Branch status: `PREPARED_FOR_ATOMIC_REGISTRY_AND_HANDOFF / NOT_MERGED / NOT_RUN`

Controlled attempt: `0/1`

Controlled scientific/history payload reads: `0`

Scientific engine invocations: `0/1`

Scientific source-network fetches: `0`

Production/signature/order/withdrawal/transfer authority: `false`

## OWNER-FIRST

### Question

Does one independently motivated, prospectively fixed cross-sectional 60-session price-momentum factor contain reproducible positive 5-session forward ranking information across a point-in-time liquid crypto perpetual universe, after strict causal timing, support, dependence-aware inference, temporal/regime robustness, and family-wise accounting, without factor selection or result-informed rescue?

### Hypothesis

Assets with stronger trailing 60-session return at weekly decision time will, on average, rank above weaker trailing-return assets over the next fully matured 5 sessions. A valid PASS requires the effect to remain positive and sufficiently stable across time and broad market states rather than being driven by one year, one asset cluster, or one thin-liquidity tail.

### Economic mechanism

Cross-sectional momentum can arise from gradual information diffusion, persistent capital flows, heterogeneous investor updating, and slow portfolio rebalancing. This study tests only whether the ranking relation exists robustly. It does not claim deployable long/short economics.

### Independence from prior IDs

0086 is not a rerun, rescue, recomputation, source substitution, or parameter repair for 0075 or 0084.

- 0075 remains permanently blocked pre-attempt under its historical state.
- 0084 remains immutable `INVALID_EXECUTION`, attempt `1/1` consumed, with no admissible scientific factor result.
- 0086 inherits zero factor result, zero lifecycle credit, zero attempt budget, zero candidate choice, and zero scientific value from 0075/0084.
- 0086 asks a narrower scientific question with one independently justified price-momentum definition instead of reproducing the old 16-factor / 64-trial atlas.

### Downstream meaning

Only an immutable 0086 PASS may make this exact MOM60 factor definition eligible for a separately governed future Factor L/S research ID. PASS does not itself authorize a long/short sleeve, portfolio allocation, or production use.

## DESIGN

### Point-in-time universe

The controlled universe must be derived from Binance USD-M USDT-margined perpetual instruments using point-in-time information available by each decision timestamp. ARM must bind exact source objects and exact eligibility implementation before controlled reads.

At each weekly decision time, an asset is eligible only if all frozen conditions are met:

1. ordinary USDT-margined perpetual contract;
2. contract was already listed and tradable at the decision timestamp;
3. at least 120 fully completed daily sessions exist before the decision close;
4. trailing 30-session median daily quote-volume is available and finite;
5. the asset ranks in the top 30 by trailing 30-session median quote-volume among otherwise eligible contracts;
6. complete, finite closes exist for the MOM60 lookback and 5-session forward-return maturation window when that label later matures;
7. stablecoins, wrapped/pegged duplicates, leveraged tokens, delivery futures, and non-USDT quote contracts are excluded.

No end-of-sample survival filter may determine historical membership. A later-delisted asset remains eligible historically when it satisfied the contemporaneous rules.

### Decision timing

- Decision cadence: every Monday UTC daily close present in the bound dataset.
- Feature timestamp: close of decision session `t`.
- Feature may use only fully completed observations at or before `t`.
- Forward label: log return from close `t` to close `t+5` daily sessions for that asset.
- A label enters analysis only after all 5 forward sessions have matured.
- No centered windows, future-filled values, revised future metadata, or end-of-sample membership knowledge.

### Exactly one factor candidate

`MOM60_RAW`

For asset `i` at decision time `t`:

`MOM60_RAW(i,t) = log(close(i,t) / close(i,t-60))`

No alternate lookback, skip window, sign inversion, residualization, volatility scaling, winsorization family, nonlinear transform, or post-result factor addition is permitted under 0086.

### Cross-sectional representation

At each decision timestamp:

1. compute MOM60 only for the frozen eligible universe;
2. require at least 10 eligible assets, otherwise that decision date has insufficient cross-sectional support and contributes no IC observation;
3. rank MOM60 with deterministic average ranks for exact ties;
4. rank the fully matured 5-session forward return using the same tie convention;
5. compute Spearman rank IC between the two rank vectors;
6. record cross-sectional count, raw MOM60 distribution, forward-return distribution, and IC.

No Q5-Q1 portfolio return is a PASS criterion in 0086. Quantile spreads may be persisted as descriptive diagnostics only if implemented prospectively in BUILD and they cannot rescue a failed IC gate.

### Primary target

`ROBUST_POSITIVE_WEEKLY_MOM60_TO_FWD5_SPEARMAN_RANK_IC`

### Support and partitions

BUILD must implement the following frozen partitions without looking at controlled values:

- full eligible weekly sequence;
- calendar-year partitions;
- four chronological blocks formed by equal-count contiguous weekly IC observations after support filtering, with deterministic earlier-block tie allocation;
- BTC market-state partition using only causal BTC trailing 60-session return sign at the same decision time: `BTC_UP` if positive, otherwise `BTC_NONUP`;
- cross-sectional liquidity partition using the median of each decision date's eligible-universe trailing-30-session median quote-volume, split relative to the expanding historical median available through the prior decision date. The first decision lacking a prior expanding median is unclassified for this secondary partition only.

No partition threshold may be tuned from 0086 outcomes.

### Multiple testing

Scientific candidate count is exactly 1. Primary hypothesis count is exactly 1. No factor-family tournament is conducted. Secondary partitions are robustness diagnostics, not separate promotion candidates and cannot substitute for the primary gate.

### Evidence tier

`RESEARCHER_EXPOSED_DEVELOPMENT_NOT_INDEPENDENT_OOS`

A PASS is DEVELOPMENT evidence only and can authorize only a new separately preregistered validation or Factor L/S study.

## PREREGISTRATION

### Frozen statistical calculations

For the weekly IC series:

- primary point estimate: arithmetic mean weekly Spearman IC;
- median weekly IC;
- fraction of weekly IC observations strictly positive;
- Newey-West/HAC standard error with lag exactly 4 weekly observations;
- two-sided HAC t-statistic for mean IC, reported descriptively;
- dependence-aware moving-block bootstrap of the mean IC with block length 8 weekly observations, exactly 10,000 replicates, seed `860086`;
- bootstrap interval: percentile 95% interval;
- lower confidence bound used for PASS: 2.5th percentile of bootstrap mean IC distribution.

If there are fewer than 104 valid weekly IC observations, classify `INCONCLUSIVE_INSUFFICIENT_SUPPORT` before applying economic/scientific PASS gates.

### Frozen PASS gates

A valid execution is `PASS_VALIDATED_MOM60_FACTOR` only if every gate below passes:

- G0: at least 104 valid weekly IC observations;
- G1: full-sample mean weekly Spearman IC >= 0.025;
- G2: moving-block-bootstrap 95% lower bound for mean weekly IC > 0.0;
- G3: fraction of weekly IC observations > 0 is >= 0.55;
- G4: at least 3 of 4 chronological blocks have mean IC > 0;
- G5: no chronological block has mean IC <= -0.025;
- G6: at least 3 distinct calendar years each contain >=20 valid weekly observations and positive mean IC;
- G7: both `BTC_UP` and `BTC_NONUP` states each contain >=30 valid weekly observations and have mean IC > 0;
- G8: leave-one-calendar-year-out mean IC is > 0 for every removable year that leaves >=104 observations;
- G9: every persisted input/read/candidate/accounting invariant is exact and all computed statistics are finite.

The 0.025 primary mean-IC threshold is a preregistered minimum effect-size floor. It is not selected from 0086 controlled outcomes.

### Frozen terminal classification

- `PASS_VALIDATED_MOM60_FACTOR`: valid execution and all G0-G9 pass.
- `FAIL_NO_ROBUST_MOM60_FACTOR`: valid execution with sufficient support, but one or more G1-G8 scientific gates fail.
- `INCONCLUSIVE_INSUFFICIENT_SUPPORT`: valid execution but G0 or a prospectively required state/year support gate cannot be evaluated because support is below its frozen minimum.
- `INVALID_EXECUTION`: source identity, manifest/hash, schema, timestamp, point-in-time membership, read count, candidate count, non-finite calculation, persistence, network, marker ordering, source-interface, or exactly-once contract is violated.

PASS/FAIL/INCONCLUSIVE are scientific outcomes. INVALID_EXECUTION is not scientific evidence.

### BUILD constraints

BUILD may use synthetic/nonhistorical fixtures only. It must implement one complete payload-bytes-to-terminal-classification engine and synthetic tests for PASS, every scientific FAIL gate, insufficient support, NaN/non-finite data, missing timestamps, schema drift, duplicate/missing object, point-in-time membership errors, and deterministic bootstrap reproducibility.

BUILD may not read controlled scientific/history payload values.

### ARM constraints

ARM must bind exact controlled artifact/object identities, exact manifest SHA-256 and byte sizes, exact runtime source-key namespace, exact expected read count, exact source-qualified engine interface, unique result branch, and zero-result preflight.

Pre-marker ARM/preflight may inspect only identity, filename, central-directory metadata, declared hashes/sizes, exact head, and absence of result markers. It may not call `testzip()`, decompress entries, open payload members, CRC-scan payload bytes, or expose scientific values.

### RUN constraints

RUN requires new explicit user authorization for `0086 controlled RUN attempt 1/1` after ARM is merged and zero-result preflight passes.

RUN must use the currently qualified `ControlledResearchRunnerV1SourceQualified` path and preserve this order:

1. exact-head and zero-result metadata-only preflight;
2. durable create-only `RUN_ATTEMPT.marker`;
3. remote durability verification;
4. controlled reads within frozen per-object budget;
5. exactly one scientific engine invocation;
6. create-only result bundle persistence;
7. durable `RUN_ONCE.marker` seal.

After marker durability, attempt `1/1` is consumed regardless of PASS/FAIL/INCONCLUSIVE/INVALID_EXECUTION. No same-ID rerun, retune, rescue, source substitution, candidate replacement, history extension, or recomputation is allowed.

If the common runner causes a new `INVALID_EXECUTION`, all new scientific attempts stop until prospective runner repair and complete requalification. Governance must not create a replacement-ID chain that simply retries this same question.

### SEAL constraints

SEAL reads persisted result evidence only and performs no scientific recomputation. It records terminal classification, execution accounting, evidence limitations, immutable no-rerun state, and the exact legal downstream dependency.

## What did not change

- 0076 remains sealed at its Stage7 pre-marker read-boundary incident. No 0076 replacement, retroactive marker, same-ID Stage8, rerun, retune, rescue, or recompute is authorized by 0086.
- 0072/0073 Carry remain paused and are not rerun.
- 0083 remains immutable FAIL with no rescue.
- 0084 remains immutable `INVALID_EXECUTION`; 0086 receives no scientific result or lifecycle credit from it.
- 0085 remains permanently sealed `INVALID_EXECUTION / CLOSED TO SAME-ID RERUN`; 0086 is not an 0085 replacement.
- `workflow run                         31381953131 / attempt 1` remains unchanged.
- CAPTURE-0001 remains sealed/no-retry.
- CAPTURE-0002 remains permanently claimed/no-refetch.
- Phase6 R1 closeout remains `PASS_FROZEN_LIVE_OBSERVATION_GATES` and grants no production authority.
- `CONTROLLED_RESEARCH_RUNNER_V1` plus source-interface qualification and future source-qualified-runner policy remain governing prospective infrastructure.
- Production/signature/order/withdrawal/transfer authority remains false.
