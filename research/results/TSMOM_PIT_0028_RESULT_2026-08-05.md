# TSMOM-PIT-0028 Result — Daily PIT Perpetual Eligibility Frozen

`TSMOM-PIT-0028-DAILY-ELIGIBILITY` is a **no-PNL construction audit** following `TSMOM-DATA-0027`. It freezes the historical daily set of Binance USD-M perpetual contracts that may participate in a future time-series-momentum experiment.

## Status

**PASSED — daily point-in-time perpetual eligibility is reproducible from completed official archive data.**

GitHub Actions run `30960227098` completed successfully after one unit-test-only date-boundary correction that did not change the eligibility rule. The full archive construction then passed with zero symbol download failures.

## Frozen eligibility rule

A contract is eligible on completed date `t` only if:

1. an actual USD-M perpetual 1d archive row exists on `t`;
2. the most recent **240 calendar daily rows through t are all present**;
3. completed-day quote volume on `t` is at least **$25 million**;
4. the mechanical stable-base / leveraged-token-like exclusions from TSMOM-DATA-0027 do not apply.

The 240-day and $25m values are inherited from the project's already-frozen PIT-ALPHA / PIT-DISP universe discipline. They were not selected from TSMOM returns.

Any future strategy must use `t -> t+1` execution; the eligibility matrix contains completed-date information only.

## Coverage

| Item | Result |
|---|---:|
| Historical archive candidates | 828 |
| Usable symbol histories | **828 / 828** |
| Symbol failures | **0** |
| Data panel | 2020-09-01 through 2026-07-31 |
| Evaluation window | 2021-05-01 through 2026-07-31 |
| Evaluation days | **1,918** |
| Symbols ever eligible | **550** |
| Total eligible symbol-days | **143,523** |

Daily eligible-contract count:

- minimum: **26**;
- median: **72**;
- mean: **74.83**;
- maximum: **212**.

This is a sufficiently broad and highly time-varying universe; no fixed present-day panel is being imposed on history.

## Fixed-date snapshots

| Date | Eligible contracts |
|---|---:|
| 2022-01-01 | 70 |
| 2023-01-01 | 39 |
| 2024-01-01 | 84 |
| 2025-01-01 | 89 |
| 2026-01-01 | 63 |
| 2026-07-31 | 53 |

The membership changes materially through time, which further demonstrates why a fixed current universe would be inappropriate.

## Later-ended contracts retained historically

**19** contracts whose archive later ends at least two months before the latest 2026-07 archive nevertheless satisfied the frozen eligibility rule while they were actually tradable:

`AKROUSDT`, `ANTUSDT`, `AUDIOUSDT`, `BTSUSDT`, `BTTUSDT`, `BZRXUSDT`, `DODOUSDT`, `EOSUSDT`, `FOOTBALLUSDT`, `FRONTUSDT`, `GALUSDT`, `HNTUSDT`, `LUNAUSDT`, `MATICUSDT`, `RNDRUSDT`, `SRMUSDT`, `SXPUSDT`, `TOMOUSDT`, `YFIIUSDT`.

For example, the 2022-01-01 eligible set contains historically important names such as `LUNAUSDT`, `SRMUSDT`, `HNTUSDT`, `EOSUSDT` and `MATICUSDT`. A survivor-only backtest would erase exactly these contracts from the historical opportunity/risk set.

## Decision

1. Pass TSMOM-PIT-0028 and freeze this eligibility construction.
2. Do not retune 240 days or $25m based on later TSMOM performance.
3. A first TSMOM mechanism experiment is now authorized.
4. That experiment should reuse the project's already-existing per-asset 20/60/120/240 trend definition rather than introduce a new horizon family.
5. The first portfolio should be continuous time-series momentum across **all eligible contracts**, not Top-N winner selection, with inverse-volatility risk normalization and a fixed unit-gross sleeve.
6. Report standalone return quality and daily/monthly correlation to BRRK before any portfolio-stack optimization.
7. Funding and venue implementation remain separate mandatory gates before promotion.
