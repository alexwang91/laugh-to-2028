# Migration Manifest

Migration date: 2026-08-04

Source research repository: `alexwang91/market`

Source research branch: `chatgpt/crypto-rotation-backtest-20260804`

Source draft PR: `alexwang91/market#2`

Target canonical repository: `alexwang91/laugh-to-2028`

## Scope rule

Only the crypto systematic-allocation project is in scope. Unrelated market/business/application code from `market` is deliberately excluded.

The target repository is organized by function rather than mirroring the old mixed repository byte-for-byte.

## Migrated as canonical/current code

- frozen V1 rotation backtest core;
- BRRK feature/state/scenario dependencies;
- mathematically corrected BRRK path-risk implementation;
- fixed and dynamic dispersion implementations;
- point-in-time / survivorship-aware universe implementation;
- PIT-DISP-0015 preregistration, workflow, exact-output exporter and validated results;
- Hyperliquid Plan B testnet/shadow execution service and tests;
- research/runtime dependencies and smoke workflow;
- exact daily PNL visualization;
- research history, literature review, experiment registry and stopping rules.

## Migrated original evidence records

The source PR formal evidence records remain under `research/results/`, including:

- AUDIT-0010/0012 calibration;
- AUDIT-0013 activation attribution;
- BRRK 0004–0011 records;
- derivatives/funding prospective snapshot;
- DISP-0013 and DISP-0014;
- Hyperliquid L2 execution-risk snapshot;
- PIT universe discovery/lifecycle/data-access audits;
- original PIT-DISP-0015 CI run-status record;
- frozen 0006 robustness and cycle-reentry audit.

Early rotation/ablation conclusions are consolidated in `docs/RESEARCH_HISTORY.md` and README.

## New canonical evidence generated after migration

The target repository subsequently completed the first valid PIT-DISP-0015 run. These are canonical target-repository evidence rather than migrated source evidence:

- `research/results/PIT_DISP_0015_RESULT_2026-08-04.md`;
- `research/results/pit_disp_0015/validated_summary.json`;
- `research/results/pit_disp_0015/daily_equity.csv`;
- `research/results/pit_disp_0015/daily_weights.csv`;
- `research/results/pit_disp_0015/daily_dynamic_universe_count.csv`;
- `research/results/pit_disp_0015/dispersion_scale.csv`;
- `research/results/pit_disp_0015/inactive_eligible_audit.csv`;
- `research/results/pit_disp_0015/pnl_daily.svg`;
- `docs/pnl.svg` generated from exact daily equity.

The valid run's full raw JSON and log are also retained in its GitHub Actions artifact; the repository persists a compact machine-readable validated summary plus exact daily source series.

The valid result includes 652 historical candidates, 646 symbols with data, zero fetch errors, and 159 currently inactive/non-TRADING symbols that were historically eligible.

## Superseded exploratory implementations

The source branch contains intermediate implementations that were rejected, superseded, or used only as one-off audit/collector scaffolding. They are not placed in the canonical runtime/import path.

Their research information is preserved through:

1. formal result records;
2. `research/regime_kelly/experiment_registry.json`;
3. `research/literature/LITERATURE_2026-08-04.md`;
4. `research/RESEARCH_ROADMAP_AFTER_0015.md`;
5. `docs/RESEARCH_HISTORY.md`;
6. `docs/SOURCE_INVENTORY.md`.

The original source PR #2 remains the immutable code-level archive for obsolete implementation details.

## Explicitly excluded

- unrelated code in `alexwang91/market` outside this crypto project;
- generated caches and transient logs;
- private keys, account secrets and deployment secrets;
- claims of valid historical funding PnL, because the attempted endpoint was blocked by HTTP451;
- any interpretation that PIT-DISP-0015 was production-promoted: it validated risk compression but failed the growth/opportunity-cost promotion gate.

## Canonical evidence hierarchy

1. `research/results/BRRK_0011_CDAR_CORRECTION_2026-08-04.md` — frozen baseline.
2. `research/results/PIT_DISP_0015_RESULT_2026-08-04.md` — survivorship-aware qualification result.
3. `research/results/pit_disp_0015/` — exact daily validated outputs and machine-readable summary.
4. `research/results/DISP_0014_MEDIAN_RATIO_REPLICATION_2026-08-04.md` — fixed-panel result, now classified selection-sensitive.
5. `research/results/AUDIT_0013_ACTIVATION_ATTRIBUTION_2026-08-04.md` — reason DISP-0013 was downgraded.
6. PIT universe discovery/lifecycle/data-access records — construction provenance.
7. `research/pit_universe/PIT-DISP-0015-DYNAMIC-UNIVERSE.json` — frozen preregistration.
8. `research/results/PIT_DISP_0015_RUN_STATUS_2026-08-04.md` — preserved historical CI failure record, superseded by the valid result rather than deleted.

For source-to-target file mapping, see `docs/SOURCE_INVENTORY.md`.
