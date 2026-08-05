# CARRY-PM-0035 controlled runbook

This gate measures Hyperliquid Portfolio Margin account behavior for the already-verified BTC/UBTC implementation. It is **not** a strategy backtest and the research script never signs or submits orders.

## Safety / isolation

Use a dedicated new account or subaccount with total value below **$1,000**. The probe spot notional is capped at **$500**. Keep all non-probe perp positions at zero.

The current Hyperliquid Portfolio Margin documentation recommends small new accounts/subaccounts for full behavior testing because caps can cause fallback to non-portfolio-margin behavior.

The account address is supplied to the script through `HL_PM_PROBE_USER`. The output stores only a SHA-256 fingerprint of the address, not the full address.

## Four frozen snapshots

### 1. `cash`

Requirements:

- account abstraction = `portfolioMargin`;
- Portfolio Margin enabled in spot state;
- no BTC perp position;
- no other perp positions;
- no probe UBTC balance.

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

Open a BTC short-perp sized to match the existing UBTC economic notional. The frozen comparison tolerance is **2%**. Do not add any other position.

Capture `matched.json`.

### 4. `closed`

Close the BTC short and exit the probe UBTC spot. Capture `closed.json` after:

- BTC short size is exactly flat within the API numerical tolerance; and
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
incremental_maintenance_consumption_usdc
  = max(0,
      spot.tokenToAvailableAfterMaintenance[USDC]
      - matched.tokenToAvailableAfterMaintenance[USDC])

incremental_maintenance_fraction
  = incremental_maintenance_consumption_usdc
    / matched_btc_short_notional
```

The first valid probe passes the capital-efficiency gate only when this fraction is **<= 25%**, while the matched account's `portfolioMarginRatio` is below **0.50** and all other frozen structural checks pass.

The 25% threshold is intentionally coarse. It only answers whether Portfolio Margin produces a material structural reduction versus treating the second leg as effectively fully funded. It is not a leverage target or a value to optimize.

## Stopping rule

If the first valid probe fails or returns an inconclusive state:

- retain the result;
- diagnose API/state/account-isolation defects only;
- do not retune probe notional, match tolerance, PM-ratio threshold, maintenance-fraction threshold, closed-dust threshold, or account structure from that outcome;
- do not run a BRRK+carry stack experiment.

A PASS authorizes only a separately preregistered PM-aware stack accounting experiment using the observed capital factor. It does not authorize production or leverage.
