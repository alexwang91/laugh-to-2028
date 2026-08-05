# TSMOM-ALPHA-0029 — first valid result

**Decision: REJECT the sleeve and stop same-window TSMOM tuning. Move the historical research queue to carry.**

The first valid result was produced by GitHub Actions run `30982562385`, successful re-run job `92232650543`, from frozen commit `62d3f02550a90518294214c0bd72298f842bfef8`. The earlier attempt on the same commit stopped only because one `NOTUSDT` funding archive request was reset by the remote peer; no strategy rule changed between attempts.

## Frozen design

- Historical Binance USD-M point-in-time perpetual universe from TSMOM-DATA-0027/0028.
- Eligibility: 240 contiguous completed daily bars and completed-day quote volume >= $25m; information at day `t` usable no earlier than `t+1`.
- Every eligible contract participates; no Top-K or cross-sectional ranking.
- Direction: sign of the existing project 20/60/120/240 `trend_score`.
- 30-day realized-vol inverse-vol weighting.
- Gross normalized to 1.0; natural net long/short exposure.
- 5 bps canonical transaction cost per absolute weight change, with 10/20 bps price-only stress.
- Official Binance USD-M historical funding events included.
- Funding timing: target from day `t` is effective at `t+1 00:00:01`; an exact 00:00 event belongs to the previous held day.

## Data integrity

### Perpetual price history

- candidates: 828
- nonempty histories: 828/828
- top-level download errors: 0
- monthly download errors: 0
- symbols ever PIT-eligible: 550
- symbols ever held: 549
- later-ended contracts ever held: 19

TSMOM-DATA-0029A detected 323 internal monthly-kline gaps. 318 were repaired only from the exact official Binance daily 1d file for the same UTC date. Five ICPUSDT dates remained unresolved, but after PIT eligibility was recomputed there were no held positions lacking an official next-day perpetual return, so the execution hard gate passed.

### Funding event coverage

- active symbols requiring funding histories: 549
- funding histories loaded: 549/549
- active symbol-days: 156,229
- active symbol-days with >=1 recorded event: 155,927
- active symbol-days without a recorded event: 302
- event coverage ratio: 99.8066940197%
- recorded funding events used: 553,743
- symbols with no-event days: 15

TSMOM-DATA-0029B treats funding as an event cashflow: only an official recorded settlement event creates PNL. An active symbol-day with no recorded event contributes no funding cashflow but remains an explicit coverage diagnostic. Missing archive files/download failures remain hard failures. This convention does **not** prove that every no-event date represented a true zero economic funding settlement; it is a residual historical-data uncertainty.

The missing subset was small by portfolio weight: mean absolute held weight per missing symbol-day was 1.1150%; on affected calendar days mean missing-subset long gross was 0.0623% and short gross was 1.5335%.

## Performance

| Variant | CAGR | MDD | Ann. vol | Sharpe | Calmar | Final $10k |
|---|---:|---:|---:|---:|---:|---:|
| Price-only, 5 bps | 7.4124% | -85.6114% | 62.8426% | 0.4336 | 0.0866 | $15,269.30 |
| Funding-aware, 5 bps | **-4.1187%** | **-88.3025%** | 62.4603% | 0.2509 | -0.0466 | **$7,797.02** |
| Price-only, 10 bps | 0.3814% | -89.4835% | 62.8470% | 0.3260 | 0.0043 | $10,227.92 |
| Price-only, 20 bps | -12.3341% | -94.3832% | 62.8575% | 0.1109 | -0.1307 | $4,587.77 |

Canonical funding-aware history is 2020-08-29 through 2026-07-30, 2,162 observations.

Funding additive attribution across recorded events:

- long positions: -43.4600%
- short positions: -23.4970%
- net: **-66.9570%**

The result is therefore not rescued by the short side receiving positive funding; across the realized path, recorded funding economics are materially adverse on both directional books in aggregate.

## Exposure diagnostics

- average long gross: 0.4626
- average short gross: 0.5374
- average net: -0.0748
- average active contracts: 72.25
- maximum active contracts: 211
- average maximum single-name absolute weight: 4.5233%
- maximum single-name absolute weight: 50.5622%
- turnover: 800.61 over the funding-aware evaluation path

## Diversification and crisis behavior versus BRRK

On common history versus canonical BRRK price-only:

- daily correlation: **0.0597**
- monthly correlation: 0.2052
- mean TSMOM return on BRRK worst 10% daily returns: **-0.5888% per day**
- compounded TSMOM return over those 133 tail days: **-59.32%**
- mean TSMOM return on BRRK worst 20 days: **-1.8428% per day**
- compounded TSMOM return over BRRK worst 20 days: **-33.68%**
- mean TSMOM return on BRRK worst-decile months: -0.1083%

Against the strict-router BRRK overlap, daily correlation is 0.0408 and monthly correlation is 0.2905. Low correlation is real, but it is not useful crisis alpha because the sleeve loses during BRRK's bad tail states as well.

## Preregistered qualification gates

| Gate | Result |
|---|---|
| funding-aware CAGR > 0 and Sharpe > 0 | **FAIL** |
| daily correlation with BRRK < 0.50 | PASS |
| mean TSMOM return on BRRK worst 10% days >= 0 | **FAIL** |
| authorize portfolio-stack experiment | **NO** |

## Stopping rule

Do not tune the 20/60/120/240 horizons, horizon weights, 30d vol window, universe age/liquidity thresholds, Top-K, gross, stop loss, funding threshold, SOL weight, or long/short balance on this historical sample to rescue TSMOM-ALPHA-0029.

Retain this as rejected evidence. The next independent historical sleeve research line is **carry**, with its own data audit and preregistration before any carry PNL is inspected.
