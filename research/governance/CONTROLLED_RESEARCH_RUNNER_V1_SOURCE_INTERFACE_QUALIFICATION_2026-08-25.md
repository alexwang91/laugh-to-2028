# CONTROLLED_RESEARCH_RUNNER_V1 source-interface qualification

Date: 2026-08-25

Status: prospective infrastructure qualification. It changes no historical scientific result and authorizes no controlled attempt.

## Incident motivating this qualification

0085 consumed its single authorized attempt after the durable marker, 201 controlled reads, and one engine invocation. The runner supplied source keys beginning `payloads/`; the 0085 engine expected `stage/payloads/`. The runner's original preflight checked only whether `execute()` existed, so it could not detect that incompatibility before consuming the attempt.

0085 remains immutable `INVALID_EXECUTION`. This qualification does not repair, rerun, rescue, recompute, reinterpret, or replace 0085.

## Prospective contract

Future controlled engines using the strengthened V1 path must implement:

```python
validate_source_keys(source_keys: Sequence[str]) -> None
```

The runner calls it during metadata-only preflight with exactly the frozen manifest filenames that will later become `EngineContext.sources` keys. The validator may inspect only those strings. It must return `None` on compatibility and raise on incompatibility.

The strengthened preflight rejects before marker creation when:

- the validator is missing;
- the adapter rejects the runtime source-key namespace;
- the validator returns a non-`None` value.

A rejection consumes zero attempt budget, performs zero controlled reads, and invokes the scientific engine zero times.

## 0085 regression fixture

The synthetic regression uses the exact source-key shape that failed in 0085:

`payloads/data__futures__um__monthly__klines__BTCUSDT__1d__BTCUSDT-1d-2021-01.zip`

A synthetic adapter requiring `stage/payloads/` must fail before marker. A synthetic adapter requiring `payloads/` must complete the full lifecycle.

## Qualification requirements

The full prospective qualification requires:

1. all original `CONTROLLED_RESEARCH_RUNNER_V1` fault-matrix tests remain green;
2. the 0085 namespace regression fails closed before marker with zero reads and zero engine invocations;
3. missing `validate_source_keys` fails closed before marker;
4. the exact runtime `payloads/` namespace completes a synthetic full lifecycle;
5. 20 consecutive source-qualified synthetic full lifecycles complete with zero unexpected failure;
6. no test opens, decompresses, hashes, or CRC-scans controlled payload bytes before marker;
7. no network, production, signing, order, withdrawal, or transfer authority is added.

## Science pause

Trend, Factor, and Options controlled attempts remain paused until this prospective qualification is merged with terminal-green exact-head mandatory CI. Passing this qualification repairs infrastructure only. It does not itself authorize a new controlled scientific attempt.

## What did not change

- 0085 attempt 1/1 remains permanently consumed and sealed `INVALID_EXECUTION`.
- 0070/0071/0083/0072/0073/0074/0075/0084 remain immutable.
- 0076 remains sealed at its Stage7 pre-marker incident with no replacement.
- `workflow run                         31381953131 / attempt 1` remains protected.
- CAPTURE-0001 remains sealed/no-retry.
- CAPTURE-0002 remains permanently claimed/no-refetch.
- Phase6 closeout remains unchanged.
- No production/signature/order/withdrawal/transfer authority is granted.
