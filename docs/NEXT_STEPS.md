# Next Steps

> **Forward source of truth changed on 2026-08-05.**
>
> Read these in order before starting new work:
>
> 1. `docs/MASTER_PLAN_2026-08-05.md`
> 2. `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`
> 3. `docs/PROJECT_GOVERNANCE_2026-08-05.md`
>
> This file is intentionally short. The detailed roadmap now lives in the documents above so future work is driven by one ordered dependency chain rather than by whichever research line was edited most recently.

---

## Current authorized next task

```text
P0.1 Canonical product config
+
P0.2 Decision registry
```

After P0 closes, proceed to **Phase 1 — Account and execution truth**.

Do not skip directly to cycle-top modeling, leverage deployment or a new short universe before their dependencies are complete.

---

## Product baseline

Current high-level decisions:

```text
Long universe: BTC / ETH / SOL / BNB
Primary venue: Hyperliquid
Initial capital: $2,000 cash/stablecoin
Recurring manual contribution: $100/week
Normal decision frequency: daily
Canonical daily boundary: 00:00 UTC
Intraday channel: risk reduction only
Leverage: model-determined, not a fixed user multiple
Catastrophic drawdown tolerance: 70% boundary, not operating target
FLAT: zero directional exposure
FLAT -> LONG/SHORT: human approval required
Production upgrades: blue/green manual cutover; no hot strategy patching
Bot credential: trading Agent/API only; no master wallet private key; no automated withdrawals
```

---

## Frozen historical decisions that remain in force

The new master plan does **not** reopen stopped research lines.

- BRRK-0011 remains the canonical directional research target unless a future registered replacement passes its gates.
- Dynamic PIT alpha portfolio line remains stopped on the tested sample.
- TSMOM-ALPHA-0029 remains rejected on the tested sample.
- all-perp implementation remains rejected as the default; instrument routing remains required.
- BTC verified spot-first evidence remains useful.
- CARRY line remains stopped after corrected risk-free cash economics failed.
- no live Portfolio Margin carry probe is authorized.
- historical ASYM-BETA work remains evidence, but higher live gross exposure is not authorized until execution and forward gates pass.

See `README.md`, `docs/RESEARCH_HISTORY.md`, `docs/REVIEW_FIX_BACKLOG.md` and the relevant `research/results/` directories for the preserved detailed evidence.

---

## Ordered forward program

```text
P0  canonical product/state registry
P1  account/order/fill reconciliation and execution hardening
P2  Hyperliquid BRRK instrument router
P3  production-quality daily BRRK target engine
P4  dynamic leverage extension and operating-risk selection
P5  2021/2025 cycle-top / late-bull / exit model
P6  integrated live-data shadow system
P7  limited-capital live long program
P8  future bear-short research
```

The detailed task definitions and acceptance gates are in `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`.

---

## Correction loop

Every task follows:

```text
PLAN
-> define acceptance criteria
-> IMPLEMENT
-> TEST
-> REVIEW
-> classify failure
-> FIX or STOP
-> record evidence
-> update roadmap status
-> next dependency
```

Allowed evidence statuses:

```text
PASS_PRODUCTION_CANDIDATE
PASS_SHADOW_ONLY
FAIL_STOP
FAIL_FIX_IMPLEMENTATION
MEASUREMENT_INCONCLUSIVE
```

Do not silently tune a failed historical result until it passes. Parameter changes intended to rescue a failed sample require a new registered experiment.

---

## Immediate implementation intent

The first implementation change after this planning set is merged should create:

1. a machine-readable canonical product/config registry;
2. a machine-readable decision/status registry;
3. tests proving the registries are the single source used by execution/research integration code.

Only after that should Phase 1 execution-state hardening begin.