# BRRK Program Timeline Dashboard V2

Read-only observability dashboard for the BRRK program. V1 landed in PR #144; V2 adds date-level drilldown and canonical-target explainability without changing any economic or production authority.

## Purpose

The dashboard puts four evidence layers on one time axis without conflating their authority:

1. **Historical immutable backtest evidence** — existing repository CSV/JSON only.
2. **Research / product decisions** — `config/research_registry.json` and `config/decision_registry.json`.
3. **Phase-6 future-only shadow evidence** — public GitHub Actions schedule-run and artifact identity metadata.
4. **Future program gates** — Phase-6 acceptance, Phase-7 explicit launch approval, and Phase-8 trigger-gated research.

It does not authorize production, signing, order submission, withdrawal, transfer, Phase-7 launch, or any strategy change.

## Current historical sources

Canonical BRRK historical equity and target weights:

- `research/results/pit_disp_0015/daily_equity.csv`
- `research/results/pit_disp_0015/daily_weights.csv`

Funding-aware comparison window:

- `research/results/funding_pnl_0003/full_window_daily_equity.csv`

Frozen BRRK descriptive attribution context:

- `research/governance/brrk_signal_attribution_result.json`

The funding experiment identifies BRRK-0011 source columns including BTC, ETH, SOL, BNB and XRP. XRP remains **feature-only** in canonical target semantics and is therefore not plotted as a target holding. Dashboard target holdings are exactly BTC / ETH / SOL / BNB.

## V2 daily drilldown

V2 adds a large historical date scrubber, date input and chart-click selection. For any selected historical date it displays:

- NAV;
- daily PnL, calculated from consecutive values of the selected existing equity column;
- cumulative PnL from the first row of that existing history;
- running drawdown;
- BTC / ETH / SOL / BNB target weights;
- target gross exposure;
- adjacent-day target-weight deltas and L1 delta;
- per-asset target action: `ENTER`, `EXIT`, `INCREASE`, `DECREASE`, or `HOLD`.

The target-action threshold is an explicit dashboard display tolerance:

```text
REBALANCE_EPS = 1e-9
```

### Exact explainability boundary

The daily explanation is deliberately labelled:

```text
目标权重变化（由 canonical weights 派生）
```

This is an authoritative mechanical description of adjacent values already present in `daily_weights.csv`. It is **not** a claim that the dashboard has reconstructed P3.3 actual turnover or proved a unique day-level `signal -> trade` causal path.

The frozen BRRK attribution result does establish portfolio-level facts such as payoff asymmetry and strong right-tail dependence, but it does not provide a unique per-day signal-causality ledger. V2 therefore refuses to invent that stronger explanation.

Semantics frozen in the UI:

```text
dashboard_record_authoritative=false
scheduled_decision_credit_created=false
production_authorized=false
target_change_mechanics_authoritative_from_canonical_weights=true
execution_causality_asserted=false
```

## Forward Phase-6 ledger

The browser reads public GitHub workflow metadata for:

- workflow: `.github/workflows/research-governance.yml`
- event: `schedule`
- branch: `main`

A row is displayed as a **scheduled credit candidate** only when public metadata shows all three:

1. scheduled workflow conclusion is `success`;
2. a `phase6-evidence-*` artifact exists;
3. a `phase6-receipt-*` artifact exists.

This UI classification is deliberately weaker than formal Phase-6 acceptance. Formal credit remains governed by the canonical evidence contract and later acceptance review. The dashboard itself never creates evidence credit.

V2 does **not** fabricate detailed forward values that public artifact metadata does not expose. Until a separately governed browser-readable derived index exists, the dashboard does not claim to know artifact-internal target weights, account equity, shadow return, cumulative shadow PnL, alerts or provenance digests.

## Run locally

From repository root:

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/research/governance/dashboard/
```

The page fetches authoritative `main` data from GitHub, so it behaves as a live read-only view rather than a copied economic snapshot.

## Chart and table set

- cumulative NAV / PnL curve;
- historical date scrubber + date picker + chart-click drilldown;
- selected-day NAV / PnL / cumulative PnL / drawdown / gross / target L1 change;
- per-asset canonical target action table;
- daily PnL percentage;
- drawdown;
- stacked BTC/ETH/SOL/BNB target weights;
- frozen BRRK aggregate attribution context;
- all Research Registry records and status/promotion state;
- major program timeline;
- Phase-6 daily schedule / evidence / receipt ledger;
- visible Phase-7 and Phase-8 blocked future gates.

## Data semantics

Never visually splice the following into one continuous economic series:

```text
historical backtest NAV
!= Phase-6 hypothetical shadow PnL
!= future real-account PnL
```

Any future browser-readable Phase-6 daily summary must remain derived/read-only, must bind back to canonical evidence/receipt identities, and must not weaken the create-only evidence/receipt contract or create scheduled-decision credit.
