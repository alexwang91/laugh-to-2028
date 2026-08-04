# AUDIT-0013-ACTIVATION-ATTRIBUTION — 2026-08-04

No trading changes. This audit attributes the realized performance difference between BRRK-0011 and BRRK-0011 + the frozen primary DISP-0013 90th-percentile alt-to-BTC overlay after the actual 0.05 rebalance band.

## Result

- actual post-band held-weight difference days: 29 / 1332 (~2.18%);
- contiguous held-difference episodes: 4;
- total additive net-return difference over changed days: +5.178 percentage points;
- total turnover difference: -3.609 (overlay lower).

Contribution concentration:
- largest episode: +2.209pp, ~43.7% of all positive episode contribution;
- top three episodes: +4.911pp, ~97.1% of all positive episode contribution.

## Episodes

| Episode | Days | Base return | Overlay return | Difference | Max L1 held diff | Mean alt change | Max lagged dispersion percentile | Min gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023-12-26 to 2024-01-13 | 19 | -11.379% | -11.245% | +0.134pp | 0.0669 | -0.18pp | 90.67% | 0.933 |
| 2024-11-18 to 2024-11-25 | 8 | +1.038% | +2.229% | +1.191pp | 0.6891 | -19.22pp | 96.89% | 0.311 |
| 2024-12-02 | 1 | -3.081% | -1.482% | +1.599pp | 0.9420 | -47.10pp | 99.42% | 0.058 |
| 2024-12-04 | 1 | +0.359% | +2.567% | +2.209pp | 0.8842 | -44.21pp | 98.84% | 0.116 |

The economically meaningful improvement is therefore highly concentrated in late November / early December 2024. The first episode contributes very little and contains many essentially identical held positions after banding.

Largest positive daily deltas were 2024-12-04 (+2.209pp), 2024-12-02 (+1.599pp), and 2024-11-25 (+0.740pp). The largest adverse day was 2024-11-21 (-0.492pp).

## Interpretation

The attribution materially lowers the evidence grade of DISP-0013. The rule remains mechanistically plausible and its preregistered 80/90/95 family all improved headline metrics, but the primary rule's realized alpha increment is not diversified across many independent episodes. Most of the benefit is tied to one late-2024 high-dispersion cluster.

This audit therefore does **not** justify production promotion or selecting the 80% sensitivity. The next decisive test is a point-in-time universe / survivorship-aware reconstruction. DISP-0013 remains a shadow candidate only.
