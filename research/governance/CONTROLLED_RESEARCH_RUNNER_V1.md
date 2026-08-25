# CONTROLLED_RESEARCH_RUNNER_V1

Status: prospective public execution infrastructure. This contract grants no scientific attempt, lifecycle, production, signing, order, withdrawal or transfer authority.

## Ordering contract

Every future controlled execution that adopts this runner must preserve this order:

1. validate exact expected git head, manifest schema/source identity, timestamp, create-only object absence, archive filenames and central-directory declared sizes;
2. durably create `RUN_ATTEMPT.marker` with create-only semantics;
3. only after the marker exists, open/decompress controlled payload entries and perform payload CRC/hash verification;
4. invoke the scientific engine exactly once;
5. persist exactly one create-only result envelope;
6. durably create `RUN_ONCE.marker` to seal the terminal attempt.

Before `RUN_ATTEMPT.marker`, the runner must never call `ZipFile.testzip()`, `ZipFile.read()`, `ZipFile.open()`, extraction/decompression code, payload CRC scans or any equivalent payload-reading path. Pre-marker inspection is restricted to source/archive identity, filenames, central-directory metadata and hashes/sizes declared by the frozen manifest.

## Failure semantics

A preflight rejection consumes no attempt and must perform zero controlled payload reads and zero engine invocations. Once `RUN_ATTEMPT.marker` exists, any corrupt payload, hash mismatch, runtime crash, duplicate read, double engine invocation, non-finite result, network attempt or persistence failure is execution failure rather than scientific evidence. The runner may persist a create-only invalid-execution envelope and `RUN_ONCE.marker` where the persistence backend remains available. Writer failure itself still consumes the marked attempt and never admits a scientific result.

An `INVALID_EXECUTION` from this common runner is a runner/infrastructure stop signal. Future science must stop until the common runner defect is fixed and re-qualified. It must not create a chain of result-informed replacement IDs.

## Exactly-once and evidence identity

The runner binds every marker/result to research ID, attempt ID, exact expected head, source/manifest identity and decision timestamp. Existing result/marker/RUN_ONCE objects fail closed. Source payloads receive one physical verified read pass. The engine invocation guard allows one invocation. Result and seal objects use create-only storage.

## Network boundary

The scientific engine runs under a deny-network guard for common Python socket/HTTP/urllib paths. A network attempt becomes `INVALID_EXECUTION_NETWORK_ATTEMPT` and cannot produce admissible science.

## Qualification matrix

The mandatory synthetic matrix covers all of the following before any new scientific attempt may use this runner:

- corrupted ZIP / CRC;
- missing file;
- wrong hash;
- duplicate object;
- stale head;
- existing result;
- marker push failure;
- crash after marker;
- duplicate read;
- double engine invocation;
- NaN/non-finite result;
- missing timestamp;
- schema drift;
- writer failure;
- network attempt;
- wrong source manifest;
- wrong execution interface.

In addition, qualification requires at least 20 consecutive synthetic full lifecycles with zero unexpected failure, and every successful lifecycle must show marker created, exact source-read count, exactly one engine invocation, create-only result, and RUN_ONCE seal.

## Scope boundary

This runner does not compress or amend the historical ten-stage lifecycle. Any future five-gate merge model (`SPEC FREEZE / BUILD / ARM / RUN / SEAL`) requires a separate prospective governance amendment after this runner passes qualification. Historical IDs remain governed by their immutable contracts and outcomes.
