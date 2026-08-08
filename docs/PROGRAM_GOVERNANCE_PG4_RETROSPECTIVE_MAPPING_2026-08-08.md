# Program-Level Epistemic Governance v1 — PG4 Retrospective Mapping

Date: 2026-08-08  
Roadmap task: `PG4`  
Mode: `RETROSPECTIVE_LEGACY`

## Scope

PG4 maps legacy research into `config/research_registry.json` using committed repository evidence only. It does not reconstruct uncommitted research history and does not pretend governance v1 existed when the legacy work was performed.

The mapping is intentionally conservative:

- committed IDs/statuses/contracts/results may be recorded as historical evidence;
- research-family/domain labels are retrospective taxonomy and therefore repository inference, not original historical declarations;
- typed lineage is recorded only when a committed contract explicitly identifies the dependency, predecessor, supersession or result-informed fork;
- uncommitted variants, views, researcher decisions and candidate universes remain `UNKNOWN` / `NOT_HISTORICALLY_RECORDED`;
- legacy dataset windows are not backfilled into the Dataset Exposure Registry unless a stable slice identity plus historical release/consumption semantics can be proved;
- the Edge Registry remains empty.

## Records mapped

The v1 Research Registry now contains 17 retrospective records covering the major frozen research history required for current governance:

1. `BRRK-0011`;
2. `PIT-ALPHA-0016-0018`;
3. `ASYM-BETA-0024`;
4. `TSMOM-ALPHA-0029`;
5. `FUNDING-PNL-0003`;
6. `CARRY-PNL-0031-CARRY-RF-0036`;
7. `EXPOSURE-SMOOTH-0038-CONTINUOUS-BETA`;
8. `LEVERAGE-0039`;
9. `LEVERAGE-0040`;
10. `LEVERAGE-0041`;
11. `P5.1-EVENT-TAXONOMY-V1`;
12. `P5.2-FEATURE-FAMILIES-V1`;
13. `P5.3-STATE-MODEL-STRUCTURE-V1`;
14. `P5.3-MARKET-STATE-PERMISSION-SEPARATION-V2`;
15. `P5.4-FIXED-STATE-GROSS-BEHAVIOR-V1`;
16. `P5.5-JOINT-PROFILE-MAP-VALIDATION-V1`;
17. `BEAR-SHORT-0001`.

This is a governance map, not a claim that these 17 records constitute every idea, local test or informal analysis ever performed.

## High-confidence lineage recovered

### Leverage line

`LEVERAGE-0039` is preserved as a pre-run stop with no economic result. Its contract states that the original architecture contradicted the intended separate leverage layer and that `LEVERAGE-0040` supersedes it. The registry therefore records:

```text
LEVERAGE-0040 --SUPERSEDES--> LEVERAGE-0039
```

`LEVERAGE-0041` explicitly states `follows: LEVERAGE-0040` and that the immutable 0040 result motivated the new implementation hypothesis/focal region. The registry therefore records both the information dependency and the genuine mechanism change:

```text
LEVERAGE-0041 --RESULT_INFORMED--> LEVERAGE-0040
LEVERAGE-0041 --MECHANISM_FORK--> LEVERAGE-0040
```

No parameter-only independence claim is made.

### P5 line

P5 contracts expose explicit upstream dependencies. The mapping records only relations directly supported by those contracts. In particular:

```text
P5.3 V1 --RESULT_INFORMED--> P5.2
P5.3 V2 --RESULT_INFORMED--> P5.3 V1
P5.3 V2 --MECHANISM_FORK--> P5.3 V1
P5.3 V2 --RESULT_INFORMED--> P5.2
P5.4 --RESULT_INFORMED--> P5.3 V2
P5.4 --RESULT_INFORMED--> P5.2
P5.5 --RESULT_INFORMED--> P5.3 V2
P5.5 --RESULT_INFORMED--> P5.4
P5.5 --RESULT_INFORMED--> P5.2
```

The V2 architecture contract explicitly preserves the V1 architecture failure rather than erasing it. P5.5 remains immutable `NO_PROMOTION / FAIL_STOP`.

## Negative and non-promoted results preserved

The retrospective registry keeps the existing dispositions rather than converting them into v1 successes:

- PIT, TSMOM, funding and carry lines remain rejected/stopped;
- `ASYM-BETA-0024` remains shadow-only;
- `EXPOSURE-SMOOTH-0038` remains mechanism evidence / shadow-only and is not substituted into BRRK;
- `LEVERAGE-0039` remains stopped before first run with no result;
- `LEVERAGE-0040` and `LEVERAGE-0041` remain immutable no-promotion research;
- P5.3 V1 architecture failure remains visible;
- P5.5 remains immutable no-promotion/fail-stop;
- `BEAR-SHORT-0001` remains trigger-absent/not-run.

PG4 performs no economic rerun, rescue, retuning or historical-result reinterpretation.

## Dataset Exposure Registry

PG4 intentionally leaves `config/dataset_exposure_registry.json` empty.

Legacy contracts do contain sources and windows, but a valid v1 dataset slice needs stable identity over source/version/assets/fields/resolution/start/end/transformation/PIT semantics plus release/consumption history. Backfilling a slice without the corresponding historical information-release facts could falsely convert researcher-exposed history into a pristine validation/sealed budget.

This missing history is therefore represented as Research Governance Debt instead of fabricated exposure events.

## Edge Registry

`config/edge_registry.json` remains:

```json
{"entries": []}
```

No BRRK feature, P5 feature family, leverage result or historical research line is retroactively declared a governance-v1 validated independent edge. Edge admission remains an evidence conclusion for future program-governed work.

## Research Governance Debt

PG4 formally records six open debt categories:

1. historical parameter/local trial counts unknown;
2. historical validation exposure/release history unknown;
3. dataset exposure identity/consumption incomplete;
4. experiment lineage incomplete beyond explicit repository evidence;
5. informal researcher decisions and discarded ideas unknown;
6. complete historical candidate/representation universe unknown.

These debts do not invalidate the immutable legacy results. They reduce the precision with which the program can estimate their historical epistemic independence and research-process degrees of freedom.

## Phase 6/7/8 authority remains separate

PG4 does not duplicate Phase 6/7/8 authority as research-registry records. Their canonical authority remains in the existing machine contracts. `BEAR-SHORT-0001` is mapped only because it is itself a preregistered research contract; its trigger/production authority remains unchanged.

## Expected program audit semantics

Because open historical governance debt is real, the correct PG4 audit state is expected to be:

```text
WARNING
```

and not `PASS` produced by hiding or inventing missing history. A future `PROGRAM_GOVERNED_V1` violation remains `ERROR/BLOCKING` and must fail closed.

## Production / strategy drift

```text
NO STRATEGY CHANGE
NO BNB CHANGE
NO PARAMETER CHANGE
NO COST CHANGE
NO PRODUCTION AUTHORITY CHANGE
NO HISTORICAL RESULT REINTERPRETATION
```

Exact next task: `PG5` add diff-aware fail-closed CI so any new formal research after the legacy boundary must be registered and complete before result-bearing code/evidence can merge.
