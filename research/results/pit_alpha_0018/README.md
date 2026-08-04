# PIT-ALPHA-0018 exact evidence

This directory is populated by the validated GitHub Actions run for `PIT-ALPHA-0018-ENTRY-RANK-ELIGIBILITY-EXIT`.

Expected files:

- `pit_alpha_0018_report.json` — machine-readable full result;
- `daily_equity.csv` — exact daily NAV for 0018, 0016 and benchmarks;
- `daily_held_weights_long.csv` — exact held weights;
- `daily_selected_names.csv` — state-machine selected incumbents;
- `daily_turnover_decomposition.csv` — BTC, sleeve-size and name-switch turnover;
- `holding_spells.csv` — holding-duration and spell contribution evidence;
- `asset_contribution.csv` — asset-level gross arithmetic contribution;
- `placebo_metrics.csv` — 100 fixed-random-priority state-machine placebos;
- `state_machine_events.csv` — entry, exit and risk-regime events;
- `pnl_daily.svg` — exact daily NAV chart;
- `pit_alpha_0018.log` — complete workflow output.

Formal interpretation: [`../PIT_ALPHA_0018_RESULT_2026-08-04.md`](../PIT_ALPHA_0018_RESULT_2026-08-04.md).
