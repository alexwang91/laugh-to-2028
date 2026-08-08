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
    ↓ later, separately armed one-shot execution only
Stage-1 primary result
```

The first historical capture is complete and its provenance/exposure is registered. The Stage-1 **Run Interface is now frozen but not executed**. No real Stablecoin feature series, real Stage-1 BRRK state path, Ridge fit, OOS prediction or research result has been produced by this interface work.

## Files

- `DATA_CONTRACT.json` — frozen source identity, coverage rule, field/unit binding, PIT semantics and Stablecoin feature definition.
- `CAPTURE_GATE.json` — frozen first-history capture sequence and durable-receipt boundary.
- `CAPTURE_EXECUTION.json` — closed record of the single successful metadata-only first capture.
- `FIRST_CAPTURE_EVIDENCE.json` — immutable capture provenance and frozen historical coverage metadata.
- `RUN_INTERFACE.json` — exact Stage-1 dataset binding, canonical BRRK baseline state, label, paired-row rules, walk-forward purge, normalization, Ridge estimator, HAC test, classification/release rules and one-shot execution lock.
- `SOURCE_AUDIT.md` — source provenance and known historical PIT limitations.
- `source_defillama.py` / `raw_vintage.py` / `data_contract.py` / `capture_once.py` — frozen source/capture/data primitives.
- `run_interface.py` — deterministic Stage-1 interface primitives only; no real-data model execution.
- `test_data_contract.py`, `test_capture_gate.py`, `test_run_interface.py` — synthetic offline regressions. They do not call the live Stablecoin source or run Stage-1.

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

## One-shot / release boundary

Stage-1 has **not** run. A later execution must first claim the create-only `RUN_ONCE_STAGE1.marker` before any result-bearing calculation and may never delete that claim to retry the same research ID.

The first result release is restricted to the frozen primary classification/metric fields. It cannot initially expose predictions, coefficient paths, feature importance, alternative lags/alphas/horizons or secondary metrics. FAIL or INCONCLUSIVE stops this research ID. PASS only permits creation of a separately preregistered Stage-2 robustness research ID.

## No-result / authority boundary

Current state remains:

- `result_status = PREREGISTERED_NOT_RUN`;
- `actual_variants_evaluated = 0`;
- no real Stage-1 feature computation;
- no real Ridge fit or OOS predictions;
- no primary research result;
- no Edge Registry admission;
- no portfolio integration;
- no BRRK, leverage, short, Phase 6/7/8 or production-authority change.
