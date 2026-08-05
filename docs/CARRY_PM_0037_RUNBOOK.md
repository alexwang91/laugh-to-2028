# CARRY-PM-0037 measurement-integrity runbook

`CARRY-PM-0037` supersedes the **gate design** of `CARRY-PM-0035` without editing or deleting the 0035 preregistration or runner. It remains a read-only account-state measurement: `/info` only, no signing, no order submission, and only a SHA-256 fingerprint of the public account address is retained.

> Upstream dependency: this probe is operationally required only if `CARRY-RF-0036R1` leaves the carry line qualified. A failed F1 risk-free hurdle stops the carry line under discipline #7; in that case do not spend live capital merely to exercise 0037.

## Unchanged 0035 limits

- dedicated probe account/subaccount;
- project probe notional cap: **$500**;
- the existing code permits at most **5% execution tolerance above that cap**, i.e. the observed spot notional must be `<= $500 × 1.05 = $525`; this tolerance is mechanical execution allowance, not a size search;
- spot quantity change from `spot` to `matched`: **<= 0.1%**;
- spot/short notional mismatch: **<= 2%**;
- Portfolio Margin ratio: **< 0.50**;
- if PM consumes margin, consumed margin / matched short notional: **<= 25%**;
- cash and closed UBTC residual market value: **<= $1**;
- no other perp positions.

## New F2 integrity limits — frozen before any account comparison

- `snapshot_gap_within_bound`: `spot` -> `matched` elapsed time must be **0 to 300 seconds** inclusive;
- `mid_drift_within_bound`: both UBTC spot midpoint and BTC perp midpoint must be present, and each absolute spot->matched drift must be **<= 0.0025 (25 bps)**.

The comparator records the two midpoint drifts separately and also persists their maximum. Missing timestamps or midpoints fail the corresponding integrity check; they are never treated as zero drift.

## Explicit margin states

The signed primary measurement is retained directly:

```text
raw_available_after_maintenance_change_usdc
  = available_after_maintenance_USDC(spot)
  - available_after_maintenance_USDC(matched)
```

It is no longer collapsed into one `max(0, ...)` number before classification.

- `PM_RELEASES_MARGIN`: integrity checks pass and raw change `< 0`; `released_margin_usdc = -raw`, `consumed_margin_usdc = 0`.
- `PM_CONSUMES_MARGIN`: integrity checks pass and raw change `> 0`; `consumed_margin_usdc = raw`, `released_margin_usdc = 0`.
- `MEASUREMENT_INCONCLUSIVE`: timing/drift checks fail, required values are missing, matched short notional is nonpositive, or raw change is exactly zero and therefore has no identified direction.

`MEASUREMENT_INCONCLUSIVE` can never pass the account-behavior gate. `PM_RELEASES_MARGIN` passes the direction-specific capital-efficiency sub-gate; `PM_CONSUMES_MARGIN` passes that sub-gate only when the unchanged 25% consumption threshold is met. All other 0035 structural checks still apply.

## Bounded `/info` retries

`post_info` uses the preregistered fixed policy:

- at most **4 total attempts**;
- per-attempt timeout **30 seconds**;
- backoff before retries: **0.5s, 1.0s, 2.0s**;
- retry only transport errors and HTTP **408/429/500/502/503/504**;
- other 4xx responses fail immediately.

No retry changes the request payload or account state; all calls remain read-only.

## Four-stage data capture

The state sequence remains `cash -> spot -> matched -> closed`. If this experiment ever becomes required after its upstream F1 dependency is satisfied, capture each stage with `run_carry_pm_0037.py snapshot`, then compare all four JSON files with `run_carry_pm_0037.py compare`.

Do not alter the 300-second, 25-bps, 2%, 0.50, 25%, $500/$525, 0.1%, or $1 bounds after observing any account result. A failed or inconclusive first valid probe is retained as negative evidence and does not authorize a rescue run.
