# BRRK-WINNER-ROBUSTNESS-0002

Lifecycle: **ONE-SHOT ROBUSTNESS PASS / FUTURE-ONLY VALIDATION STAGE ELIGIBLE**  
Formal preregistration state: **PREREGISTERED_NOT_RUN** *(immutable pre-result evidence)*  
Pull request: **#153**  
Merged preregistration: **PR #152 / `11c7967e4d22766b3abee33d382ab2912c16f5cb`**  
Successful run: **GitHub Actions `31374176442`, attempt 1**

This research ID executed exactly once from trigger SHA `346e26e3906df2416a21a40223e8791c3dfef86a` after pre-result green baseline `561ecee69d30253aa398caf51d589cb03b5cfe47`. The exact frozen 40% BTC / 60% sole-eligible-alt construction passed the preregistered robustness panel. No new allocation split is searched under this research ID, and the ID is now closed against rerun or rescue tuning.

## Evidence binding

The 5 bps canonical and candidate metric payloads and both target-frame hashes reproduced before any robustness metric was released. The immutable Actions artifact is bound by:

```text
workflow run                       31374176442 / attempt 1
artifact id                        9057294415
artifact digest                    sha256:8eb08d0080fae185953ae50a15b05bc9994d6c06da33761bd2125dc89037313c
PRIMARY_RESULT exact-byte SHA256   cf149308df5aea1a0cc1315432a7effd0e163cda21e6df0b8f39cf0b6ce6fdf0
```

`PRIMARY_RESULT.json` preserves the exact artifact result bytes. `EXECUTION.json` binds the result, artifact provenance, pre-result baseline, trigger SHA and one-shot execution count.

## Frozen 5 bps primary reproduction

```text
canonical CAGR                     65.3057%
candidate CAGR                     69.6917%
canonical max drawdown             -33.5292%
candidate max drawdown             -33.4499%
canonical Calmar                   1.9477
candidate Calmar                   2.0835
right-tail log-growth capture      103.5595%
turnover ratio                     1.1229x
```

## Temporal robustness at 5 bps

The panel used one continuous full-horizon P3.3 path and sliced realized returns without boundary position resets or artificial rebalances.

```text
T1  2022-12-10 .. 2024-02-26
    canonical CAGR 213.3798%   candidate 235.9630%   delta +22.5832 pp   PASS
    MDD            -25.0922%             -26.8381%   deterioration 1.7459 pp

T2  2024-02-27 .. 2025-05-15
    canonical CAGR  36.4848%   candidate  34.7482%   delta  -1.7365 pp   NEGATIVE EVIDENCE
    MDD            -33.5292%             -33.4499%   no deterioration

T3  2025-05-16 .. 2026-08-02
    canonical CAGR   5.6108%   candidate   7.9363%   delta  +2.3255 pp   PASS
    MDD            -32.1255%             -32.1255%   effectively unchanged
```

The preregistered temporal gate required candidate CAGR not below canonical in at least two of three blocks. It passed exactly 2/3. T2 remains committed negative evidence and may not be removed, redefined or used to justify same-ID retuning.

## Transaction-cost robustness

Only `cost_bps` changed; the full target paths and canonical P3.3 5% L1 band remained fixed.

```text
10 bps
canonical CAGR      63.2574%   candidate 67.3311%   delta +4.0737 pp
canonical Calmar     1.8583    candidate  1.9805
canonical MDD      -34.0405%   candidate -33.9963%

20 bps
canonical CAGR      59.2440%   candidate 62.7142%   delta +3.4702 pp
canonical Calmar     1.6910    candidate  1.7888
canonical MDD      -35.0351%   candidate -35.0594%
MDD deterioration at 20 bps: 0.0244 pp
```

All fixed cost-stress CAGR, Calmar and drawdown gates passed.

## Evidence status and authority

The study reuses `BRRK-WINNER-0001-CANONICAL-HIST-V1`, which is already consumed and researcher-exposed DEVELOPMENT history. This is result-informed historical robustness evidence, not independent OOS evidence and not temporal novelty.

The result is `PASS_FUTURE_ONLY_VALIDATION_STAGE_ELIGIBLE`. That means only a new, separately preregistered future-only validation stage is eligible. This PASS makes a future-only validation stage eligible; it does not authorize canonical or production promotion. It does **not** modify canonical `BRRK-0011`, Phase 6 scheduled-decision credit, Phase 7, leverage, shorts, execution authority, signing, order submission or production authorization.

```text
production_authorized      false
signature_authorized       false
order_submission_authorized false
canonical_brrk_changed     false
phase6_observation_changed false
```

`RUN_ONCE.marker` is retained permanently. BRRK-WINNER-ROBUSTNESS-0002 may not run again. Any future validation must use a new research ID and a new preregistration created before future-only observations are released.
