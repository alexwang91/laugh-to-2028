# BRRK Next Steps

Last updated: 2026-08-07

## Current instruction

**LEVERAGE-0041 preregistration is merged. Proceed continuously through implementation, pre-run validation and the already-authorized one-time research run. Do not stop for another RUN_ONCE permission prompt. P4.6 remains a separate production decision.**

## Immediate state

```text
implementation base main               baaa5776892411990734ef2121cf54a5dbbab047
PR #90                                 MERGED
PR #93                                 MERGED
LEVERAGE-0040                          COMPLETE / IMMUTABLE / NO_PROMOTION
LEVERAGE-0041                          PREREGISTERED / IMPLEMENTATION PRE-RESULT
RUN_ONCE research authority            AUTHORIZED
selected research cap                  NONE YET
selected operating DD budget           NONE YET
P4.6 production authorization          BLOCKED / SEPARATE
production gross cap                   1.0
production_authorized_components       []
```

## Frozen LEVERAGE-0041 objective

Maximize matched after-cost long-run compounded wealth / CAGR among candidates satisfying every survival, tail-risk, liquidation, funding, cost, execution and robustness hard gate.

Candidate grid:

`1.00 / 1.05 / 1.10 / 1.15 / 1.20 / 1.25 / 1.30`

`1.20` is the focal region only, not a preselected result.

## Required implementation before candidate economics

1. freeze `LEVERAGE-0041-STUDY-IMPLEMENTATION-V1`;
2. prove cap=1 requested-target exact parity against frozen raw BRRK-0011;
3. implement 25% reserve / <=75% spot financing route accounting;
4. implement BTC/ETH/SOL spot-first, BNB perp-only, residual/incremental perp routing;
5. implement monotone 168h funding reducer at 5/10 bps/day;
6. map liquidation to actual routed perp notional against exactly 25% reserve and require >55%;
7. pin route-capacity evidence, funding evidence, margin snapshot and input hashes;
8. freeze immutable result schema/validator;
9. run fresh contract tests and blinded `--preflight-only`.

If those gates are green, commit the already-frozen RUN_ONCE marker and execute immediately under the standing owner authorization.

## One-time integrity rule

The RUN_ONCE marker is a technical single-execution control. It is not an additional approval request.

After first candidate computation begins:

- no candidate grid change;
- no reserve/spot-budget change;
- no funding threshold/lookback change;
- no stress/liquidation threshold change;
- no seed/robustness change;
- no selection-rule change;
- no route-architecture change.

A non-economic implementation defect may be corrected only through an explicit recovery record; result-driven retuning is forbidden.

## Selection and downstream

A cap is selectable only if it is interior to at least three contiguous all-PASS caps with immediate lower and higher neighbors passing. Within a qualifying region choose the highest CAGR, with the lower cap preferred for <=1pp annualized CAGR near-ties.

If no cap qualifies: `NO_PROMOTION`, keep production gross 1.0.

If a research cap qualifies: record `RESEARCH_PROMOTION_CANDIDATE_NOT_PRODUCTION_AUTHORIZED`; the prospective P4.6 cap is the next lower grid point capped at 1.20.

**Never cross P4.6 automatically.** Production leverage requires a separate explicit authorization after research evidence.
