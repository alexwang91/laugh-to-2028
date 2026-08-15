# 0068 IMPLEMENTATION-ONLY contract

Research ID: `BRRK-BTC-SOL-PATH-EVENT-EXECUTION-EQUIVALENCE-0068`.

This stage implements only the execution-assurance contract frozen in merged preregistration `60746a7d96c7b55df5384c4e9f54e3d7fd4b833f`. Historical measurement remains forbidden and the historical attempt budget remains zero.

## Canonical graph law

`execution_graph.build_downstream_manifest` is the only graph-builder entry point. Qualification and controlled-mode dry run must call it with the same eligibility inputs and must obtain byte-identical canonical manifest bytes and SHA256.

The candidate downstream geometry remains explicit even when work is ineligible. An excluded candidate receives zero expected physical actions and an `ELIGIBILITY_EXCLUDED` terminal trace. This preserves a complete audit trail while allowing the frozen validation/base-prediction eligibility law to contract physical work.

Full-support geometry contains 240 P01-P06 asset/target/horizon/architecture candidates plus 8 pooled P07 asset/target candidates, each across 48 economic refit blocks, for 11,904 expected estimator fits. P08 has 40 asset/target/horizon candidate locations and therefore 40 expected NNLS solves under full support.

Validation remains structurally 31,008 estimator fits and is not modified by this implementation.

## Physical accounting

Every manifest unit includes `expected_fit_calls` and `expected_nnls_solves`. Consumption produces exactly one terminal trace per unit, bound to the manifest SHA256. Qualification fails on duplicate unit IDs, duplicate/missing terminal traces, fit-count mismatch, NNLS-count mismatch, historical reads, network fetches, or qualification/controlled-mode manifest divergence.

## Synthetic regimes

The implementation exercises all preregistered regimes: `FULL_SUPPORT`, `PARTIAL_SUPPORT`, `SINGLE_CLASS_UNDEFINED_TRACKS`, `MISSING_BASE_PREDICTIONS`, and `MIXED_P07_P08_ELIGIBILITY`. The fixtures alter eligibility only. They do not alter event definitions, features, architectures, grids, validation selection semantics, horizons, controllers/economics, bootstrap/PBO definitions, or scientific classification gates.

## Authority

`historical_execution_authorized=false`; `production_authorized=false`; `signature_authorized=false`; `order_submission_authorized=false`.
