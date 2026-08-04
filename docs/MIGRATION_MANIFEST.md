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
- BRRK feature/state/scenario dependencies needed by the current baseline and PIT-DISP-0015 path;
- mathematically corrected BRRK path-risk implementation;
- dispersion overlay implementation;
- point-in-time / survivorship-aware universe implementation;
- PIT-DISP-0015 preregistration and manual workflow;
- Hyperliquid Plan B testnet/shadow execution service and tests;
- research/runtime dependency files and smoke workflow;
- PNL visualization;
- research history, literature review, experiment registry and next-step stopping rules.

## Migrated as original evidence records

All formal Markdown records from the source PR `research/results/` evidence set are retained under `research/results/`, including:

- AUDIT-0010 tail calibration;
- AUDIT-0012 PIT calibration;
- AUDIT-0013 activation attribution;
- BRRK 0004/0005 OOS comparison;
- BRRK 0006 frozen candidate;
- BRRK 0007 factor ensemble / CYCLE-0002;
- BRRK 0008 anchor-stable rejection;
- BRRK 0009 label-free rejection;
- BRRK 0011 path-CDaR correction;
- derivatives/funding prospective snapshot;
- DISP 0013 result;
- DISP 0014 literature replication;
- Hyperliquid L2 execution-risk snapshot;
- PIT universe discovery/lifecycle/data-access audits;
- PIT-DISP-0015 run-status record;
- frozen 0006 robustness and cycle-reentry audit.

Early fixed-universe rotation/ablation conclusions that predate this formal result set are consolidated in `docs/RESEARCH_HISTORY.md` and the root README.

## Superseded exploratory implementations

The source research branch contains intermediate implementations that were explicitly rejected, superseded, or used only as one-off audit/collector scaffolding. They are project-related historically, but they are not placed in the canonical runtime/import path of the new repository.

Their research information is preserved through:

1. the formal result records above;
2. `research/regime_kelly/experiment_registry.json`;
3. `research/literature/LITERATURE_2026-08-04.md`;
4. `research/RESEARCH_ROADMAP_AFTER_0015.md`;
5. `docs/RESEARCH_HISTORY.md`;
6. `docs/SOURCE_INVENTORY.md`, which maps the source PR tree to the curated target tree.

The original PR #2 remains the immutable code-level archive for obsolete implementation details. This avoids making rejected specifications look supported while preserving their conclusions and provenance.

## Explicitly excluded

- unrelated code already present in `alexwang91/market` outside this crypto research PR/branch;
- generated logs and cache files;
- temporary runtime reports unless they are preregistration/evidence records;
- private keys, account secrets or deployment secrets;
- any claim of a valid historical funding PnL result (the historical funding fetch was blocked by HTTP 451);
- any claimed PIT-DISP-0015 performance (no valid model run exists yet).

## Canonical evidence hierarchy after migration

1. `research/results/BRRK_0011_CDAR_CORRECTION_2026-08-04.md` — frozen baseline.
2. `research/results/DISP_0014_MEDIAN_RATIO_REPLICATION_2026-08-04.md` — strongest shadow risk overlay.
3. `research/results/AUDIT_0013_ACTIVATION_ATTRIBUTION_2026-08-04.md` — reason DISP-0013 was downgraded.
4. `research/results/PIT_UNIVERSE_0001_DISCOVERY_2026-08-04.md` — archive enumeration.
5. `research/results/PIT_UNIVERSE_0002_LIFECYCLE_2026-08-04.md` — quantified survivorship problem.
6. `research/results/PIT_UNIVERSE_0003_DATA_ACCESS_2026-08-04.md` — historical inactive-symbol data feasibility.
7. `research/pit_universe/PIT-DISP-0015-DYNAMIC-UNIVERSE.json` — frozen next qualification test.
8. `research/results/PIT_DISP_0015_RUN_STATUS_2026-08-04.md` — explicitly records that no valid result exists yet.

For source-to-target file mapping, see `docs/SOURCE_INVENTORY.md`.
