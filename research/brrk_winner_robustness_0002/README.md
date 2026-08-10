# BRRK-WINNER-ROBUSTNESS-0002

Status: **RUN_INTERFACE_FROZEN_NOT_RUN**  
Pull request: **#153**  
Merged preregistration: **PR #152 / `11c7967e4d22766b3abee33d382ab2912c16f5cb`**

This governed research path contains the merged preregistration and the frozen pre-result run interface for one robustness panel of the exact 40% BTC / 60% sole-eligible-alt construction selected by `BRRK-WINNER-0001`. `RUN_ONCE.marker` is absent, so no robustness economics have been executed on PR #153 yet.

## Frozen construction

```text
single-alt BTC share       40%
single-alt winner share    60%
all alternative splits     FORBIDDEN
```

The runner imports the already-closed `BRRK-WINNER-0001` candidate constructor rather than implementing another allocation rule. Signals, eligibility, multi-alt allocation, caps, BRRK defensive gross scaling, universe, long-only constraint, gross cap and the canonical P3.3 5% L1 execution band remain unchanged.

## Reproduction gate

Before any robustness metric may be computed or written, the full-horizon 5 bps canonical and 40/60 metric payloads must reproduce `research/brrk_winner_0001/PRIMARY_RESULT.json` within absolute tolerance `5e-10`, and both canonical/candidate target-frame SHA256 values must match the merged primary evidence. Reproduction failure aborts without a robustness result file.

## Fixed temporal panel

The 1,332 primary daily return sessions are partitioned mechanically into three equal contiguous 444-session blocks:

```text
T1  2022-12-10 .. 2024-02-26   444 sessions
T2  2024-02-27 .. 2025-05-15   444 sessions
T3  2025-05-16 .. 2026-08-02   444 sessions
```

Implementation semantics are frozen in `RUN_INTERFACE.json`: simulate the complete continuous 5 bps P3.3 path once, preserve economic-position continuity across block boundaries, then slice realized returns for subperiod metrics. The sliced NAV is renormalized to 1 for each block's CAGR and drawdown calculation only. No boundary position reset or artificial boundary rebalance occurs.

## Fixed friction panel

The complete 1,332-session canonical and candidate target paths are replayed at exactly:

```text
10 bps transaction cost    2x original cost
20 bps transaction cost    4x original cost
```

Only `cost_bps` changes. The P3.3 5% L1 band, fill fraction, transaction-cost multiplier, funding semantics, target paths and initial-position semantics remain frozen.

## Frozen admission gates

A full PASS requires all preregistered gates, including:

- candidate CAGR not below canonical in at least two of three temporal blocks;
- temporal-block maximum-drawdown deterioration no worse than 4.00 percentage points in every block;
- candidate CAGR strictly above canonical at both 10 bps and 20 bps full-horizon stresses;
- at both cost stresses, maximum-drawdown deterioration no worse than 4.00 percentage points and Calmar not below canonical;
- reproduced 5 bps canonical-best-20 log-growth capture at least 98%;
- total turnover no more than 1.25x canonical;
- long-only, gross <= 1.0, BTC/ETH/SOL/BNB only, unchanged P3.3 band and zero production authority.

## Evidence status

The study reuses `BRRK-WINNER-0001-CANONICAL-HIST-V1`, which is already consumed and researcher-exposed DEVELOPMENT history. This robustness study is explicitly result-informed and cannot claim independent OOS, temporal novelty or future-only evidence.

A PASS can only make a new, separately preregistered future-only validation stage eligible. It cannot modify canonical `BRRK-0011`, Phase 6 scheduled-decision credit, Phase 7, execution authority, signing, order submission, leverage, shorts or production authorization.

See `PREREGISTRATION.json` for the merged research contract, `RUN_INTERFACE.json` for the frozen execution semantics, and `research/governance/BRRK_WINNER_ROBUSTNESS_0002_PREREG_DRAFT.json` for the Research Registry record.
