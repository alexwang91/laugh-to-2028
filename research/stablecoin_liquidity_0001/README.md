# STABLECOIN-LIQUIDITY-0001

Status: `FAIL_NO_INCREMENTAL_INFORMATION / TERMINAL_STOP`  
Authority: research only; `production_authorized=false`

This directory is the prospectively owned formal path registered by `STABLECOIN-LIQUIDITY-0001` before path creation.

## Terminal result

Stage-1 executed **exactly once** under the frozen `STABLECOIN-LIQUIDITY-0001-RUN-INTERFACE-V1` on merge commit `dd50ec35085eee2a2883dc1b29e3dd21ec52b043`, GitHub Actions run `31264048473`, run attempt 1.

The immutable primary result is:

```text
classification                       FAIL_NO_INCREMENTAL_INFORMATION
valid_oos_prediction_count           933
mean_primary_loss_differential       -5430210.12771038
hac_max_lag                          19
hac_test_statistic                   -1.2454264237630361
hac_one_sided_p_value                0.8935124773215692
primary_result_digest                d920d45397d45ae5636a2f3c682600778d4d087d97e035ba911844cca65821ff
```

The preregistered failure rule was triggered because the mean primary loss differential (`MSE_baseline - MSE_augmented`) is non-positive. The augmented Stablecoin model therefore did **not** demonstrate incremental predictive information beyond the frozen canonical P3.2 BRRK price/regime state.

This research ID is terminally stopped. `RUN_ONCE_STAGE1.marker` remains permanently committed and may not be deleted to rerun. There is no LAG1/LAG3 rescue, alpha/horizon/feature-representation retuning, repeated evaluation, Stage-2 robustness eligibility, Edge Registry admission, portfolio integration, BRRK change or production authorization from this result.

## Layering and provenance

```text
DefiLlama source
    ↓ exact HTTP bytes
first-capture gate
    ↓ immutable raw vintage + manifest + durability receipt
registered validation slice / RAW_DATA exposure
    ↓ frozen RUN_INTERFACE.json
irreversible RUN_ONCE_STAGE1.marker
    ↓ exact Binance input capture + durable receipt
canonical P3.2 multi-date parity gate
    ↓ exactly one paired walk-forward Ridge Stage-1 run
immutable primary-only result
    ↓
FAIL_STOP / NO PROMOTION / NO RERUN
```

## Key files

- `DATA_CONTRACT.json` — pre-result frozen Stablecoin source/PIT/feature contract.
- `CAPTURE_GATE.json` — pre-result frozen first-history capture boundary.
- `CAPTURE_EXECUTION.json` — closed first-capture execution record.
- `FIRST_CAPTURE_EVIDENCE.json` — first-capture provenance/coverage evidence.
- `RUN_INTERFACE.json` — immutable pre-result Stage-1 statistical/execution interface. It remains unchanged after the result.
- `RUN_ONCE_STAGE1.marker` — permanent irreversible Stage-1 claim.
- `STAGE1_EXECUTION.json` — closeout record for the exactly-once Stage-1 execution.
- `STAGE1_PRIMARY_RESULT.json` — immutable primary-only result evidence and artifact provenance.
- `stage1_price_capture.py` / `stage1_execution.py` — exact code used for the frozen execution; the live Stage-1 workflow entry has been removed after use.
- `run_interface.py` and synthetic tests — deterministic frozen interface/reference logic.

## Validation data

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

Historical DefiLlama rows do not expose verifiable original publication/first-seen timestamps, so this history remains reconstructed `RESEARCHER_EXPOSED_HISTORY`, never sealed or `TEMPORALLY_UNSEEN`.

## Frozen Stage-1 design

The baseline was the frozen 35-column continuous canonical P3.2 BRRK price/regime state. The augmented model appended exactly two preregistered Stablecoin columns:

```text
stablecoin_growth_20d
stablecoin_growth_acceleration_20d
```

At decision `D 00:00 UTC`, Stablecoin used exact `D-2d`, `D-22d`, `D-42d` metric dates. Baseline and augmented models used identical paired rows, labels, walk-forward dates, minimum 365 fully realized expanding training rows, training-only `StandardScaler`, and `Ridge(alpha=1.0, solver="svd")`. The primary test used one-sided Newey-West/HAC lag 19 and required at least 730 OOS predictions.

Before Ridge, the historical batch P3.2 state path passed parity against canonical `calculate_target()` on all six frozen parity dates. Exact Binance input pages and a hash-bound receipt were durably archived before model evaluation. Predictions, coefficients and secondary metrics were not persisted or released.

## Durable evidence

Stage-1 run `31264048473` produced immutable Actions artifacts:

- Binance input artifact `9023613464`, digest `sha256:26748abdd75a7568872617b5bc2f6618b8b3a315cbcd785cf1175e4c606354db`.
- Binance receipt artifact `9023613629`, digest `sha256:bdf9ed3486c426c75f4b7cd9eed2e88bc2843c457459481b0eb56e14429ce9d3`.
- Primary result artifact `9023630485`, digest `sha256:6eac38957c3592e18eb2cb4706e87be12daeca6cfe504065af19e944984674f1`.

The input ZIP, receipt ZIP, primary-result ZIP and primary JSON were additionally mirrored outside the repository to ChatGPT Library under the Stage-1 execution SHA folder, preserving the immutable evidence chain.

## Final authority boundary

- `actual_variants_evaluated = 1`.
- `result_status = FAIL_NO_INCREMENTAL_INFORMATION`.
- `promotion_state = NO_PROMOTION`.
- Stage-2 robustness = **not eligible**.
- Edge Registry = **no entry**.
- portfolio integration = **none**.
- BRRK/BNB/parameters/costs = **unchanged**.
- Phase 6/7/8 authority = **unchanged**.
- production authorization = **none**.
- first real short authorization = **none**.

`ONCHAIN-HOLDER-COST-0001` remains a separate backlog research idea. It is not started, preregistered or evaluated by this Stablecoin closeout.
