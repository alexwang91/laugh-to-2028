# Source Inventory

Source: `alexwang91/market`, branch `chatgpt/crypto-rotation-backtest-20260804`, Draft PR #2.

This file records how the old mixed-repository research tree maps into the canonical `laugh-to-2028` repository.

## 1. Canonical/current code migrated

These components remain useful for reproducing or continuing the current research line and therefore exist as runnable/current code in this repository:

- `research/core/crypto_rotation_backtest.py`
- `research/crypto_rotation_backtest.py` compatibility entry point
- `research/regime_kelly/config.py`
- `research/regime_kelly/features.py`
- `research/regime_kelly/features_no_dominance.py`
- `research/regime_kelly/regime_model.py`
- `research/regime_kelly/regime_model_vb_nd.py`
- `research/regime_kelly/daily_distribution.py`
- `research/regime_kelly/experiment_registry.json`
- `research/hybrid_meta/walkforward_v1_meta.py`
- `research/risk_metric_fix/corrected_risk.py`
- `research/dispersion_overlay/run_dispersion_overlay.py`
- `research/pit_universe/run_archive_discovery.py`
- `research/pit_universe/run_dynamic_dispersion.py`
- `research/pit_universe/PIT-DISP-0015-DYNAMIC-UNIVERSE.json`
- `research/RESEARCH_ROADMAP_AFTER_0015.md`
- `research/literature/LITERATURE_2026-08-04.md`
- `execution/plan-b-bot/**`
- `.github/workflows/project-smoke.yml`
- `.github/workflows/pit-disp-0015.yml`

## 2. Formal result/evidence records migrated

All formal Markdown result records from the source PR research-results set are retained in `research/results/`, including:

- `AUDIT_0010_TAIL_CALIBRATION_2026-08-04.md`
- `AUDIT_0012_PIT_CALIBRATION_2026-08-04.md`
- `AUDIT_0013_ACTIVATION_ATTRIBUTION_2026-08-04.md`
- `BRRK_0004_0005_2026-08-04.md`
- `BRRK_0006_2026-08-04.md`
- `BRRK_0007_AND_CYCLE_0002_2026-08-04.md`
- `BRRK_0008_2026-08-04.md`
- `BRRK_0009_2026-08-04.md`
- `BRRK_0011_CDAR_CORRECTION_2026-08-04.md`
- `DERIV_AUDIT_0001_FUNDING_PREMIUM_2026-08-04.md`
- `DISP_0013_ALT_RELIABILITY_2026-08-04.md`
- `DISP_0014_MEDIAN_RATIO_REPLICATION_2026-08-04.md`
- `EXEC_AUDIT_0001_BOOK_DEPTH_2026-08-04.md`
- `PIT_DISP_0015_RUN_STATUS_2026-08-04.md`
- `PIT_UNIVERSE_0001_DISCOVERY_2026-08-04.md`
- `PIT_UNIVERSE_0002_LIFECYCLE_2026-08-04.md`
- `PIT_UNIVERSE_0003_DATA_ACCESS_2026-08-04.md`
- `ROBUSTNESS_AND_CYCLE_2026-08-04.md`

The numerical conclusions from the early rotation/ablation/robustness work that predated this formal result set are consolidated in `docs/RESEARCH_HISTORY.md` and the root README.

## 3. Source-PR exploratory implementations deliberately not placed in the canonical runtime path

The source PR also contains intermediate/rejected implementations whose *research information is preserved* but whose code is not presented as current strategy code. These include the old implementation trees around:

- `research/audit_0006/`
- `research/automation/`
- `research/calibration/` implementation scripts
- `research/crypto_cycle_sequence_v2.py`
- `research/crypto_cycle_state_machine.py`
- older `research/crypto_rotation_*` experimental variants
- `research/cycle_reentry/`
- `research/derivatives_risk/` collectors
- `research/execution_risk/` collectors
- `research/label_free/`
- superseded `research/regime_kelly/current_snapshot*`, optimizer and older walk-forward variants
- `research/riskoff_gate/`
- `research/state_ensemble/`
- `research/state_identity/`
- old source-branch-specific GitHub Actions workflows

Why they are not canonical here:

1. several were explicitly rejected by preregistered tests;
2. several were one-off audit/collector scripts rather than a strategy dependency;
3. copying them into the live import path would make obsolete specifications look supported;
4. their experiment definitions, results, failure reasons and decisions are preserved in the formal result records, experiment registry, roadmap and research history.

The original PR #2 remains the immutable code-level archive for those obsolete implementation details.

## 4. Explicitly excluded as unrelated or unsafe

Not migrated:

- any `alexwang91/market` code outside this crypto research PR/branch;
- unrelated business/market applications;
- generated caches and logs;
- private keys, account secrets, deployment secrets or wallet credentials;
- fabricated PIT-DISP-0015 or funding-backtest outputs that never produced a valid run.

## 5. Canonical reading order

1. `README.md`
2. `docs/RESEARCH_HISTORY.md`
3. `research/results/BRRK_0011_CDAR_CORRECTION_2026-08-04.md`
4. `research/results/DISP_0014_MEDIAN_RATIO_REPLICATION_2026-08-04.md`
5. `research/results/PIT_UNIVERSE_0001_DISCOVERY_2026-08-04.md`
6. `research/results/PIT_UNIVERSE_0002_LIFECYCLE_2026-08-04.md`
7. `research/results/PIT_UNIVERSE_0003_DATA_ACCESS_2026-08-04.md`
8. `research/pit_universe/PIT-DISP-0015-DYNAMIC-UNIVERSE.json`
9. `docs/NEXT_STEPS.md`
