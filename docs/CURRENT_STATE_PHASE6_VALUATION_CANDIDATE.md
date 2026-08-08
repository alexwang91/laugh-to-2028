# Phase 6 valuation candidate handoff

This file is a scoped candidate note and does not replace `docs/CURRENT_STATE.md`.

Candidate branch: `phase-6/live-valuation-contract`.

Baseline main: `af8ff7c6ce3bf16dd81ab9f510393d38fc790b63`.

Candidate state:

```text
Phase-6 implementation/replay             PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY
live elapsed evidence                     MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
collector armed                           false
schedule configured                       false
elapsed evidence credit authorized        false
observation account identity frozen       false
valuation contract frozen                 true (candidate; authoritative only after merge)
durable evidence backend frozen           true
schedule/duplicate rule frozen            true
production/signature/order authority       false / false / false
```

Valuation V1 supports explicit Hyperliquid Standard (`userAbstraction=disabled`) mode only. It maps signed perp `positionValue` plus instrument-registry-verified UBTC/UETH/USOL spot mark-to-market into canonical BTC/ETH/SOL/BNB P3.3 notionals. Standard account equity is first-perp-dex `marginSummary.accountValue` plus spot USDC and allowed spot mark-to-market. Unsupported abstraction modes or unknown nonzero assets fail closed.

If this candidate merges, one exact verified read-only observation account identity is the only remaining pre-arm dependency. The later arm change remains separate and future-only.
