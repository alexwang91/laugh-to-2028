# BRRK Multi-Horizon Trend Vol-Target 0085 — SEAL

Research ID: `BRRK-MULTI-HORIZON-TREND-VOL-TARGET-0085`

Terminal state: `INVALID_EXECUTION / CLOSED TO SAME-ID RERUN`

The single authorized controlled attempt 1/1 was consumed on 2026-08-25. The durable `RUN_ATTEMPT.marker` was created before controlled source reads. The common runner then read exactly 201 ARM-bound controlled objects and invoked the scientific engine exactly once. The engine failed with `TrendExecutionError:UNKNOWN_CONTROLLED_SOURCE:payloads/data__futures__um__monthly__klines__BTCUSDT__1d__BTCUSDT-1d-2021-01.zip`. The create-only result records `scientific_result_admissible=false`, and `RUN_ONCE.marker` seals the attempt.

No Trend performance conclusion is admissible from 0085. The failure is an execution-interface defect: the 0085 adapter regex expects names prefixed by `stage/payloads/`, while the frozen RUN manifest intentionally strips the staging-container prefix and supplies runner context names beginning with `payloads/`. This mismatch occurs after marker creation and after the exactly-once controlled read pass, so the attempt cannot be retried or repaired in place.

Under the project rule that a new infrastructure-caused `INVALID_EXECUTION` pauses new science, Trend, Factor and Options controlled attempts remain paused until the shared execution-interface qualification is strengthened prospectively. No 0085 replacement ID is created by this closeout.

## Immutable execution evidence

- unique RUN workflow: `32859047927` / attempt 1;
- RUN head: `1db59100b730b8aee1b5daa0000d0027f53256c1`;
- marker created at `2026-08-25T14:22:19.333170Z`;
- result produced at `2026-08-25T14:22:20.965646Z`;
- controlled source reads: `201`;
- scientific engine invocations: `1`;
- terminal classification: `INVALID_EXECUTION:ENGINE_OR_RUNTIME_FAILURE:TrendExecutionError`;
- scientific result admissible: `false`;
- production/signature/order/withdrawal/transfer authority: `false`.

## Required prospective repair

Before any new controlled scientific attempt, the public runner/build qualification must verify the exact post-marker `context.sources` key interface consumed by the configured execution adapter. Qualification must exercise representative manifest member names exactly as the runner will present them, rather than only synthetic JSON-source interfaces. A passing repair may protect future IDs but cannot reopen, rerun, recompute or rescue 0085.

## What did not change

- 0085 frozen science, source identities, candidate count, parameters, cost panels and decision rules remain unchanged.
- Attempt 1/1 remains permanently consumed. Same-ID rerun, retune, rescue, recomputation, source substitution and result reinterpretation are forbidden.
- 0070/0071/0083/0072/0073/0074/0075/0084 remain immutable in their recorded states.
- 0076 remains sealed at its Stage7 pre-marker read-boundary incident with no replacement or retroactive marker.
- `workflow run                         31381953131 / attempt 1`, CAPTURE-0001 sealed/no-retry and CAPTURE-0002 permanently claimed/no-refetch remain unchanged.
- Phase6 closeout remains unchanged.
- No production/signature/order/withdrawal/transfer authority is granted.

## Next legal step

Merge this immutable SEAL after exact-head mandatory CI reaches terminal green. Then repair and requalify the shared controlled execution-interface contract using synthetic/nonhistorical data only. Do not start a new Trend, Factor or Options controlled attempt until that prospective infrastructure repair is merged and qualified.
