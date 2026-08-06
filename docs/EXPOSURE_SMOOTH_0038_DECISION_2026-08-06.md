# EXPOSURE-SMOOTH-0038 Governance Decision — 2026-08-06

Status: **MECHANISM VALIDATED / NOT PROMOTED / BASELINE UNCHANGED**

This document closes an authority-chain bookkeeping gap for an experiment that was preregistered, run and merged before the 2026-08-05 Master Plan / decision-registry program was established.

## Experiment

```text
EXPOSURE-SMOOTH-0038-CONTINUOUS-BETA
```

Preregistration:

```text
research/exposure_smooth_0038/EXPOSURE-SMOOTH-0038.json
```

Result:

```text
research/results/EXPOSURE_SMOOTH_0038_RESULT_2026-08-05.md
research/results/exposure_smooth_0038/summary.json
```

The experiment changed one structural mechanism in the historical V1 exposure function: the discontinuous two-branch BTC beta response was replaced with one continuous function using constants already present in the old implementation. It did not change the asset universe, alt-selection logic, transaction-cost convention, rebalance band or BRRK regime overlay.

## Evidence retained

Full-panel headline comparison reported by the frozen experiment:

| Metric | Frozen V1 | Smooth-beta 0038 |
| --- | ---: | ---: |
| CAGR | 36.38% | 34.13% |
| Max drawdown | -59.72% | -43.20% |
| Sharpe | 0.888 | 0.966 |
| Calmar | 0.609 | 0.790 |

The intended whipsaw mechanism improved materially in the 2021-05 stress window, while the experiment also documented real opportunity cost in strong one-way bull conditions such as 2023. Paired bootstrap uncertainty still included zero for the headline risk-adjusted differences.

## Canonical decision

```text
MECHANISM_VALIDATED_NOT_PROMOTED_BASELINE_UNCHANGED
```

Meaning:

- the structural defect diagnosis is preserved as valid research evidence;
- the experiment must not be forgotten or silently rerun as though the mechanism had never been tested;
- the 0038 function is **not** the canonical V1 exposure function;
- BRRK-0011 remains the canonical directional research target;
- P3.2 must reproduce the frozen BRRK-0011 / frozen V1 authority, not substitute 0038;
- no production or shadow integration is authorized by this bookkeeping decision;
- no same-window parameter retuning of 0038 is authorized.

Promotion would require a separate registered decision that explicitly rebuilds the dependent BRRK regime/risk chain and all affected comparison tables on the changed V1 return process. A future promotion study must preserve the already-observed 2023 opportunity cost and uncertainty rather than tune them away on the same sample.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

This is historical evidence normalization only.
