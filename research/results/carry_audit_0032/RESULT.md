# CARRY-AUDIT-0032 — basis outlier source attribution

Decision: **PASS**. The extreme SOL/XRP daily-close basis observations that triggered this post-hoc audit are reproducible across the official Binance monthly and exact daily archives. No source mismatch or missing daily cross-check was found. The frozen CARRY-PNL-0031 result is unchanged and may proceed to a separately preregistered BRRK+carry stack test.

## SOLUSDT

- Largest absolute basis: **-16.903% on 2022-11-09**.
- Other |basis| >= 2% dates: 2021-01-06 and 2022-11-08.
- 37 selected/prior-day cross-check dates were examined; **0 unavailable**, **0 source mismatches** at relative tolerance 1e-10.
- Frozen 0031 full-window additive SOL price-spread contribution was **-1.704%**.
- The top 20 absolute-basis dates contributed **+1.490%** additive; the >=2% dates contributed **+1.236%**.

Thus the extreme basis dates did not create the negative full-window SOL spread result; they offset part of the loss accumulated on other dates.

## XRPUSDT

- Largest absolute basis: **-6.689% on 2020-12-11**; this was the only |basis| >= 2% date.
- 33 selected/prior-day cross-check dates were examined; **0 unavailable**, **0 source mismatches**.
- Frozen 0031 full-window additive XRP price-spread contribution was **-0.203%**.
- The top 20 absolute-basis dates contributed **+0.594%** additive; the >=2% date contributed **+0.612%**.

Again, the outlier is source-consistent and is not the cause of the negative full-window spread contribution.

## Authority limit

This audit was registered after observing 0031's basis extrema and is data-validation evidence only. No day was removed, no value was winsorized, no asset was excluded, and 0031 was not recomputed with a filtered history.
