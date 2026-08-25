# Prospective Five-Gate Research Lifecycle V1

Status: **PROSPECTIVE GOVERNANCE AMENDMENT / NEW RESEARCH IDS ONLY**

This amendment reduces GitHub merge plumbing while preserving the ten logical scientific-control checkpoints already used by the governed research program. It does not modify, reinterpret, reopen, rescue, rerun, or transfer lifecycle credit for any historical research ID.

## Objective

Future research should answer scientific questions faster without weakening preregistration, frozen science, point-in-time discipline, anti-lookahead rules, exactly-once execution, marker-before-read ordering, or immutable closeout.

The ten logical checkpoints remain mandatory:

1. OWNER-FIRST
2. DESIGN
3. PREREGISTRATION
4. IMPLEMENTATION
5. NONHISTORICAL QUALIFICATION
6. CONTROLLED BOUNDARY
7. ZERO-RESULT PREFLIGHT
8. UNIQUE CONTROLLED ATTEMPT
9. RESULT
10. IMMUTABLE CLOSEOUT

They are grouped into five merge gates:

| Merge gate | Required logical checkpoints | Authority |
| --- | --- | --- |
| `SPEC_FREEZE` | OWNER-FIRST, DESIGN, PREREGISTRATION | freezes question, data identities, candidate/trial budget, economics and success/failure gates before controlled results |
| `BUILD` | IMPLEMENTATION, NONHISTORICAL QUALIFICATION | implements only frozen science and proves synthetic/nonhistorical mechanics |
| `ARM` | CONTROLLED BOUNDARY, ZERO-RESULT PREFLIGHT | freezes controlled identities/budgets and proves zero-result readiness |
| `RUN` | UNIQUE CONTROLLED ATTEMPT | performs the sole irreversible controlled attempt through `CONTROLLED_RESEARCH_RUNNER_V1` |
| `SEAL` | RESULT, IMMUTABLE CLOSEOUT | interprets only persisted result evidence and seals terminal state |

## Internal ordering

Grouping checkpoints into one merge gate does not allow reordering them. Evidence inside each gate must prove the original logical order. In particular:

- PREREGISTRATION must be frozen before result-bearing implementation choices are made.
- NONHISTORICAL QUALIFICATION cannot read controlled scientific/history payload values.
- ZERO-RESULT PREFLIGHT must remain metadata/identity-only and must not decompress or traverse controlled payload entries.
- `RUN_ATTEMPT.marker` must be durably created before the first controlled payload read.
- the scientific engine may execute exactly once per authorized attempt.
- RESULT/closeout may not reread or recompute controlled science when persisted immutable result evidence is sufficient.

## Common runner requirement

Every future `RUN` gate that reads controlled scientific payload must use a currently qualified `CONTROLLED_RESEARCH_RUNNER_V1` or a prospectively approved successor. The runner must retain its synthetic qualification, including at least 20 consecutive full synthetic lifecycles with zero unexpected failure and the complete frozen fault matrix.

Any new `INVALID_EXECUTION` attributable to the common runner stops new scientific attempts until the runner is fixed and requalified. Governance must not respond by creating a replacement-ID chain that merely retries the same scientific question.

## Applicability

This amendment applies only to research IDs that:

1. are first registered after this amendment merges to `main`; and
2. explicitly declare adoption of `PROSPECTIVE_FIVE_GATE_LIFECYCLE_V1` in their owner-first/spec-freeze record.

All already-existing research IDs retain their historical lifecycle, attempt budget, read budget, result classification, closeout state, and ancestry. No stage or gate credit transfers from an old ID to a new ID.

## Dependency policy

Future research tracks may proceed independently when no scientific dependency exists. Artificial numeric-ID serialization is not a dependency. A child study must still wait for any parent evidence it explicitly consumes.

Examples:

- Trend research does not need to wait for Cross-sectional Factor research.
- Options/VRP atlas research does not need to wait for Trend.
- Factor L/S must wait for a qualifying Factor Atlas result if its design consumes validated factors.
- Multi-sleeve portfolio research must wait until its preregistered minimum set of economically distinct sleeves exists.

## Result discipline

`PASS`, `FAIL`, and `INCONCLUSIVE` are valid scientific outcomes. `INVALID_EXECUTION` is an infrastructure outcome and answers zero scientific questions.

The following remain forbidden:

- result-informed retuning or threshold rescue under the same frozen attempt;
- same-ID rerun after a consumed attempt;
- historical payload reads before the durable attempt marker;
- source substitution after preregistration without a new prospective hypothesis;
- classifying researcher-exposed DEVELOPMENT history as independent OOS;
- using governance compression to enlarge production, signing, order, withdrawal, or transfer authority.

## Production boundary

This amendment changes research merge structure only.

`production_authorized=false`

`signature_authorized=false`

`order_submission_authorized=false`

No production authority follows from a research PASS.
