# AUDIT-0025 Result — Long-Horizon Trend Masks 20d Weakness, but No Clean Short-Horizon Veto Is Authorized

`AUDIT-0025-APRIL-TREND-DECOMP` is a **no-trading-change attribution audit** authorized after `ASYM-BETA-0024` left April 2024 as the dominant unresolved tail episode.

## Status

**MASKING MECHANISM CONFIRMED / SHORT-TREND VETO NOT AUTHORIZED.**

GitHub Actions run `30958976327` completed successfully. The exact frozen BTC trend score was decomposed into its existing 20/60/120/240-day components. No alternative horizon, weight or threshold was tested.

## Validation

The weighted component reconstruction matches the existing `btc_trend` exactly:

- maximum absolute reconstruction error: **0.0**.

Frozen construction:

```text
20d  weight 0.15
60d  weight 0.25
120d weight 0.30
240d weight 0.30

component_h = tanh(log(P_t/P_t-h) / (std_h(log return) * sqrt(h)))
```

## April 2024 primary finding

Audit window: 2024-03-01 through 2024-05-15.

Natural negative crossings:

- 20d component: **2024-03-19**;
- 60d component: **2024-04-30**;
- 120d component: no negative crossing;
- 240d component: no negative crossing.

Within this window:

- **35 days** have `20d < 0` while aggregate `btc_trend > 0`;
- **12 days** have both `20d < 0` and `60d < 0` while aggregate trend remains positive;
- minimum 20d component: **-0.905**;
- minimum 60d component: **-0.596**;
- minimum 120d component: **+0.647**;
- minimum 240d component: **+0.957**;
- minimum aggregate trend: still **+0.267**.

The long-horizon weighted contribution remains large enough to keep the aggregate signal positive even when the short component has materially weakened. This is a real masking effect.

Examples during the unresolved April drawdown:

- 2024-04-02: 20d **-0.522**, 60d +0.918, 120d +0.873, 240d +0.965; aggregate still **+0.703**;
- 2024-04-17: 20d **-0.798**, 60d +0.545, 120d +0.804, 240d +0.970; aggregate still **+0.549**;
- 2024-04-28: 20d **-0.803**, 60d +0.042, 120d +0.836, 240d +0.977; aggregate still **+0.434**;
- only on 2024-04-30 does the 60d component finally turn negative, while aggregate remains +0.356.

## Why this does not authorize a simple 20d veto

The 20d-negative / aggregate-positive condition is common:

- **400 days** over the full completed sample.

Forward BTC returns after those days are not consistently negative enough to elevate the natural sign crossing into an approved trading rule:

- mean 1d: -0.055%;
- mean 5d: +0.010%;
- mean 10d: +0.123%;
- median 10d: -0.565%.

The stricter condition where both 20d and 60d are negative while aggregate remains positive is less common (**133 days**) and has more negative descriptive forward returns:

- mean 1d: -0.359%;
- mean 5d: -0.885%;
- mean 10d: -0.592%;
- median 10d: -0.801%.

However, that joint condition does not appear in the April episode until **2024-04-30**, after most of the April incremental loss has already occurred. It therefore cannot explain or repair the main April failure in a timely way.

## June comparison

June behaves differently and is consistent with the already validated latency story:

- 60d crosses negative on 2024-06-07;
- 20d crosses negative on 2024-06-09;
- both are negative with aggregate still positive from 2024-06-09;
- 120d finally turns negative on 2024-06-27;
- 240d remains positive throughout June.

Thus short-horizon confirmation could plausibly help June, but `ASYM-BETA-0024` has already addressed much of that episode through daily refresh. The unresolved problem remains April.

## Decision

1. **Long-horizon masking is real.** The current 120d/240d components can keep aggregate trend strongly positive during a sharp short-horizon reversal.
2. **Do not tune trend weights or horizons.** The audit does not authorize changing 0.15/0.25/0.30/0.30 or adding a fitted component threshold.
3. **Do not promote `20d < 0` as a veto.** It is too frequent/noisy across history.
4. **Do not promote `20d < 0 and 60d < 0` as the April fix.** It becomes active too late in the primary failure episode.
5. The next attribution should stay within already-existing information and inspect the frozen HMM's **daily semantic `P(RISK_OFF)`** plus the existing `btc_drawdown_252` trajectory during April. `p_bad` is a raw-state profitability diagnostic and remained near zero in April; the semantic risk posterior may contain different information.
6. No SOL-specific overweight is authorized by this audit. SOL remains a separate later satellite/beta-allocation question after the generic extra-beta risk architecture is stable.
