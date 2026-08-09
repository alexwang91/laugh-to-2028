# Right-Tail Preservation Gate

**Production authorization: NO_CHANGE**

Status: `PROSPECTIVE_FROZEN_RESEARCH_ADMISSION_GATE`

This V1 gate is a prospective admission requirement for a **future new Research ID**. It is not a new experiment, a backtest, a Stablecoin rescue, a dual-layer rerun, a BRRK retune, or a retrospective score applied to immutable historical evidence.

## 1. Authority and frozen evidence

No result is recomputed in this document.

`BRRK-SIGNAL-ATTRIBUTION-AUDIT-V1` reports the canonical matched path:

| Metric | Immutable result |
|---|---:|
| canonical CAGR | 65.3056777227% |
| active-session win rate | 51.0752688172% |
| holding-cycle win rate | 54.4061302682% |
| daily payoff ratio | 1.1988078522 |
| canonical best-10 / total log growth | 51.5460339139% |
| canonical best-20 / total log growth | 91.6115239964% |
| canonical best-50 / total log growth | 180.3400637249% |
| CAGR if canonical best-20 sessions are zeroed | 4.3064145767% |
| CAGR if canonical best-50 sessions are zeroed | -33.2229136001% |

The immutable dual-layer sanity result records the frozen baseline/fused portfolio paths and remains non-promotable. The subsequent immutable BRRK attribution audit decomposes that already-frozen fusion path as:

| Fused minus canonical BRRK daily-return attribution | Immutable result |
|---|---:|
| sum delta on canonical-negative sessions | +1.1305444025 |
| sum delta on canonical-positive sessions | -1.3929560797 |
| net summed daily-return delta | -0.2624116772 |

The diagnostic therefore saved downside on canonical-negative sessions but clipped still more upside on canonical-positive sessions.

## 2. Scope

This gate applies to any future new component that can reduce canonical BRRK target gross on any date, including but not limited to:

- external state layer;
- structural overlay;
- cycle exit;
- risk overlay;
- volatility reducer;
- exposure scaler;
- crash filter;
- macro filter;
- defensive cap;
- regime veto.

A component does not escape this gate because its purpose is "risk reduction." If it can lower canonical target gross, it can clip the canonical right tail.

## 3. Mandatory reporting for every future candidate

### 3.1 Baseline right-tail retention

The candidate must report the percentage of canonical baseline log growth retained on each pre-defined canonical set:

- best-10 session log growth retained;
- best-20 session log growth retained;
- best-50 session log growth retained.

The **canonical BRRK baseline**, fixed before the candidate is evaluated, defines the best-N session date sets. A candidate may not re-rank dates, select its own best-N sessions, or redefine the right-tail set using candidate outcomes.

For a fixed canonical best-N set, report:

```text
retention_N =
sum(log(1 + candidate_return_t)) over canonical best-N dates
/
sum(log(1 + canonical_baseline_return_t)) over the same dates
```

Report the ratio as a percentage.

### 3.2 Positive / negative attribution

Report:

```text
sum(candidate_return - baseline_return) on canonical-positive sessions
sum(candidate_return - baseline_return) on canonical-negative sessions
net summed daily-return delta
```

The sign classification is defined by the canonical baseline return, not by candidate return.

### 3.3 Best-20 intervention list

For every date in the canonical best-20 set on which the candidate lowered exposure, list at least:

- date;
- canonical baseline return;
- canonical baseline gross;
- candidate gross;
- candidate-minus-baseline return delta.

No intervention in the canonical best-20 may be hidden inside aggregate metrics.

## 4. Frozen V1 hard numerical gates

### Gate 1 — Right-tail retention

```text
candidate retained canonical best-20 log growth >= 90%
```

### Gate 2 — Net economic contribution

```text
net summed daily-return delta > 0
```

The second inequality is strict. `0` does not pass.

A future candidate must:

```text
PASS Gate 1
AND
PASS Gate 2
```

before it may enter any higher-level economic or integration review.

Failure of either gate yields:

```text
FAIL_RIGHT_TAIL_GATE
```

Failure does not authorize threshold tuning, a different cap search, rescue variants, post-result parameter search, or a discretionary override based on headline CAGR.

## 5. Why V1 freezes 90%

The immutable canonical attribution shows that the best 20 baseline sessions contribute approximately **91.6% of total canonical log growth**. BRRK is therefore right-tail-dependent rather than a high-win-rate strategy.

V1 freezes 90% because:

- 100% retention would leave almost no room for a genuinely useful downside overlay to intervene;
- a materially lower threshold would permit one candidate to remove too much of the core economic engine before higher-level review;
- 90% is a conservative admission threshold frozen while no new overlay candidate is being designed, fitted, evaluated, or selected;
- the threshold is not inferred from any new candidate outcome.

Best-10 and best-50 retention remain mandatory reporting metrics, but V1 adds no separate numerical threshold for them. This avoids adding free parameters without a prospective need.

Gate 2 is independently necessary because preserving the right tail is insufficient if the candidate's total intervention is economically negative. The candidate must save more return on canonical-negative sessions than it clips elsewhere, so net summed daily-return delta must be strictly positive.

## 6. Freeze declaration

This threshold was frozen prospectively while no new overlay
candidate was being designed, fitted, evaluated, or selected.
It must not be changed after observing a future candidate merely
to rescue that candidate.

A future change to the 90% threshold requires:

1. a new governance version;
2. publication before the affected new candidate begins;
3. an independent rationale not derived from that candidate's observed result;
4. preservation of V1 as historical governance rather than overwriting it.

## 7. Historical exclusion

V1 does **not** retrospectively rescore, reopen, rerun, rescue, retune, reinterpret for promotion, or alter:

- P5.x terminal evidence;
- `LEVERAGE-0040`;
- `LEVERAGE-0041`;
- `STABLECOIN-LIQUIDITY-0001`;
- `DUAL-LAYER-FUSION-ARCH-SANITY-V1`;
- `BRRK-SIGNAL-ATTRIBUTION-AUDIT-V1`;
- any other immutable / terminal / `NO_PROMOTION` / `FAIL_STOP` evidence.

Those historical results retain their original status and authority.
