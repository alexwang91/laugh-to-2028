# BRRK Program Timeline Dashboard V4

Read-only observability dashboard for the BRRK program. V4 keeps the V3 audit semantics and redesigns only the presentation layer into a light, simplified Chinese interface. It changes no strategy mathematics, immutable result artifact, production authorization, signing, order-submission, withdrawal, transfer, or Phase-7 authority.

## Evidence layers

The page keeps these distinct:

```text
historical backtest NAV
!= Phase-6 hypothetical shadow PnL
!= future real-account PnL
```

Historical sources:

- `research/results/pit_disp_0015/daily_equity.csv`
- `research/results/pit_disp_0015/daily_weights.csv`
- `research/results/funding_pnl_0003/full_window_daily_equity.csv`

Governance sources:

- `config/research_registry.json`
- `config/decision_registry.json`

Runtime rules read and reviewed for V3, but not modified by this dashboard change:

- `execution/plan-b-bot/beta_bot/target_engine.py`
- `execution/plan-b-bot/beta_bot/target_math.py`
- `execution/plan-b-bot/beta_bot/rebalance_control.py`

XRP remains **feature-only**. Dashboard target holdings are exactly BTC / ETH / SOL / BNB.

## V4 presentation contract

The public page is intentionally optimized for a non-developer reader:

- light neutral background and white cards;
- blue as the primary chart color, restrained green/red for positive/negative returns;
- all primary user-facing headings, controls, table labels, explanations and workflow states are Chinese;
- raw curve identifiers are mapped to readable Chinese strategy names in the selector;
- complex P3.2/P3.3, Phase-6 and research-registry detail is collapsed behind Chinese disclosure panels;
- Plotly's mode bar is disabled so English tool labels do not leak into the primary UI;
- the homepage prioritizes return, drawdown, target holdings and selected-day changes.

This is presentation-only. All V3 evidence boundaries remain unchanged.

## V4 daily timing contract

P3.2 freezes this timing:

```text
decision D 00:00 UTC
uses completed daily data through D-1
target_session = D-1
that target is held over D return
```

For a selected historical row `t`, V4 therefore separates:

- the `t` target session;
- the mapped P3.2 decision time `t+1 00:00 UTC`;
- the `t+1` return for which that target is intended;
- the historical NAV return at row `t`, which used the prior row's target.

The dashboard does not introduce look-ahead by pairing the same-row target with the same-row historical return as a cause.

## P3.3 threshold contract

The canonical controller freezes:

```text
target_gap_metric = L1_ABSOLUTE_WEIGHT_GAP
rebalance_band = 0.05
boundary_rule = REBALANCE_WHEN_L1_GAP_GTE_BAND
```

The gap is:

```text
sum(abs(model_target_weight - current_position_weight))
```

Safety overrides force repair to the P3.2 target when the current state contains a short position or gross exposure above 1.

The V4 `adjacent target L1` chart is **not** this account gap. It only measures change between adjacent target vectors already stored in `daily_weights.csv`. The displayed 5% line is a controller-rule reference, not a historical execution trigger classification.

The historical `pit_disp_0015` result directory does not persist daily `current_position_weights`, `l1_target_gap`, `control_turnover_weight`, or P3.3 plans. Therefore V4 reports:

```text
historical_p3_3_execution_state_available=false
```

and does not invent actual `HOLD` / `REBALANCE` events.

## P3.2 signal / regime boundary

The runtime target implementation proves the model rules and output schema, including:

- decision D consumes D-1;
- `btc_trend < 0` selects the BTC-only V1 branch;
- ETH and SOL eligibility require positive score, positive asset trend, and positive ratio trend;
- BNB eligibility requires positive score plus positive slow BNB and BNB/BTC trends;
- V1 allocation caps are ETH 50%, SOL 35%, BNB 25% of budget, with overflow back to BTC;
- semantic states are `RISK_OFF`, `BTC_LEAD`, `MAJOR_ROTATION`, `ALT_EXPANSION`;
- P3.2 output contains `risk_state`, state probabilities, `riskoff_probability`, `meta_scale`, `defensive_scale`, and a feature snapshot;
- target output is long-only with gross <= 1.

However the frozen historical result directory does not persist these daily P3.2 snapshots. V4 therefore reports:

```text
historical_signal_snapshot_available=false
execution_causality_asserted=false
```

and never reverse-engineers a 2023 signal/regime from NAV or target weights.

## Range statistics

The selected range recomputes, from the selected existing equity series only:

- cumulative return;
- positive-return-day ratio;
- daily payoff ratio = mean positive daily return / abs(mean negative daily return);
- maximum drawdown;
- count of adjacent target-vector changes;
- sum of adjacent target-vector L1 changes.

`Positive-return-day ratio` is not labelled as holding-cycle win rate. Actual rebalance count, executed turnover and holding-cycle win rate stay `UNAVAILABLE` until an authoritative executed-turnover series exists.

## Daily target mechanics

For BTC / ETH / SOL / BNB, adjacent canonical target rows can be labelled mechanically as:

`ENTER`, `EXIT`, `INCREASE`, `DECREASE`, `HOLD`

with dashboard display tolerance:

```text
REBALANCE_EPS = 1e-9
```

These labels describe target-vector mechanics only. They are not P3.3 execution labels.

## Phase 6 ledger

The browser reads public GitHub Actions schedule-run and artifact metadata. A row is a scheduled-credit candidate only when:

1. `run.conclusion === success`;
2. a `phase6-evidence-*` artifact exists;
3. a `phase6-receipt-*` artifact exists.

This classification is weaker than formal acceptance. The dashboard itself never creates evidence credit and does not fabricate artifact-internal values not exposed through safe browser-readable evidence.

## Semantics frozen in source

```text
dashboard_version=v4-cn-simple-ui
dashboard_record_authoritative=false
scheduled_decision_credit_created=false
production_authorized=false
target_change_mechanics_authoritative_from_canonical_weights=true
p3_3_rule_authoritative_from_controller=true
historical_p3_3_execution_state_available=false
historical_signal_snapshot_available=false
execution_causality_asserted=false
```

## Local use

```bash
python -m http.server 8000
```

Open:

```text
http://localhost:8000/research/governance/dashboard/
```

The public deployment is expected to serve the merged `main` dashboard at `https://laugh-to-2028.vercel.app/`; deployment is considered complete only after that URL is independently verified to expose the V4 marker.
