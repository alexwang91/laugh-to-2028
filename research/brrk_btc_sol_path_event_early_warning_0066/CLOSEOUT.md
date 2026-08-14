# BRRK-BTC-SOL-PATH-EVENT-EARLY-WARNING-0066 — IMMUTABLE CLOSEOUT

Status: `INVALID_EXECUTION / CLOSED TO SAME-ID RERUN`

Date: 2026-08-14

## Terminal classification

0066 is closed as an execution invalidation, not as a scientific PASS or FAIL.

The unique authorized historical execution attempt was consumed and did not complete. No complete historical result bundle exists, so 0066 supports no inference about event predictability, classifier quality, controller economics, CAGR, terminal wealth, drawdown, robustness, or promotion.

## Exactly-once accounting

- research ID: `BRRK-BTC-SOL-PATH-EVENT-EARLY-WARNING-0066`
- authorized historical attempt: `1 / 1 CONSUMED`
- boundary merge SHA: `b1af358577349c58a8468a3822775152b5aaad34`
- workflow run: `31806690040`
- workflow job: `94787213750`
- durable attempt-marker commit: `03e6f5a099c9163ff14c3387d4d06f0dff4f368a`
- `RUN_ATTEMPT.marker`: PRESENT and immutable
- same-ID rerun allowed: false
- same-ID retune allowed: false
- same-ID rescue allowed: false

The marker was durably pushed before the historical evaluation was allowed to proceed. This is the intended exactly-once ordering and is not relaxed by the subsequent infrastructure failure.

## Verified execution failure

The historical workflow job configured `timeout-minutes: 350` and `cancel-in-progress: false`.

The job started at approximately `2026-08-14T13:51:43Z`. The frozen historical execution step began after successful setup and preflight and was cancelled at approximately `2026-08-14T19:41:47Z`, at the configured job timeout boundary. The terminal workflow conclusion was `cancelled`, and the execution step ended with `The operation was canceled.`

Therefore the direct failure mode is the configured GitHub Actions wall-clock timeout. It is not evidence of a Python exception, an estimator failure, a data-validation failure, a scientific rejection, or concurrency cancellation.

## Persisted artifact state

After termination, the result branch contained the durable attempt marker but no complete result bundle:

- `RUN_ATTEMPT.marker`: PRESENT
- `PRIMARY_RESULT.json`: ABSENT
- `EVIDENCE.json`: ABSENT
- `EXECUTION.json`: ABSENT
- `RUN_ONCE.marker`: ABSENT

Because the required three-file result bundle is absent, marker-only finalize recovery is not eligible. `RUN_ONCE.marker` must not be created for 0066.

No historical recomputation may be used to manufacture the missing bundle.

## Scientific interpretation

No 0066 scientific conclusion is valid.

In particular, this closeout must not be interpreted as evidence that:

- the event atlas lacks information;
- BTC or SOL path events cannot be warned in advance;
- any predictor architecture passes or fails;
- any of the eight controllers improves or harms the closed 0064 benchmark;
- CAGR, NAV, MDD, bootstrap inference, PBO, or event support has any particular historical value.

Those outputs were not durably produced by the unique attempt.

## Root-cause and process finding

The frozen program had a substantially larger physical compute graph than the high-level variant count suggested. Validation tuning alone contains `1632` configurations, each expanded through repeated walk-forward refits; prior implementation diagnostics showed that this implies on the order of tens of thousands of estimator fits before the remaining FINAL, controller, bootstrap, and PBO work.

The bounded artificial CI run validated interfaces, configuration enumeration, frozen counts, zero-result behavior, and basic executability. It did not qualify the wall-clock and memory envelope of the complete production-shaped computation.

The process defect is therefore an execution-qualification gap: the exactly-once marker was crossed without first proving that an equivalent full-shape, nonhistorical workload fits safely inside the selected runner budget.

Increasing a workflow timeout alone is not a scientific remedy and does not authorize a 0066 rerun.

## Mandatory rule for any successor research ID

Any successor program that carries forward this scientific question must use a new research ID and must treat the 0066 execution failure as process information only, not as scientific result information.

Before a new historical attempt marker may be crossed, the successor must include a pre-registered full-shape computational qualification gate using nonhistorical/synthetic inputs. The qualification must exercise the intended dimensional shape, track/configuration counts, refit geometry, inference workload, and execution environment while recording at least wall-clock time, peak memory, estimator-fit accounting, and deterministic thread/parallelism settings.

Semantic-preserving engineering optimizations may be developed before preregistration. Any change that can alter the statistical estimand, event labels, training sample, solver semantics, model family, hyperparameter search space, prediction timing, economics, inference, or randomization is a scientific change and must be declared and frozen under the successor lifecycle before historical execution.

## No-drift authority

- `production_authorized = false`
- `signature_authorized = false`
- `order_submission_authorized = false`
- Canonical BRRK-0011: NO CHANGE
- closed 0064: NO CHANGE
- closed 0065: NO CHANGE
- Phase 6: NO CHANGE

This closeout performs no historical content read, no model evaluation, no historical remeasurement, and no result-informed scientific tuning.
