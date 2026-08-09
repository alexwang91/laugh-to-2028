# BRRK Program Timeline Dashboard V1

Read-only observability dashboard for the BRRK program. Governance handoff: PR #144.

## Purpose

The dashboard puts four different layers on one time axis without conflating their authority:

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

The frozen funding experiment explicitly identifies the BRRK-0011 source columns as:

- `BRRK0011_BASELINE__BTC`
- `BRRK0011_BASELINE__ETH`
- `BRRK0011_BASELINE__SOL`
- `BRRK0011_BASELINE__BNB`
- `BRRK0011_BASELINE__XRP`

XRP remains feature-only in the canonical target semantics and is therefore not plotted as a target holding.

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

## Run locally

From repository root:

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/research/governance/dashboard/
```

The page fetches authoritative `main` data from GitHub, so it behaves as a live read-only view rather than a copied snapshot.

## V1 chart set

- cumulative NAV / PnL curve;
- daily PnL percentage;
- drawdown;
- stacked BTC/ETH/SOL/BNB target weights;
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

A future V2 may add a separately persisted daily Phase-6 dashboard summary containing target weights, hypothetical shadow return, account equity, alerts and provenance digests. That summary must remain derived/read-only and must not weaken the create-only evidence/receipt contract.
