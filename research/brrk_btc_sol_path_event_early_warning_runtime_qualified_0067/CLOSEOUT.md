# BRRK-BTC-SOL-PATH-EVENT-EARLY-WARNING-RUNTIME-QUALIFIED-0067 — IMMUTABLE CLOSEOUT

Status: `INVALID_EXECUTION / CLOSED TO SAME-ID RERUN`

Date: 2026-08-15

## Terminal classification

0067 is closed as an execution-integrity invalidation, not as a scientific PASS or FAIL.

The unique authorized historical execution completed its workflow lifecycle and durably persisted the complete five-artifact run bundle, but the post-execution physical-compute accounting did not match the frozen controlled boundary. Therefore no 0067 inference about event predictability, classifier quality, controller economics, CAGR, terminal wealth, drawdown, robustness, or promotion is admissible.

## Exactly-once accounting

- research ID: `BRRK-BTC-SOL-PATH-EVENT-EARLY-WARNING-RUNTIME-QUALIFIED-0067`
- authorized historical attempt: `1 / 1 CONSUMED`
- controlled-boundary merge SHA: `d5c7938f0e0bb62368c0b6ce5330088c0fda817c`
- historical workflow run: `31882271904`
- historical workflow job: `95006404891`
- immutable result branch head after final persistence: `85c9f4124c308f7fb283c3f015a60e282f2792d5`
- `RUN_ATTEMPT.marker`: PRESENT
- `PRIMARY_RESULT.json`: PRESENT
- `EVIDENCE.json`: PRESENT
- `EXECUTION.json`: PRESENT
- `RUN_ONCE.marker`: PRESENT
- same-ID rerun allowed: false
- same-ID retune allowed: false
- same-ID rescue allowed: false

The durable attempt marker was persisted before any historical content read. The workflow then performed the frozen historical evaluation exactly once and completed marker-only finalization without historical reread.

## Verified historical I/O and call accounting

The persisted execution record reports:

- market evidence reads = 1;
- BRRK equity reads = 1;
- BRRK weights reads = 1;
- DTB3 reads = 1;
- market loader calls = 1;
- top-level scientific engine calls = 1;
- network fetches = 0.

The final marker reports:

- historical content reads during finalize = 0;
- market loader calls during finalize = 0;
- scientific engine calls during finalize = 0.

The workflow's final immutable-execution verification step completed successfully, including the persisted artifact/hash-chain and zero-authority checks.

## Physical-compute accounting failure

The controlled boundary required the historical execution to match the qualified physical compute graph:

| Quantity | Frozen required | Historical actual | Status |
| --- | ---: | ---: | --- |
| Validation estimator fit calls | 31,008 | 31,008 | MATCH |
| Economic estimator fit calls | 11,904 | 5,808 | MISMATCH |
| Total estimator fit calls | 42,912 | 36,816 | MISMATCH |
| P08 stacking NNLS solves | 40 | 20 | MISMATCH |
| Process workers | 4 | 4 | MATCH |

Because the economic fit graph, total fit graph, and NNLS accounting were incomplete relative to the prospectively frozen boundary, the runner correctly persisted `classification = INVALID_EXECUTION`.

This accounting mismatch is an execution-integrity failure. It must not be reinterpreted as a negative scientific finding, and the partially computed predictive/controller outputs must not be promoted as confirmatory evidence.

## Scientific interpretation

No admissible 0067 scientific PASS/FAIL exists.

In particular, this closeout does not establish that:

- the event atlas contains or lacks predictive information;
- any warning horizon or predictor architecture succeeds or fails;
- any predictive winner is confirmatory;
- any of the eight controllers improves or harms the closed 0064 benchmark;
- CAGR, NAV, MDD, bootstrap inference, PBO, or event support has a valid 0067 historical value.

Any values computed before the accounting invalidation are diagnostic execution traces only and are not scientific evidence under the frozen lifecycle.

## Relationship to full-shape qualification

The nonhistorical qualification workflow `31867786428` passed the prospectively frozen full shape on the exact merged implementation: 31,008 validation fits, 11,904 economic fits, 42,912 total fits, 40 NNLS solves, four workers, 4000+4000 bootstrap replicates, and 70 PBO splits.

The historical run's lower economic and NNLS counts therefore expose a historical execution-path/accounting divergence that was caught by the controlled runner. Exactly-once governance forbids using this observation to patch and rerun 0067 under the same ID.

## Mandatory rule for any successor research ID

Any further measurement of this scientific question must use a new research ID with a new preregistration, implementation/boundary lifecycle, nonhistorical full-shape qualification, and a new prospectively authorized attempt budget.

The 0067 mismatch may be used as process information for engineering diagnosis. It may not be used to tune scientific event definitions, features, architectures, model grids, selection rules, controller rules, economics, inference, or classification gates.

## No-drift authority

- `production_authorized = false`
- `signature_authorized = false`
- `order_submission_authorized = false`
- Canonical BRRK-0011: NO CHANGE
- closed 0064: NO CHANGE
- closed 0065: NO CHANGE
- closed 0066: NO CHANGE
- Phase 6: NO CHANGE

This closeout performs no historical content read, no model evaluation, no historical remeasurement, no retuning, no rescue, and no recomputation.