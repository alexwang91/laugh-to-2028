# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- Master plan: `docs/MASTER_PLAN_2026-08-05.md`
- Roadmap: `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`
- Governance: `docs/PROJECT_GOVERNANCE_2026-08-05.md`
- Continuity protocol: `docs/CONTEXT_CONTINUITY_PROTOCOL.md`
- P1.1 implementation PR #42 + handoff #43: PASS / MERGED
- P1.2 implementation PR #44 + handoff #45: PASS / MERGED
- P1.3 implementation PR #46 + handoff #47: PASS / MERGED
- P1.4 implementation PR #48 + handoff #49: PASS / MERGED
- Current main before P1.5: `41dbbcdbea26f5d811b4e60cc0d65fc0a247e4a4`
- P1.5 candidate branch: `p1-5/precision-metadata`

## Current roadmap position

```text
P0.1 Canonical product config: PASS / MERGED
P0.2 Decision registry: PASS / MERGED
P1.1 Deterministic order identity: PASS / MERGED
P1.2 Persistent order ledger: PASS / MERGED
P1.3 Partial-fill correctness: PASS / MERGED
P1.4 Reversal safety: PASS / MERGED
P1.5 Precision / metadata: CANDIDATE / NOT MERGED
P1.6+ blocked until P1.5 closes its evidence/merge gate
```

The only active implementation task is **P1.5 Precision / metadata**. Do not start P1.6, P2, P3, P4, P5 or P8 before P1.5 merges.

## Frozen product state

- Long universe: BTC / ETH / SOL / BNB.
- Initial managed capital: $2,000 cash/stablecoin.
- Recurring manual contribution: about $100/week.
- Primary venue: Hyperliquid.
- Official daily boundary: 00:00 UTC.
- Daily strategy decisions; intraday automation may only reduce risk.
- Leverage is model-determined; 70% drawdown is catastrophic tolerance only.
- FLAT = zero directional exposure; re-entry and first short activation require human approval.
- Bot uses trading Agent/API credentials only; no master wallet private key, automated withdrawals or external transfers.
- Strategy upgrades use candidate/shadow + manual blue-green cutover.
- BTC-only executor capability does not redefine the four-asset product universe.

## P1.1–P1.4 closure baseline

Registered engineering decisions retained:

- `EXEC-ORDER-ID-P1.1 = IMPLEMENTATION_VERIFIED`
- `EXEC-ORDER-LEDGER-P1.2 = IMPLEMENTATION_VERIFIED`
- `EXEC-PARTIAL-FILL-P1.3 = IMPLEMENTATION_VERIFIED`
- `EXEC-REVERSAL-SAFETY-P1.4 = IMPLEMENTATION_VERIFIED`

P1.4 final implementation head `879ce2da3b1e4382473037650c3fca30cda7f63f` passed Phase 0 baseline contract `31078243843`, execution tests, research integration, PR handoff governance `31078243847`, and evidence-only governance `31078303601`; PR #48 merged as `7acb093af59825c39fd092f232573666682197d8`, then PR #49 normalized the handoff as main `41dbbcdbea26f5d811b4e60cc0d65fc0a247e4a4`.

## P1.5 candidate behavior

Roadmap requirement: remove hardcoded size and price precision.

Candidate implementation:

- adds `beta_bot/instrument_metadata.py` as the canonical formatting layer;
- parses Hyperliquid perp `meta.universe` and reads each asset's `szDecimals`;
- executor fetches exchange metadata before any write action and fails closed when configured instrument metadata is absent/malformed;
- execution quantity is formatted conservatively toward zero using the exchange-provided `szDecimals` instead of a global `5` decimal constant;
- ledger order parameters persist `sz_decimals` and `precision_source=hyperliquid_meta`;
- price helper enforces metadata-derived decimal cap plus the Hyperliquid five-significant-figure rule, with integer-price allowance;
- formatting tests explicitly cover BTC, ETH, SOL and BNB with distinct metadata values;
- malformed, duplicate or incomplete metadata and sizes that round to zero fail closed;
- existing reversal executor tests now inject deterministic exchange metadata rather than relying on network access.

P1.5 does **not** authorize ETH/SOL/BNB production execution. Formatting correctness is separate from P2 instrument identity/routing and later production authorization.

## P1.5 self-review notes

- Size rounding uses `Decimal` and `ROUND_DOWN`, so formatting cannot increase requested economic risk through rounding up.
- Metadata is fetched before wallet/exchange order write actions, so missing metadata fails before economic submission.
- The executor no longer contains the previous `_round_size(..., decimals=5)` hardcoded precision helper.
- Price formatting is implemented even though the current market-open/close path does not submit explicit limit prices; this satisfies the roadmap precision contract without claiming a new order type.

## P1.5 evidence status

Candidate implementation is **not yet IMPLEMENTATION_VERIFIED and not merged**. Authoritative PR CI is required.

## Deliberately not solved

P1.5 does not claim:

- P1.6 full post-submit account reconciliation;
- P1.7 complete restart recovery;
- P1.8 kill/emergency paths;
- P2 route selection or spot identity completion;
- P3 production-quality daily BRRK target engine;
- P4 leverage research completion;
- P5 cycle-top research completion;
- multi-asset production readiness;
- production authorization.

## Frozen research boundaries

- Do not rescue stopped carry work.
- Do not rescue rejected TSMOM / failed historical alpha lines by retuning the same sample.
- Historical ASYM-BETA evidence is not leverage authorization.
- Spot identity cannot be inferred from PnL.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Latest project-drift assessment

```text
DRIFT_0
```

P1.5 is the exact next roadmap dependency and changes no product economics, risk philosophy, human-approval rule, security boundary, stopped research line or production authorization.

## Exact next action

```text
P1.5 PR -> CI -> fix same PR if required -> final-head CI -> decision registry -> merge -> normalize handoff to P1.6
```

Do not start P1.6 before P1.5 is PASS / MERGED.