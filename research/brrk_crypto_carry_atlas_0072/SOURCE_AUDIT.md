# 0072 source capability audit

Status: `GOVERNANCE/DATA IDENTITY PRECONDITION / NO CONTROLLED HISTORY READ / NO LIFECYCLE CREDIT`

Research ID: `BRRK-CRYPTO-CARRY-ATLAS-0072`

DESIGN merge: `90a7b68718c5cb59002fe4b451d39d8979602161`

Audit date: 2026-08-18

Controlled scientific/history payload reads: `0`

Attempt: `0/1`

## Purpose

This audit records source-interface facts used to freeze `SOURCE_IDENTITY_CONTRACT.json`. It does not fetch a market endpoint, open historical source payload, calculate a carry feature, choose a result-informed window or release a scientific result.

## Binance official public interfaces

The official Binance public-data project documents downloadable Spot and Futures archives under `data.binance.vision`, including USD-M/COIN-M futures index-price, mark-price and premium-index klines, and publishes companion checksum objects for archive integrity. The official USD-M Futures market API exposes funding-rate history, exchange information, trade-price klines, mark-price klines and index-price klines.

The source contract therefore permits Binance only for the explicitly enumerated archive families and REST paths. Archive revision risk is handled by immutable raw-vintage identity; a later upstream replacement cannot silently replace a captured object.

Binance's documented COIN-M basis endpoint states that only the latest 30 days are available. That endpoint is not admitted as a historical atlas source in V1 because it cannot establish the long chronological history required by 0072 without a prospectively collected vintage series.

## Bybit official public interfaces

The official Bybit V5 market API documents historical funding rates for linear/inverse perpetual products and an open-interest endpoint with explicit timestamp pagination. Bybit states that open-interest queries may reach the symbol launch time. Its market API also documents price/mark/index/instrument interfaces used only under the exact paths frozen in the source contract.

The source contract therefore uses Bybit as the prospective cross-venue funding and OI source, subject to actual capture support and point-in-time qualification. Present-day instrument metadata alone cannot prove historical-effective metadata; failure to prove historical semantics fails the affected family closed.

## Conditional families

Liquidation intensity remains unqualified because V1 does not yet identify a lawful point-in-time historical public source that satisfies the DESIGN boundary. It cannot be substituted with another family.

The optional tenth family is narrowed to a price-trend representation derived only from already admitted point-in-time prices. An external attention proxy remains unqualified.

Dated-futures basis and term structure remain conditional on the first capture proving instrument and price-history support with defensible historical metadata. Absence of support produces insufficient-family support; it does not authorize a source swap after exposure.

## Capture boundary

The repository precedent from `STABLECOIN-LIQUIDITY-0001` freezes a source/data/PIT contract and a one-shot first-capture gate before first immutable historical capture. That gate uses exact raw-byte persistence, manifest/hash verification, metadata-only output, no automatic network retry and manual reconciliation after partial artifacts. 0072 adopts the same governance pattern without importing Stablecoin scientific semantics.

No live 0072 capture occurs in this audit. Full Stage 3 PREREGISTRATION remains incomplete until truthful captured identities exist and the complete numerical/scientific contract binds them.

## Authority

`production_authorized=false`

`signature_authorized=false`

`order_submission_authorized=false`
