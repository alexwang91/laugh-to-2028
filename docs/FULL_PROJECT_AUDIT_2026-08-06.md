# BRRK Full Project Audit — 2026-08-06

Status: audit record for the canonical forward program

## Scope

This audit re-read the Master Plan, Implementation Roadmap, Project Governance, Context Continuity Protocol, CURRENT_STATE, NEXT_STEPS, product config, decision registry, instrument registry, merged material PR chain, current main, open PR state and the execution/router modules present on main.

The purpose is to verify that completed work still matches the original program before continuing beyond P2.3.

## Executive result

```text
PRODUCT / STRATEGY DRIFT: NONE
PRODUCTION AUTHORIZATION DRIFT: NONE
CURRENT PROCESS / HANDOFF DRIFT: DRIFT_1
CURRENT ROADMAP BLOCKER: P2.3 live L2 measurement correction
P2.4: BLOCKED until correction closes
```

`DRIFT_1` is process/implementation-detail only. No master-plan foundational assumption, live-risk boundary, security boundary or research objective changed.

## Completed roadmap chain reviewed

| Roadmap item | Primary implementation PR | Audit result |
| --- | ---: | --- |
| P0.1 / P0.2 | #40 | PASS / MERGED; canonical product config + decision registry present |
| P1.1 deterministic identity | #42 | PASS / MERGED; deterministic CLOID/replay suppression present |
| P1.2 persistent ledger | #44 | PASS / MERGED; durable intent/order/fill/reconciliation truth present |
| P1.3 partial-fill correctness | #46 | PASS / MERGED; actual-fill-driven transition present |
| P1.4 reversal safety | #48 | PASS / MERGED; fresh-flat gate before reversal open present |
| P1.5 precision / metadata | #50 | PASS / MERGED; metadata-driven formatting present |
| P1.6 post-submit reconciliation | #52 | PASS / MERGED; unexplained differences block risk increase while reductions remain available |
| P1.7 restart recovery | #54 | PASS / MERGED; cold-start recovery matrix and idempotence present |
| P1.8 kill / emergency paths | #56 | PASS / MERGED; independent emergency controls present |
| P2.1 instrument registry | #58 | PASS / MERGED; canonical BTC/ETH/SOL/BNB registry present |
| P2.2 spot identity validation | #60 | PASS / MERGED; UETH/USOL verified; BNB policy frozen perp-only |
| P2.3 cost model core arithmetic | #62 | MERGED with green CI, but full roadmap acceptance reopened by this audit because live L2 depth/VWAP was caller-supplied rather than canonically measured |

The corresponding post-merge handoff PRs through #61 were also reviewed. PR #63 attempted to normalize P2.3 to P2.4 but was closed without merge after the audit found the P2.3 measurement gap.

## Frozen product boundary audit

Verified unchanged:

- long universe = BTC / ETH / SOL / BNB;
- primary venue = Hyperliquid;
- initial live-validation capital = $2,000;
- recurring contribution ≈ $100/week, manual deposit only;
- canonical daily boundary = 00:00 UTC;
- intraday automation = risk reduction only;
- leverage = model determined; operating risk budget still unfrozen pending P4;
- 70% drawdown remains catastrophic tolerance only;
- FLAT = zero directional exposure;
- FLAT -> LONG / FLAT -> SHORT and first short of a new bear phase require human approval;
- bot uses trading Agent/API credentials only;
- master wallet private key, automated withdrawals and external transfers remain forbidden;
- production upgrades remain candidate/shadow + manual blue-green cutover;
- stopped carry / TSMOM / PIT-alpha lines were not silently rescued.

`production_authorized_components` remains empty.

## Router policy audit

Canonical current policy:

- BTC: verified spot candidate with perp fallback;
- ETH: verified UETH spot candidate with perp fallback;
- SOL: verified USOL spot candidate with perp fallback;
- BNB: `PERP_ONLY_DEFAULT` under decision `ROUTER-BNB-PERP-ONLY-2026-08-06`.

The original Master Plan §6 working-policy sentence for BNB still says to choose spot/perp by availability/cost. That sentence is stale relative to the later explicit product routing decision. This does **not** alter a foundational Master Plan assumption such as universe or venue; the later decision registry / instrument registry is the current authoritative BNB routing policy. Fresh sessions must treat the old BNB working-policy sentence as superseded unless the BNB decision is explicitly reopened.

## P2.3 acceptance audit

The merged #62 cost model correctly introduced:

- configurable spot/perp fees;
- spread and beyond-spread slippage fields;
- signed funding by holding horizon;
- basis/premium evolution;
- custody/redemption friction;
- capacity/VWAP diagnostic fields;
- same-asset/equal-notional/equal-horizon comparison;
- no P2.4 route decision.

However, #62 did not canonically derive `live_depth_usd` or `vwap_impact_bps` from a Hyperliquid `l2Book` snapshot. The roadmap explicitly requires live depth / VWAP. Therefore the audit reopens P2.3 only for a narrow measurement-completeness correction.

Required correction:

1. fetch canonical `l2Book` snapshots through the market layer;
2. derive bid/ask spread, target-notional buy/sell VWAP, beyond-half-spread impact and displayed two-sided USD depth;
3. treat inability to fill target quantity from Hyperliquid's returned book depth as a capacity/measurement failure rather than extrapolating unseen liquidity;
4. make Hyperliquid funding-rate decimal-to-bps/hour conversion explicit;
5. keep VWAP impact diagnostic separate from charged beyond-spread slippage to prevent double counting;
6. preserve BNB exclusion and do not implement P2.4.

## Process / governance findings

### 1. Historical branch hygiene

The repository still contains many historical merged/research branches. Governance §17 says merged branches should normally be deleted after unique evidence is archived on main. This is historical repository hygiene debt. Main + the current candidate remain the only production-truth sources.

Classification: `DRIFT_1`.

### 2. Direct-main documentation incident

A pure documentation commit (`c0bc7a6f5efe12fdc81e9bba8052a0523f91793e`, BNB perp-only policy note) was previously written directly to main instead of through the branch/PR guard. It changed no code, strategy economics, live risk or production authorization. Subsequent work returned to the required branch/PR process.

Classification: `DRIFT_1` process incident. Preserve the history; do not rewrite it away.

### 3. Premature P2.3 handoff

After #62 merged, PR #63 was opened to advance to P2.4. The full audit found the live L2 measurement gap before #63 merged. #63 was closed without merge so the dependency order remains enforceable.

Classification: correction prevented a `DRIFT_2` sequencing error from becoming canonical.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

Nothing in this audit or the P2.3 correction authorizes live capital, expanded leverage, new production assets, shorts, withdrawals, external transfers, or a production cutover.

## Exact continuation

```text
P2.3 live-L2 measurement correction
-> candidate tests / self-review
-> PR / CI
-> final-head evidence
-> merge
-> post-merge normalization
-> P2.4 Router decision
```

Do not start P2.4 until the correction PR is merged and the handoff explicitly closes P2.3.
