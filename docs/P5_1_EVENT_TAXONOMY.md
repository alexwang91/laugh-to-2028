# P5.1 Event Taxonomy — Cycle-top / Late-bull / Exit Research

Status: **FROZEN BEFORE P5.2 FEATURE SELECTION**  
Contract: `P5.1-EVENT-TAXONOMY-V1`  
Base main: `b61a368383d08b83d04a2aec52777cf31196efac`

## Purpose

P5.1 defines **what historical situations the Phase-5 model must distinguish** before any indicator or model family is evaluated.

This is not an exit model. It does not select RSI, dominance, breadth, funding, OI, KAMA, trend slopes, or any other feature. It freezes the evaluation cases so later research cannot move a historical top date merely because one signal looks better on a nearby day.

The controlling product decision remains `PRODUCT-CYCLE-EXIT-2026-08-05`.

## Canonical anchor data

Event anchors use the existing P3.1 signal-data authority:

```text
Binance spot BTCUSDT
UTC 1d completed close
00:00 UTC canonical daily boundary
no forward fill
missing required day = fail closed
```

BTC is used to resolve the event anchor because the Master Plan defines BTC as the dominant cycle reference asset. This does **not** mean BTC alone will determine the future P5 state model.

## Anchor mechanics

The calendar search windows below are frozen first. The final anchor date inside each window is mechanical:

- `BTC_CLOSE_MAX_IN_SEARCH_WINDOW` — earliest date of the maximum canonical BTC close in the fixed window;
- `BTC_CLOSE_MIN_IN_SEARCH_WINDOW` — earliest date of the minimum canonical BTC close in the fixed window;
- `MAX_10D_DRAWDOWN_END` — earliest date of the worst close-versus-trailing-10-calendar-day-peak drawdown in the fixed window;
- `PARENT_EVENT_ANCHOR` — reuse another event's already-resolved anchor for a subsequent outcome phase.

The resolver is `research/cycle_exit/p5_1_event_taxonomy.py`.

## Frozen required cases

| Event | Class | Fixed search window | Anchor rule | Interpretation |
| --- | --- | --- | --- | --- |
| 2021 spring major top | `LOCAL_MAJOR_TOP_NONTERMINAL` | 2021-03-15 → 2021-05-15 | max BTC close | first major top / May crash, but not the final 2021 cycle top |
| 2021 summer recovery | `SECOND_WIND_TRANSITION` | 2021-05-16 → 2021-07-31 | min BTC close | recovery / second-wind transition after the spring crash |
| 2021 November terminal top | `TERMINAL_TOP_BEAR_TRANSITION` | 2021-10-01 → 2021-11-30 | max BTC close | explicit terminal 2021 top / bear transition |
| 2025 June new high | `TEMPORARY_NEW_HIGH_PHASE` | 2025-05-01 → 2025-06-30 | max BTC close | first required 2025 new-high phase |
| 2025 August new high | `SECOND_WIND_NEW_HIGH_PHASE` | 2025-07-01 → 2025-08-31 | max BTC close | renewed / second-wind new-high phase |
| 2025 October new high / deleveraging | `NEW_HIGH_DELEVERAGING_PHASE` | 2025-09-01 → 2025-10-31 | max BTC close | new high followed by deleveraging dynamics |
| late-2025 deterioration | `POST_DELEVERAGING_DETERIORATION` | 2025-10-01 → 2025-12-31 | parent October anchor | subsequent deterioration phase, not silently declared a terminal-cycle top |

### Terminal-label discipline

Only the 2021 November event is explicitly labeled `TERMINAL_TOP_BEAR_TRANSITION` in V1.

The 2025 windows are deliberately **not** declared terminal cycle tops. They exist to force the later model to distinguish temporary highs, second winds, deleveraging, and deterioration instead of learning a simplistic rule that every high-volatility new high means immediate cycle exit.

## Frozen non-top controls

At least three high-volatility non-top controls are mandatory. V1 contains four:

1. 2021 January–February high-volatility pullback window;
2. 2021 August–October high-volatility second-wind window;
3. 2024 March–May masking/stress window already used in prior registered stress work;
4. 2025 February–May high-volatility window before the required 2025 new-high sequence.

Control anchors use `MAX_10D_DRAWDOWN_END`.

The purpose is to penalize a future model that reacts to ordinary volatility as if it were a terminal top.

## Evaluation buckets

Every resolved anchor is evaluated using the same relative calendar buckets:

```text
early_warning    -28 .. -15 days
target_lead      -14 ..  -7 days
near_event        -6 ..   0 days
immediate_after   +1 .. +28 days
medium_after     +29 .. +90 days
```

The `target_lead` bucket implements the Master Plan's interest in approximately 7–14 days of useful warning. It is an **evaluation bucket, not a forced optimization target**. If evidence does not support reliable 7–14 day lead, P5 must report that rather than retune labels or features to manufacture it.

## Causality / leakage boundary

P5.1 labels may use realized future outcomes to state what happened historically. That is normal supervised-label construction.

P5.2 and later predictive features are different: for an evaluation date `t`, a feature may use only information observable by `t` under the canonical data contract.

Forbidden examples:

- choosing the top anchor after seeing where RSI divergence is prettiest;
- moving the June/August/October windows after feature scoring;
- using post-anchor price action inside a feature evaluated before the anchor;
- reclassifying a 2025 event as terminal merely because a model scores it highly;
- changing BRRK-0011 relative ranking to improve P5 labels.

## What P5.1 does not change

- BRRK-0011 remains frozen;
- BTC/ETH/SOL/BNB remain the long target universe;
- XRP remains feature-only;
- Hyperliquid remains the primary venue;
- P4.1 remains `[0,1]`;
- production gross remains `1.0`;
- LEVERAGE-0040 and LEVERAGE-0041 remain immutable `NO_PROMOTION` results;
- no production component is authorized.

## Completion gate

P5.1 is complete when:

1. the machine-readable taxonomy is frozen;
2. the deterministic validator/resolver contract is tested;
3. required 2021/2025 cases and multiple non-top controls are present;
4. the causal feature boundary is explicit;
5. CI/governance passes and the taxonomy is merged before P5.2 feature evaluation begins.

After that, the unique next task is **P5.2 Feature Families** under this unchanged taxonomy.
