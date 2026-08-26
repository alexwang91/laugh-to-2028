# BRRK Factor Long/Short 0088 — BUILD

Research ID: `BRRK-FACTOR-LS-0088`
Gate: `BUILD`
Controlled attempt: `0/1`
Controlled reads: `0`
Scientific engine calls: `0/1`

## Implemented frozen mechanics

This BUILD implements only synthetic/nonhistorical qualification for the merged 0088 SPEC and its pre-exposure invalid-week clarification.

- immutable 0086 signs remain `MOM60_RAW=-1`, `RVOL20_RAW=-1`, `LIQ30_RAW=+1`;
- target portfolios must remain gross `2.0`, net `0.0`, max absolute weight `<=0.15`;
- turnover is exact `sum |w_t-w_t-1|`;
- C0/C1/C2 use 0/10/20 bps per traded-notional turnover;
- funding enters weekly PnL separately from price PnL;
- capacity uses decision-time trailing-30 median quote volume and reference NAV 1,000,000 USDT;
- unsupported Mondays create no observation, mechanically remove a preceding observation when its transition cannot be truthfully accounted, reset state to zero, and force the next admissible week to pay full entry turnover;
- support admission never inspects realized portfolio return;
- inference uses 8-week moving-block bootstrap, 10,000 replicates, seed `880088`;
- G0-G9 and PASS/FAIL/INCONCLUSIVE classifications match the frozen SPEC.

## Synthetic qualification

`research/governance/test_0088_factor_ls_build.py` covers adequate-support PASS, insufficient-support INCONCLUSIVE, missing-capacity fail-closed support handling, consecutive unsupported weeks, preceding-observation removal, zero-state restart semantics, and return-blind admission.

The BUILD intentionally does not bind or parse controlled historical sources. `FactorLS0088Engine.execute()` fails closed until ARM supplies a source-qualified controlled adapter.

## ARM frontier

ARM must bind exact USD-M price and funding object identities, hashes/sizes, source keys, schema/timestamp contract, expected read budget, result/marker paths, source-qualified runner interface, and engine budget. Pre-marker payload parsing, decompression, `testzip()`, and CRC traversal remain forbidden.

## What did not change

- 0088 remains attempt `0/1`, controlled reads `0`, engine `0/1`, with no scientific result.
- 0086 remains immutable `PASS_VALIDATED_FACTOR_ATLAS` and its three passing signs remain fixed.
- 0076 remains sealed at its Stage7 pre-marker read-boundary incident.
- 0085 remains immutable `INVALID_EXECUTION`, attempt `1/1` consumed.
- 0072/0073 remain paused; 0083 remains immutable FAIL.
- Phase6 closeout, common-runner qualification, prospective five-gate lifecycle, and all immutable capture/workflow anchors remain unchanged.
- No production, signing, order, withdrawal, or transfer authority is granted.
