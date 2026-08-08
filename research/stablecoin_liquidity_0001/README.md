# STABLECOIN-LIQUIDITY-0001

Status: `PREREGISTERED_NOT_RUN`  
Authority: research only; `production_authorized=false`

This directory is the prospectively owned formal path registered by `STABLECOIN-LIQUIDITY-0001` before path creation.

## Layering

```text
DefiLlama source
    ↓ exact HTTP bytes
first-capture gate
    ↓ persist + verify before parse
immutable raw vintage + manifest + durability receipt
    ↓
registered validation slice / RAW_DATA exposure
    ↓ frozen exact LAG_2D transform
STABLECOIN_LIQUIDITY_STATE_V1
    ↓ frozen Run Interface
paired baseline vs augmented walk-forward Ridge information test
    ↓ irreversible one-shot execution claim + main-push token
Stage-1 primary result
```

The first historical capture is complete and its provenance/exposure is registered. The Stage-1 Run Interface is frozen. The current execution branch has **claimed the irreversible `RUN_ONCE_STAGE1.marker` and armed the executor, but Stage-1 has not executed**. Pull-request CI is synthetic/preflight only; result-bearing work is conditioned on the separately controlled main-push token `[STABLECOIN_STAGE1_EXECUTE_V1]`.

## Files

- `DATA_CONTRACT.json` — frozen source identity, coverage rule, field/unit binding, PIT semantics and Stablecoin feature definition.
- `CAPTURE_GATE.json` — frozen first-history capture sequence and durable-receipt boundary.
- `CAPTURE_EXECUTION.json` — closed record of the single successful metadata-only first capture.
- `FIRST_CAPTURE_EVIDENCE.json` — immutable capture provenance and frozen historical coverage metadata.
- `RUN_INTERFACE.json` — exact Stage-1 dataset binding, canonical BRRK baseline state, label, paired-row rules, walk-forward purge, normalization, Ridge estimator, HAC test, classification/release rules and one-shot execution lock.
- `RUN_ONCE_STAGE1.marker` — irreversible create-only Stage-1 claim. If this branch is merged, the research ID is consumed even if execution later fails or invalidates; the marker may not be deleted to rerun the same ID.
- `STAGE1_EXECUTION.json` — armed one-shot result-execution contract; production authority remains false.
- `stage1_price_capture.py` — pre-result create-only Binance raw-page capture and manifest writer for the frozen P3.2 market-data window.
- `stage1_execution.py` — frozen batch P3.2 state construction, canonical multi-date parity gate, paired walk-forward Ridge comparison, HAC classification and primary-only result writer.
- `SOURCE_AUDIT.md` — source provenance and known historical PIT limitations.
- `source_defillama.py` / `raw_vintage.py` / `data_contract.py` / `capture_once.py` — frozen source/capture/data primitives.
- `run_interface.py` — deterministic Stage-1 interface primitives.
- `test_data_contract.py`, `test_capture_gate.py`, `test_run_interface.py` — synthetic offline regressions. Pull-request CI additionally runs `stage1_execution.py --self-test`; none of these execute the real Stage-1 dataset/model comparison.

## Captured validation slice

The single first capture is bound as:

```text
dataset_slice_id      STABLECOIN-LIQUIDITY-0001-DEFILLAMA-HIST-V1
exposure_id           STABLECOIN-LIQUIDITY-0001-RAW-DATA-20260808T141719Z
data_budget           VALIDATION
contamination_state   RESEARCHER_EXPOSED_HISTORY
consumed              true
historical_start      2017-11-29T00:00:00Z
historical_end        2026-08-08T00:00:00Z
raw_sha256            7cffe6fb3a21e891082c06c60e91491edfbc78e9c01e2d549805815a646d9ffd
```

Historical source rows do not expose verifiable original publication/first-seen timestamps. They therefore remain reconstructed `RESEARCHER_EXPOSED_HISTORY`; the frozen primary historical availability rule is exactly `available_at = metric_timestamp + 2 calendar days`. This dataset is not sealed and is not `TEMPORALLY_UNSEEN`.

## Frozen Stage-1 comparison

The baseline is not a substitute model. It is the continuous canonical P3.2 BRRK price/regime state exposed by `P3.2-BRRK0011-V1`, frozen as a 35-column vector. The augmented model appends exactly two columns:

```text
stablecoin_growth_20d
stablecoin_growth_acceleration_20d
```

At decision timestamp `D 00:00 UTC`, Stablecoin uses the exact metric date `D-2d` and exact `D-22d` / `D-42d` levels. No interpolation, forward fill, LAG_1D or LAG_3D substitution is allowed.

The label is the future 20-calendar-day compounded net return of the canonical daily P3.2 BRRK target path under the frozen 5 bps BRRK research turnover-cost convention. Baseline and augmented models use exactly the same paired rows and labels.

Walk-forward rules are frozen as expanding training only, minimum 365 fully realized training labels, 20-day label purge, `StandardScaler` fit on training rows only, and `Ridge(alpha=1.0, solver="svd")` with no parameter grid. PASS still requires at least 730 valid OOS predictions and the preregistered one-sided Newey-West/HAC lag-19 test at alpha 0.05.

## One-shot execution boundary

The armed push executor is intentionally separated from pull-request CI:

1. PR CI compiles the capture/execution code and runs synthetic `--self-test` only.
2. If and only if the fully green PR is merged with `[STABLECOIN_STAGE1_EXECUTE_V1]`, the first `main` push attempt may execute.
3. `github.run_attempt == 1` is required; a GitHub rerun cannot execute the Stage-1 job again.
4. The frozen Stablecoin raw SHA256 is verified.
5. Exact Binance pages are captured and uploaded as an immutable Actions artifact **before** model evaluation.
6. A hash-bound Binance durability receipt is itself archived before evaluation.
7. A batch historical P3.2 state path is built using the same frozen target math; before Ridge, it must match canonical `calculate_target()` on the six committed parity dates.
8. Only after those gates pass may the single paired baseline/augmented walk-forward Ridge variant execute.
9. Predictions and coefficients remain in memory only. The only persisted result is the frozen primary-result JSON.
10. The primary JSON is uploaded before any job-summary release.

Any failure after this branch is merged consumes the Stage-1 claim. There is no automatic retry, no deletion of the marker and no same-ID rescue run.

## Release boundary

The first result release is restricted to the frozen primary classification/metric fields. It cannot initially expose predictions, coefficient paths, feature importance, alternative lags/alphas/horizons or secondary metrics. FAIL or INCONCLUSIVE stops this research ID. PASS only permits creation of a separately preregistered Stage-2 robustness research ID.

## Current no-result / authority boundary

Until the controlled main-push execution actually occurs:

- `result_status = PREREGISTERED_NOT_RUN`;
- `actual_variants_evaluated = 0`;
- Stage-1 execution contract = `ARMED_NOT_EXECUTED`;
- irreversible run-once marker = `CLAIMED_BEFORE_RESULT_BEARING_EXECUTION` on this branch;
- no real Stage-1 feature/model comparison has executed;
- no OOS primary result exists;
- no Edge Registry admission;
- no portfolio integration;
- no BRRK, leverage, short, Phase 6/7/8 or production-authority change.
