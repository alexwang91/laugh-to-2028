# Migration Manifest

Migration date: 2026-08-04

Source research repository: `alexwang91/market`

Source research branch: `chatgpt/crypto-rotation-backtest-20260804`

Source draft PR: `alexwang91/market#2`

Target canonical repository: `alexwang91/laugh-to-2028`

## Scope rule

Only the crypto systematic-allocation project is in scope. Unrelated market/business/application code from `market` is deliberately excluded.

The target repository is organized by function rather than mirroring the old mixed repository byte-for-byte.

### Migrated as canonical runnable/current code

- frozen rotation backtest core;
- BRRK evidence and corrected baseline documentation;
- point-in-time / survivorship-aware universe implementation;
- PIT-DISP-0015 preregistration and implementation;
- Hyperliquid Plan B execution service and configuration;
- PNL visualization;
- research history and next-step stopping rules.

### Migrated as original evidence records

The following source result records are preserved under `research/results/`:

- BRRK 0004/0005 OOS comparison;
- BRRK 0006 frozen candidate;
- BRRK 0011 path-CDaR correction;
- AUDIT 0012 PIT calibration;
- DISP 0013 result;
- AUDIT 0013 activation attribution;
- DISP 0014 literature replication;
- PIT universe lifecycle audit;
- PIT universe historical-data access audit;
- PIT-DISP-0015 run status.

These are the evidence records used by the root README and `docs/RESEARCH_HISTORY.md`.

## Superseded exploratory implementations

The source research branch contains many intermediate implementations (early HMM variants, factor ensembles, label-free variants, cycle/reentry experiments and robustness scripts). They are project-related historically, but many were explicitly rejected or superseded.

To avoid presenting obsolete code as current strategy code, the target repository does **not** place all of those old scripts in the canonical execution path. Their experiment IDs, methodology, conclusions and rejection reasons are consolidated in `docs/RESEARCH_HISTORY.md`, while the original source PR remains the immutable code-level audit trail for those superseded implementations.

This is intentional curation, not omission of their research conclusions.

## Explicitly excluded

- unrelated code already present in `alexwang91/market` outside this research branch/PR;
- generated logs and cache files;
- temporary JSON runtime reports covered by `.gitignore` unless they are preregistration/evidence records;
- private keys, account secrets or Vercel environment values;
- any claim of a valid historical funding PnL result (the historical funding fetch was blocked by HTTP 451);
- any claimed PIT-DISP-0015 performance (no valid model run exists yet).

## Canonical evidence hierarchy after migration

1. `research/results/BRRK_0011_CDAR_CORRECTION_2026-08-04.md` — frozen baseline.
2. `research/results/DISP_0014_MEDIAN_RATIO_REPLICATION_2026-08-04.md` — strongest shadow risk overlay.
3. `research/results/AUDIT_0013_ACTIVATION_ATTRIBUTION_2026-08-04.md` — reason DISP-0013 was downgraded.
4. `research/results/PIT_UNIVERSE_0002_LIFECYCLE_2026-08-04.md` — quantified survivorship problem.
5. `research/results/PIT_UNIVERSE_0003_DATA_ACCESS_2026-08-04.md` — historical inactive-symbol data feasibility.
6. `research/pit_universe/PIT-DISP-0015-DYNAMIC-UNIVERSE.json` — frozen next qualification test.
7. `research/results/PIT_DISP_0015_RUN_STATUS_2026-08-04.md` — explicitly records that no valid result exists yet.
