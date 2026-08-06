# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0.1 / P0.2: PASS / MERGED
- P1.1 through P1.8: PASS / MERGED
- Phase 1 Account and execution truth: COMPLETE
- P2.1 through P2.4: PASS / MERGED
- Phase 2 Hyperliquid instrument router: COMPLETE
- P2.4 implementation PR #66: PASS / MERGED
- P2.4 post-merge handoff / Master Plan BNB-policy synchronization PR #67: PASS / MERGED
- Current main baseline for P3.1: `221a9f7306adeee65715660a0224342881c5d9c1`
- Full project audit: `docs/FULL_PROJECT_AUDIT_2026-08-06.md`
- Current implementation PR: #68
- Current candidate branch: `p3-1/data-contract`

## Current roadmap position

```text
P2.1-P2.4: COMPLETE
Phase 2: COMPLETE
P3.1 Data contract: IMPLEMENTATION VERIFIED ON CANDIDATE / FINAL-HEAD CI REQUIRED / NOT MERGED
P3.2 Target calculation API: BLOCKED
P3.3+: BLOCKED
P4+: BLOCKED
```

P3.1 is the unique current task.

## P3.1 implementation contract

Machine-readable authority:

```text
config/data_contract.json
contract_id = BRRK-DATA-CONTRACT-P3.1-2026-08-06
```

Implementation:

```text
execution/plan-b-bot/beta_bot/data_contract.py
execution/plan-b-bot/beta_bot/strategy_data_source.py
research/integration/p3_1_data_contract_adapter.py
```

Detailed contract note:

```text
docs/P3_1_DATA_CONTRACT.md
```

`DATA-CONTRACT-P3.1 = IMPLEMENTATION_VERIFIED` is registered after successful candidate CI. This status verifies the data-contract engineering only; it authorizes no target generation or production trading.

## Strategy daily-close semantics

The frozen BRRK directional research source is preserved rather than silently replaced by execution-venue candles:

```text
source      = Binance spot klines
symbols     = BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT
interval    = 1d
timeZone    = 0 (UTC, explicit)
decision    = 00:00:00 UTC
```

At decision `D 00:00 UTC`, a daily candle is canonical only when:

```text
close_time_ms < decision_timestamp_ms
```

The latest required session therefore opens at `D-1 00:00 UTC`.

The source adapter makes `timeZone=0` explicit and permits fallback only between the two already-used Binance public spot endpoints. It does not switch exchange, instrument type or economic price series.

## Missing-data semantics

```text
NO forward fill
NO previous-close substitution
NO cross-venue substitution
NO incomplete-candle substitution
```

Common BRRK history begins at the latest first-available canonical day across BTC/ETH/SOL/BNB. From that point through the latest required session, every UTC day must exist for every asset. An internal or latest-session gap fails closed and canonical target input is not published.

Duplicate day, malformed day duration, non-midnight daily open, nonpositive/nonfinite close or ambiguous source mapping also fails closed.

## Asset/source mapping semantics

Strategy-source mappings are versioned explicitly in `config/data_contract.json`.

A consumed session must resolve to exactly one mapping under:

```text
valid_from_utc <= session < valid_to_utc
```

Overlap, ambiguity or a mapping gap on a consumed session fails closed. Historical mappings are not silently rewritten.

## Router funding / basis semantics

Strategy-price data and router/execution market observations are separate namespaces.

Canonical funding input:

```text
source         = Hyperliquid fundingHistory
window         = exact trailing 24 completed hourly slots before router_as_of
API unit       = decimal/hour
canonical unit = bps/hour
aggregation    = arithmetic mean
```

Missing/duplicate/non-hour-aligned required funding slots fail closed as unavailable cost input. Boundary/future funding observations are not consumed early.

Canonical basis:

```text
(perp_mark_price / verified_spot_price - 1) * 10000 bps
```

Both source observation timestamps are preserved; neither may be after router `as_of`; observed timestamp skew is retained for replay. P3.1 deliberately does not invent an arbitrary live freshness threshold.

## Research/live determinism

Research does not have a second candle-cleaning implementation. `research/integration/p3_1_data_contract_adapter.py` calls the exact same `beta_bot.data_contract` canonicalizer intended for live use.

Controlled tests require that different raw row ordering representing the same observations emits:

```text
research canonical JSON == live canonical JSON
research SHA-256 digest  == live SHA-256 digest
```

The byte-identical close sequence is also fed into the already-existing frozen signal component and produces identical signal/target-beta output. P3.1 does **not** implement the P3.2 multi-asset target API.

## Candidate CI evidence

Candidate head before decision/evidence writeback:

```text
cd55535cf4720e259109b0080104d642183e9efe
```

passed:

- `Phase 0 baseline contract` #86 / Actions `31108327909`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- `PR handoff governance` #108 / Actions `31108329917`: SUCCESS.

The decision-registry and evidence writeback changes the branch head, so **one final authoritative CI run is still required on the new exact head before merge**.

## Controlled test coverage

Tests cover:

1. canonical BTC/ETH/SOL/BNB scope and explicit no-production authorization;
2. exact UTC `00:00:00` decision timestamp;
3. exclusion of current/in-progress daily candle;
4. midnight-open / expected-close-time / positive-price validation;
5. explicit source-symbol enforcement;
6. internal missing-day failure with no forward fill;
7. latest-required-session failure;
8. order-independent canonical JSON/digest;
9. existing frozen signal target-beta parity from identical canonical history;
10. exact 24 completed hourly funding slots and bps/hour conversion;
11. missing funding-hour failure;
12. deterministic basis formula and observation-skew retention;
13. future basis-observation rejection;
14. versioned source-mapping boundary switch;
15. mapping-gap failure;
16. mapping-overlap failure;
17. research/live shared-adapter byte parity;
18. explicit Binance `timeZone=0` request;
19. same-source Binance endpoint fallback;
20. research integration contract reads the same machine-readable data contract.

## Self-review / scope audit

- No BRRK model parameter or weight formula changed.
- The frozen historical research result is not retuned or overwritten.
- P3.1 preserves Binance spot UTC daily signal-price semantics because that is the frozen research source; Hyperliquid remains the execution/router market-data venue.
- Missing data fails closed rather than changing the price path through imputation.
- Mapping changes are versioned rather than inferred from UI names.
- Router funding/basis units and cutoff semantics are explicit and replayable.
- P3.1 records basis observation skew but does not invent an unsupported freshness threshold.
- No P3.2 target API, P3.3 rebalance control, P3.4 cash-contribution logic, P4 leverage or P5 cycle-exit logic is implemented.

## Project drift audit — current P3.1

```text
DRIFT_0
```

The task follows the exact next roadmap dependency and changes no product, universe, venue, risk, security, research-rescue or production boundary.

Historical process `DRIFT_1` from the full audit remains preserved as history and is not reclassified away.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

The data contract authorizes no target, live capital, production route, leverage, short, withdrawal/external transfer, strategy release or cutover.

## Exact next action

```text
final-head CI on PR #68
-> expected-head merge if and only if all checks pass
-> documentation-only post-merge normalization to P3.2 Target calculation API
```

Do not begin P3.2 until PR #68 is merged and the canonical handoff is normalized.
