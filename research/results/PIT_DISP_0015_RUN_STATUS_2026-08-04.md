# PIT-DISP-0015-DYNAMIC-UNIVERSE — run status 2026-08-04

The survivorship-aware dynamic-universe dispersion experiment is fully preregistered and implemented, but **no model result exists yet**.

Registered rules remain frozen:
- historical ordinary Binance spot-USDT candidates, including later inactive/BREAK symbols while daily rows exist;
- at least 240 completed daily observations;
- completed-day quote volume >= $25m;
- minimum cross-section size 5;
- dispersion = sample standard deviation of 20-day cumulative log returns across the eligible point-in-time universe;
- risk overlay = expanding-prior-median/current dispersion clipped [0.10,1.00], recursively smoothed with lambda=0.80;
- entire frozen V1 exposure is scaled to cash; 0.05 band and 5bps cost;
- BRRK comparator remains frozen BRRK-0011.

Implementation file: `research/pit_universe/run_dynamic_dispersion.py`.

## Execution issue

The first pull-request-triggered GitHub Actions run created a job but failed before any step started. Three retries/re-runs, including one after aligning the workflow timeout from 60 minutes to the repository's normal 45 minutes, produced the same infrastructure-level signature: job conclusion `failure`, zero step records, and no job log/artifact blob. Therefore this is classified as a CI/runner-start failure, **not** an experiment failure and not a Python exception.

No data rule, universe criterion, signal formula, risk parameter or trading parameter was changed in response. The pull-request trigger was removed after the repeated startup failures to prevent every unrelated PR commit from spawning another failed check. Branch-path push and manual workflow-dispatch triggers remain available.

Do not quote or infer PIT-DISP-0015 performance until a run actually enters the Python step and produces `dynamic_dispersion_report.json`.
