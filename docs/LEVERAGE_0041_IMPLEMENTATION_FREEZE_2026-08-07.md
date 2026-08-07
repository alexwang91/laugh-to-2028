# LEVERAGE-0041 implementation freeze — 2026-08-07

Status: **FROZEN BEFORE FIRST ECONOMIC RUN**

## Authority

- experiment: `LEVERAGE-0041`
- preregistration: merged by PR #93
- implementation base main: `baaa5776892411990734ef2121cf54a5dbbab047`
- owner authorization: preregistration merge, implementation, pre-run validation, and the one-time research run are authorized as one continuous research workflow
- production leverage authorization remains separate under P4.6
- `production_authorized_components = []`
- production gross cap remains `1.0`

The RUN_ONCE marker remains a technical one-shot/audit control. It is **not** an additional permission prompt.

## Frozen implementation

Requested economic target:

```text
requested_target(cap) = frozen_raw_BRRK0011_target * cap
```

Cap `1.00` must exactly reproduce the frozen raw BRRK-0011 requested-target path before any cap > 1 result is valid.

Candidate caps:

```text
1.00 / 1.05 / 1.10 / 1.15 / 1.20 / 1.25 / 1.30
```

`1.20` remains a focal point only and receives no favorable selection treatment.

Architecture: `SPOT_FIRST_BASE_PLUS_PERP_OVERLAY_V1`

- explicit cash/cross-margin collateral reserve: 25% NAV;
- maximum spot financing: 75% NAV;
- BTC / ETH / SOL base long exposure is spot-first subject to the pinned P2.4 route evidence and capacity;
- BNB is perp-only;
- residual base exposure and incremental exposure are perp;
- actual routed perp notionals, not gross economic exposure, enter liquidation accounting;
- spot notional is neither perp notional nor additional cross-margin collateral;
- no external collateral is assumed.

## Funding reducer

Trailing evidence: seven complete daily sessions = 168 hours.

```text
debit <= 5 bps/day        incremental overlay scale = 1
5 < debit < 10            linear scale 1 -> 0
debit >= 10               incremental overlay scale = 0
missing/incomplete data   incremental overlay scale = 0
```

Funding logic may only reduce incremental exposure. It cannot create alpha, change direction, alter relative asset weights, or increase exposure.

Native funding is charged only to actual routed perp notional where the required Hyperliquid funding evidence is complete. Funding-spike scenarios magnify debit only.

## Survival / robustness

Frozen hard boundaries:

- defensive scenario CVaR/CDaR budget: 20%;
- operating DD candidates: 35/40/45/50%;
- catastrophic drawdown boundary: 70%;
- one-day uniform gap stress through -50%;
- liquidation distance: strictly greater than 55%;
- degraded depth/fill tests remain mandatory;
- start-date robustness remains mandatory;
- stationary bootstrap blocks: 7/21/63 days;
- resamples: 10,000;
- seed: `20260807`.

For liquidation, reference equity is $2,000 and modeled cross-margin collateral is exactly $500 (25%). An already-liquidatable starting state is distance zero and fails closed.

## Selection

A selected cap must be an interior member of a contiguous all-PASS neighborhood of at least three caps, with both immediate neighbors passing every hard gate.

Within a qualifying region, maximize matched after-cost CAGR. If candidates are within 1.0 percentage point annualized CAGR, choose the lower cap.

A research selection is not production authorization. The cap presented to P4.6 would be the next lower preregistered grid point and may not exceed 1.20.

## One-time execution

Frozen marker:

`research/leverage_0041/RUN_ONCE_LEVERAGE_0041.marker`

SHA256:

`55f06b1549593e847b42ae71c2e82d4c4a23931bdbfc671a6af9d05859e16ca5`

After implementation/preflight CI is green, the already-authorized marker may be committed without another owner prompt. Candidate economics may be evaluated once. Economic parameters may not be changed after candidate computation begins.

Only non-economic implementation defects may be corrected through a separately recorded recovery chain. No cap, threshold, route architecture, collateral fraction, funding rule, stress, seed, hard gate or selection rule may be changed to rescue a result.
