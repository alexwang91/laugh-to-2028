# TSMOM-DATA-0027 Result — Historical USD-M Perpetual Universe Is Recoverable

`TSMOM-DATA-0027-PIT-PERP-UNIVERSE` is a **no-PNL data audit** required before any crypto time-series-momentum long/short research.

## Status

**PASSED — historical contract-existence layer is reproducible from Binance Public Data archives.**

GitHub Actions run `30959742172` completed successfully. Unit tests, archive enumeration and all per-symbol 1d archive probes passed with zero per-symbol listing errors.

## Official archive evidence

Archive roots:

- `data/futures/um/monthly/klines/`
- `data/futures/um/monthly/fundingRate/`

Latest observed archive month: **2026-07**.

Counts:

| Item | Count |
|---|---:|
| All archived USD-M symbol prefixes | 986 |
| Archived USDT symbols | 832 |
| Ordinary USDT perpetual candidates after stable/leveraged-token exclusions | **828** |
| Ordinary candidates with resolvable 1d monthly archives | **828 / 828** |
| Ordinary candidates with funding archive prefix | **828 / 828** |
| Per-symbol archive-listing errors | **0** |
| Contracts whose last 1d archive is >=2 months before latest archive month | **29** |

The current Binance futures `exchangeInfo` endpoints were not usable from the Actions environment (`451` / invalid responses), so the audit does **not** claim a current-API-confirmed archive-only count. That limitation does not affect the historical archive-existence result.

## Historical contracts that ended well before the current archive

The 29 ordinary USDT contracts whose 1d archive ends at least two months before 2026-07 include:

`1000BTTCUSDT`, `AKROUSDT`, `ANCUSDT`, `ANTUSDT`, `AUDIOUSDT`, `BDXNUSDT`, `BLUEBIRDUSDT`, `BTSUSDT`, `BTTUSDT`, `BZRXUSDT`, `COCOSUSDT`, `DODOUSDT`, `DOTECOUSDT`, `EOSUSDT`, `FOOTBALLUSDT`, `FRONTUSDT`, `GALUSDT`, `HNTUSDT`, `KEEPUSDT`, `LENDUSDT`, `LUNAUSDT`, `MATICUSDT`, `MBLUSDT`, `NUUSDT`, `RNDRUSDT`, `SRMUSDT`, `SXPUSDT`, `TOMOUSDT`, `YFIIUSDT`.

Examples:

- `1000BTTCUSDT`: 2022-01 through 2022-04 only;
- `LUNAUSDT`: historical contract archive ends long before the current archive;
- `SRMUSDT`, `HNTUSDT`, `EOSUSDT`, `MATICUSDT`, `RNDRUSDT`: all appear in the historical perpetual archive even though their archive history terminates before the latest month.

This is sufficient to demonstrate why today's surviving perpetual list cannot be substituted for the historical shortable universe.

## Research implication

A future TSMOM test must reconstruct **point-in-time perpetual existence** from the archive itself. It must not:

- start from today's surviving symbols;
- infer perpetual shortability from spot listing;
- silently exclude later-delisted contracts;
- fill unavailable historical contracts from another venue based on later performance.

The archive also provides a funding-series prefix for every one of the 828 ordinary candidates, so later funding-aware accounting can use the same historical contract set rather than a survivor-only subset.

## Decision

1. Pass `TSMOM-DATA-0027` as the historical contract-existence layer.
2. Do not calculate TSMOM PNL yet.
3. The next authorized gate is a **daily PIT eligibility construction audit** using completed information only: actual contract archive availability/age and completed-day liquidity.
4. Reuse existing project eligibility discipline where possible instead of inventing a new universe after seeing returns.
5. Only after daily PIT eligibility is frozen may a separate preregistered TSMOM signal/portfolio experiment be run.
6. Funding, fees, slippage and correlation with BRRK remain separate validation gates after the gross time-series-momentum mechanism is established.
