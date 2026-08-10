# BRRK-BETA-HANDOFF-EVENT-STUDY-0047

Status: **IMPLEMENTED_PRE_RESULT_NOT_RUN / IMPLEMENTATION-ONLY CANDIDATE**

Design boundary:

`398b7ec3f78f602461787b1b45e8d5041729e126`

Formal preregistration boundary:

`80c0d3cb7339012cac74e20563e07c7139ba3031`

Binding design:

`research/governance/BRRK_BETA_HANDOFF_EVENT_STUDY_0047_DESIGN_FREEZE_2026-08-11.md`

Binding preregistration:

`research/brrk_beta_handoff_0047/PREREGISTRATION.json`

Run contract:

`research/brrk_beta_handoff_0047/RUN_INTERFACE.json`

## Question

After the canonical BTC fast trend becomes positive, does researcher-exposed BTC/ETH/SOL history contain recurrent, duration-aware handoffs in which ETH or SOL becomes a unique durable relative leader?

0047 is **not** a portfolio optimization study. It does not answer how much to allocate after a handoff and does not fit the later duration-aware handoff model.

## Frozen anatomy implemented

`engine.py` mechanically implements only the preregistered Stage-1 anatomy:

- universe BTC / ETH / SOL;
- Binance UTC daily OHLCV + quote-volume + trade-count, frozen through `2026-08-02`;
- exact V1 trend horizons `20 / 60 / 120 / 240`;
- exact FAST weights `0.15 / 0.25 / 0.30 / 0.30`;
- exact SLOW weights `0.10 / 0.20 / 0.30 / 0.40`;
- BTC-positive episodes are maximal contiguous common daily sessions with `BTC_TREND_FAST >= 0`;
- ETH/BTC and SOL/BTC fast/slow relative trend;
- relative acceleration = `REL_FAST - REL_SLOW`;
- Beta breadth = share of ETH/SOL with both absolute-fast and relative-fast > 0;
- trade participation = `log(1+daily trades)` minus trailing-60 median;
- raw one-based state age;
- separate hindsight durable target requiring the same unique Beta winner over BTC and the competing Beta at both +20 and +60 sessions while BTC itself is positive on both horizons;
- unavailable +60 target is right-censored, never negative;
- earliest durable handoff is primary within each BTC-positive episode;
- event-time causal anatomy grid `-60..+20`;
- episode-preserving BTC/ETH and BTC/SOL return cross-correlation at lags `-14..+14`;
- pooled episode-preserving VAR(7) with episode fixed intercepts;
- all six directed Granger/Wald diagnostics using episode-cluster CR0 where nonsingular;
- generalized one-residual-standard-deviation BTC-shock IRFs at horizons `0..14`;
- complete-episode bootstrap with exactly 10,000 replicates and seed `470047`;
- one-switch BTC→ETH/SOL hindsight oracle with a 10 bps full-switch cost, isolated as non-gating opportunity bound.

## Pre-result implementation clarifications

These resolve engineering semantics without creating candidate freedom:

1. Raw requests still start on `2020-08-01`. The common daily history begins at the latest first available date across BTC/ETH/SOL. From that common start through `2026-08-02`, every calendar day must exist for all three assets or execution fails closed. No synthetic backfill is permitted.
2. Cross-correlation uses `corr(BTC_t, ALT_{t+lag})`; positive lag therefore means BTC leads.
3. A transmission return on the first day of a BTC-positive episode is unavailable because its prior close lies outside that episode. Cross-episode return pairs and VAR lags are forbidden.
4. Pooled VAR(7) episode intercepts are implemented with within-episode demeaning, algebraically equivalent to explicit episode-dummy-intercept OLS. There is no lag search.
5. Granger/Wald uses episode-cluster CR0 covariance. A singular covariance produces a null descriptive p-value rather than a rescue estimator.
6. The generalized IRF avoids arbitrary contemporaneous Cholesky ordering.
7. Oracle switches are evaluated at the candidate close. Exact ties retain `NO_SWITCH`, then ETH precedes SOL only as a deterministic non-gating tie order.
8. The raw common market frame is canonically JSON-serialized and SHA256-bound before any result metric is emitted.

## Frozen Stage-1 gates

A later valid execution can receive `PASS_DURATION_AWARE_HANDOFF_MODEL_STAGE_ELIGIBLE` only if:

1. at least 5 distinct target-eligible BTC-positive episodes exist;
2. at least 3 distinct episodes contain a primary durable handoff;
3. episode-level durable handoff prevalence is at least 0.50;
4. at least one ETH-cause episode exists;
5. at least one SOL-cause episode exists.

The implementation does not allow VAR, Granger, IRF, oracle or event-time diagnostics to rescue these gates.

## Run interface

The later controlled execution is split into two create-only stages:

```text
prepare-data
  -> fetch frozen Binance history
  -> fail-closed common-index validation
  -> create-only MARKET_EVIDENCE.json
  -> canonical payload SHA256

evaluate
  -> verify market-evidence SHA256
  -> run exactly one frozen 0047 anatomy protocol
  -> create-only PRIMARY_RESULT.json
  -> create-only EXECUTION.json
  -> create-only RUN_ONCE.marker
```

No market evidence, result, execution record or marker exists on this implementation branch.

## Explicitly forbidden in 0047

- no 40/60, 20/80, 0/100 or other allocation test;
- no CAGR/Sharpe/Sortino/Calmar/MDD/turnover optimization;
- no hazard/semi-Markov model fit under this ID;
- no HMM/classifier/boosting/neural-net candidate;
- no fixed N-day switch-delay search;
- no BOCPD rescue;
- no BNB/other-alt expansion;
- no alternate 20/60 target horizon;
- no oracle-informed feature/label/model/allocation selection;
- no canonical BRRK, winner, exhaustion, Phase-6, leverage, shorting, signing, order-submission or production change.

## Current lifecycle

```text
design                              MERGED / 398b7ec3f78f602461787b1b45e8d5041729e126
formal preregistration              MERGED / 80c0d3cb7339012cac74e20563e07c7139ba3031
PROGRAM_GOVERNED_V1                REGISTERED
dataset slice                       REGISTERED / DEVELOPMENT EXPOSED
declared variants                   1
actual variants evaluated           0
engine                              IMPLEMENTED PRE-RESULT
run interface                       IMPLEMENTED PRE-RESULT
market evidence                     NOT CREATED
historical result                   NONE
duration-aware model                FORBIDDEN UNDER 0047
portfolio economics                 FORBIDDEN
production_authorized               false
signature_authorized                false
order_submission_authorized         false
```

The exact next step is to make this implementation branch fully green, verify the final diff contains no generated evidence, and merge it as a zero-result implementation boundary. Only after that immutable boundary exists may a separate controlled execution branch prepare the market evidence and execute 0047 exactly once.