# BRRK-WINNER-ROBUSTNESS-0002

Status: **PREREGISTERED_NOT_RUN**  
Pull request: **#152**

This governed research path preregisters one robustness panel for the exact 40% BTC / 60% sole-eligible-alt construction selected by `BRRK-WINNER-0001`. No new allocation split is searched here and no robustness economics have been executed.

## Frozen construction

```text
single-alt BTC share       40%
single-alt winner share    60%
all alternative splits     FORBIDDEN
```

Signals, eligibility, multi-alt allocation, caps, BRRK defensive gross scaling, universe, long-only constraint, gross cap and the canonical P3.3 5% L1 execution band remain unchanged.

## Reproduction gate

Before any robustness metric may be released, the full-horizon 5 bps canonical and 40/60 results must reproduce `research/brrk_winner_0001/PRIMARY_RESULT.json` within absolute tolerance `5e-10`. Reproduction failure invalidates the run and stops this research ID.

## Fixed temporal panel

The 1,332 primary daily return sessions are partitioned mechanically by observation order into three equal contiguous 444-session blocks. These blocks are frozen before robustness economics and are not market-regime labels.

```text
T1  2022-12-10 .. 2024-02-26   444 sessions
T2  2024-02-27 .. 2025-05-15   444 sessions
T3  2025-05-16 .. 2026-08-02   444 sessions
```

All three temporal blocks use the original 5 bps cost assumption and unchanged P3.3 5% L1 band.

## Fixed friction panel

The full 1,332-session horizon is evaluated at exactly:

```text
10 bps transaction cost    2x original cost
20 bps transaction cost    4x original cost
```

Canonical and candidate always use identical sessions and identical cost assumptions inside each panel cell.

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

See `PREREGISTRATION.json` for the compact machine-readable contract and `research/governance/BRRK_WINNER_ROBUSTNESS_0002_PREREG_DRAFT.json` for the Research Registry record.
