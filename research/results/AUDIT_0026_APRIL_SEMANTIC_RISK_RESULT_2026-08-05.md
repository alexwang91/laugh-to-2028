# AUDIT-0026 Result — Frozen HMM Does Not See the April 2024 Risk

`AUDIT-0026-APRIL-SEMANTIC-RISK` is a **no-trading-change attribution audit** following `AUDIT-0025`. It asks whether the existing monthly-fitted PCA4 HMM already contained useful daily semantic `P(RISK_OFF)` information during the unresolved April 2024 tail.

## Status

**SEMANTIC RISK INFORMATION ABSENT IN APRIL — NO DAILY HMM VETO AUTHORIZED.**

GitHub Actions run `30959280178` completed successfully. The HMM, PCA transform and semantic mapping remain frozen within each scheduled 30-day interval; only causal filtering is updated daily. No daily refit or new feature is introduced.

## April 2024 result

Primary window: 2024-03-01 through 2024-05-15.

- starting `P(RISK_OFF)`: **1.70e-41**;
- maximum `P(RISK_OFF)`: **6.38e-08**;
- date of maximum: **2024-05-01**;
- mean `P(RISK_OFF)`: **1.73e-09**;
- no crossing of descriptive 25%, 50% or 75% probability levels;
- existing `btc_drawdown_252` reaches **-20.13%**.

The semantic HMM therefore remains effectively certain that the market is **not** RISK_OFF throughout the unresolved episode.

Selected dates:

- 2024-04-02: BTC 252d drawdown **-10.41%**, `P(RISK_OFF)=9.78e-22`;
- 2024-04-13: drawdown **-12.52%**, `P(RISK_OFF)=1.30e-14`;
- 2024-04-17: drawdown **-16.14%**, `P(RISK_OFF)=1.65e-09`;
- 2024-04-30: drawdown **-16.97%**, `P(RISK_OFF)=3.75e-08`;
- 2024-05-01: drawdown **-20.13%**, `P(RISK_OFF)=6.38e-08`.

This is not a cadence problem. Even with daily filtering, the frozen model does not assign meaningful probability to the semantic risk-off state.

## June comparison

June shows the same semantic limitation:

- starting `P(RISK_OFF)`: **1.04e-11**;
- maximum: only **8.31e-05** on 2024-06-28;
- existing BTC drawdown reaches **-17.49%**;
- no 25/50/75% descriptive crossing.

June's partial improvement under `ASYM-BETA-0024` came from daily trend / p_bad / semivol updates, not from semantic RISK_OFF probability.

## Full-history context

The semantic state is not globally useless. Over the full frozen-filter sample its probability is extremely bimodal:

- median: **3.59e-08**;
- 75th percentile: **0.00166**;
- 90th percentile: **0.99990**;
- 95th percentile: **0.999994**.

There are 13 monthly intervals in which daily frozen-fit probability crosses the descriptive 25/50/75% levels. When `P(RISK_OFF)>=0.5`, descriptive subsequent BTC returns are negative on average:

- mean next 1d: **-0.072%**;
- mean next 5d: **-0.328%**;
- mean next 10d: **-0.403%**.

So the semantic risk state has information when it actually fires. The problem is specifically that **April 2024 is not recognized as that state at all**.

## Interpretation

This result closes another tempting rescue path:

> Giving the existing HMM a faster daily veto would not have fixed April, because the relevant probability stayed essentially zero.

The existing `btc_drawdown_252` clearly deteriorates during April, but selecting a new drawdown threshold from this same failed episode would be post-hoc threshold fitting and is not authorized by this audit.

## Decision

1. Do **not** add daily semantic `P(RISK_OFF)` as a new extra-beta veto under this historical family.
2. Do **not** tune the HMM, PCA count, semantic mapping or refit cadence to rescue April on the same sample.
3. Do **not** select a `btc_drawdown_252 > X%` exit threshold from the April path.
4. Preserve `ASYM-BETA-0024` as the best historical bull-extra architecture found under the authorized sequence, but stop attempting to rescue its April tail with the same historical sample.
5. The appropriate next evidence for the bull-extra sleeve is **forward shadow**, where 0024 can be observed without live allocation and without retuning.
6. To pursue higher portfolio Sharpe, shift research effort away from further BRRK gating and toward a separately preregistered low-correlation return sleeve (time-series momentum first, then carry), consistent with the portfolio-construction direction already identified.
7. SOL-specific overweight remains a separate conditional-beta research question and should not be mixed into the generic extra-beta tail repair loop.
