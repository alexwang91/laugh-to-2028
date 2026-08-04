# TSMOM-DATA-0028 Result — Daily PIT Perpetual Eligibility

`TSMOM-DATA-0028-PIT-ELIGIBILITY` completed successfully in GitHub Actions run `30960195350`.

**Decision: PASS the daily point-in-time eligibility layer. No TSMOM strategy PNL was calculated in this audit.**

## Frozen eligibility rule

For every ordinary historical Binance USD-M USDT perpetual candidate identified by `TSMOM-DATA-0027`, completed UTC day `t` is eligible only when:

1. the contract has at least **240 contiguous completed daily bars** through `t`;
2. completed-day quote volume on `t` is at least **$25,000,000**;
3. the eligibility observation is usable no earlier than **t+1**.

The `240`-day age rule and `$25m` liquidity floor are reused unchanged from `PIT-DISP-0015`. They were not selected from TSMOM returns.

Missing calendar bars reset contiguous age. A contract naturally becomes ineligible after its archived daily history ends. Current survivor status and future delisting information are not inputs to historical eligibility.

## Coverage

- historical ordinary USDT perpetual candidates: **828**;
- symbol jobs returned: **828 / 828**;
- nonempty histories: **828 / 828**;
- top-level symbol errors: **0**;
- symbols with month download errors: **0**;
- month download errors: **0**;
- latest archive date observed: **2026-07-31**.

## PIT universe result

- contracts ever eligible: **550**;
- later-ended contracts that had previously been eligible: **19**;
- premature eligibility violations before 240 contiguous bars: **0**;
- first eligible date: **2020-08-27**;
- last eligible date: **2026-07-31**;
- eligible calendar days: **2,165**;
- median eligible contracts on nonzero days: **69**;
- maximum eligible contracts: **212** on **2024-12-03**.

Later-ended contracts that were historically eligible include:

`AKROUSDT`, `ANTUSDT`, `AUDIOUSDT`, `BTSUSDT`, `BTTUSDT`, `BZRXUSDT`, `DODOUSDT`, `EOSUSDT`, `FOOTBALLUSDT`, `FRONTUSDT`, `GALUSDT`, `HNTUSDT`, `LUNAUSDT`, `MATICUSDT`, `RNDRUSDT`, `SRMUSDT`, `SXPUSDT`, `TOMOUSDT`, `YFIIUSDT`.

This directly demonstrates that the TSMOM universe preserves historically shortable contracts that later disappeared; it does not substitute today's survivor set.

## Calendar snapshots

| Date | Eligible contracts |
|---|---:|
| 2021-01-01 | 16 |
| 2022-01-01 | 70 |
| 2023-01-01 | 39 |
| 2024-01-01 | 84 |
| 2025-01-01 | 89 |
| 2026-01-01 | 63 |
| 2026-07-31 | 53 |

## Validation

All preregistered success gates passed:

- candidate universe nonempty;
- at least 98% of symbol jobs returned (actual 100%);
- nontrivial eligible cross-section exists;
- at least one later-ended contract had been historically eligible (actual 19);
- no contract became eligible before 240 contiguous completed bars.

Deterministic unit tests also passed before the full archive audit.

## Research decision

The historical contract-existence and daily PIT eligibility gates are now both valid. The next experiment may define a **low-degree-of-freedom time-series momentum sleeve**.

The next signal experiment must preserve the following discipline:

- no Top-K or cross-sectional winner selection;
- no current-survivor substitution;
- no PNL-selected liquidity or age thresholds;
- use only completed information with `t -> t+1` execution;
- include actual historical perpetual funding in the implementation result;
- evaluate correlation and crisis behavior versus BRRK, not only standalone CAGR.

This audit itself contains no trend signal, position, return, Sharpe, CAGR or drawdown calculation.
