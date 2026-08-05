# CARRY-PM-0035 controlled runbook

> **Superseded and not required.** `CARRY-RF-0036R1` re-priced CARRY-PNL-0031 against cash instead of zero and the sleeve failed the corrected `net_economics` gate, so the carry line is stopped under discipline #7 and no probe capital is committed. `CARRY-PM-0037` supersedes this gate's *design* (adds snapshot-gap and mid-price-drift bounds, and a three-state outcome instead of a clamp) without editing or deleting this file. See [`docs/RESEARCH_HISTORY.md`](RESEARCH_HISTORY.md#11-carry-pm-0035--superseded-and-no-longer-required), [`docs/CARRY_PM_0037_RUNBOOK.md`](CARRY_PM_0037_RUNBOOK.md), and [`docs/RISK_FREE_METRIC_CONVENTIONS.md`](RISK_FREE_METRIC_CONVENTIONS.md). Do not run this probe with live capital. The steps below are retained as the frozen historical design, not as live guidance.

This gate measures Hyperliquid Portfolio Margin account behavior for the already-verified BTC/UBTC implementation. It is **not** a strategy backtest and the research script never signs or submits orders.

## Current platform context

Hyperliquid's June 2026 official announcement states that Portfolio Margin is now in **beta** and supports BTC and HYPE as collateral. Rollout limits and eligibility can change, so current platform status should be checked before a live probe.

The **<$1,000 account value** and **$500 UBTC probe notional** below are project-imposed experimental safety/isolation limits. They are deliberately much smaller than current platform limits and are not claims about Hyperliquid's current eligibility requirements.

## Safety / isolation

Use a dedicated new account or subaccount with total value below **$1,000**. The probe spot notional is capped at **$500**. Keep all non-probe perp positions at zero.

The account-value limit is a manual precondition. Under Portfolio Margin, Hyperliquid documents the spot clearinghouse state as the authoritative unified balance/hold source rather than individual perp-DEX balance summaries, so the experiment does not invent an account-value formula from non-authoritative fields.

The account address is supplied to the script through `HL_PM_PROBE_USER`. The output stores only a SHA-256 fingerprint of the address, not the full address. Never put a private key in this secret or in the research workflow.

## Four frozen snapshots

Portfolio Margin mode must remain enabled for **all four snapshots**. Changing abstraction mode invalidates the probe.

### 1. `cash`

Requirements:

- account abstraction = `portfolioMargin`;
- Portfolio Margin enabled in spot state;
- no BTC perp position;
- no other perp positions;
- no probe UBTC balance above the fixed **$1 residual-value tolerance**.

Capture:

```bash
python research/carry/run_carry_pm_0035.py snapshot \
  --user "$HL_PM_PROBE_USER" \
  --label cash \
  --output research/results/carry_pm_0035/cash.json
```

### 2. `spot`

Acquire UBTC spot only. The actual observed UBTC spot notional must be greater than zero and no more than $500 plus the fixed 5% execution tolerance. Do not open the BTC short yet.

Capture `spot.json` with the same command and `--label spot`.

### 3. `matched`

Keep the **same UBTC quantity** from the spot-only snapshot, with a fixed maximum quantity change of **0.1%**. Then open a BTC short-perp sized to match the existing UBTC economic notional. The frozen spot/short notional mismatch tolerance is **2%**. Do not add any other position.

This quantity invariant is methodological: the only intended state change from `spot` to `matched` is addition of the BTC short leg.

Capture `matched.json`.

### 4. `closed`

Close the BTC short and exit the probe UBTC spot. Capture `closed.json` after:

- BTC short size is flat within the API numerical tolerance; and
- residual UBTC **market value is <= $1**.

The $1 residual rule was frozen before any account result. It prevents ordinary spot quantity dust from creating a false failure and is not a parameter to optimize.

## Compare

```bash
python research/carry/run_carry_pm_0035.py compare \
  --cash research/results/carry_pm_0035/cash.json \
  --spot research/results/carry_pm_0035/spot.json \
  --matched research/results/carry_pm_0035/matched.json \
  --closed research/results/carry_pm_0035/closed.json \
  --output research/results/carry_pm_0035/summary.json
```

## Frozen primary measurement

The experiment measures the incremental maintenance consumption of adding the matched BTC short after the UBTC spot is already present:

```text
raw_available_change_usdc
  = spot.tokenToAvailableAfterMaintenance[USDC]
    - matched.tokenToAvailableAfterMaintenance[USDC]

incremental_maintenance_consumption_usdc
  = max(0, raw_available_change_usdc)

incremental_maintenance_fraction
  = incremental_maintenance_consumption_usdc
    / matched_btc_short_notional
```

A negative raw change is retained in the evidence because it would mean the matched hedge increased available capacity; the structural capital factor is floored at zero rather than converting such a hedge benefit into negative capital consumption.

The first valid probe passes the capital-efficiency gate only when this fraction is **<= 25%**, while the matched account's `portfolioMarginRatio` is below **0.50** and all other frozen structural checks pass.

The 25% threshold is intentionally coarse. It only answers whether Portfolio Margin produces a material structural reduction versus treating the second leg as effectively fully funded. It is not a leverage target or a value to optimize.

## Data-authority rule

Portfolio Margin / Unified Account balances and holds are read from `spotClearinghouseState`. `clearinghouseState` is used for BTC position diagnostics, but its individual DEX balance fields are not treated as the authoritative unified balance source.

## Stopping rule

If the first valid probe fails or returns an inconclusive state:

- retain the result;
- diagnose API/state/account-isolation defects only;
- do not retune probe notional, 0.1% spot-quantity invariant, 2% match tolerance, PM-ratio threshold, maintenance-fraction threshold, dust thresholds, or account structure from that outcome;
- do not run a BRRK+carry stack experiment.

A PASS authorizes only a separately preregistered PM-aware stack accounting experiment using the observed capital factor. It does not authorize production or leverage.
