# BRRK-LEADERSHIP-INTRADAY-SUPPORT-0053

Status: **PREREGISTERED / FIRST 4H DATASET CAPTURED AND HASH-FROZEN / SUPPORT NOT MEASURED / NO MODEL FIT / NO PREDICTIVE RESULT**.

0053 is a label-blind 4h support-feasibility study created after the immutable 0048 insufficient-support closeout. It measures whether 4h resolution creates genuine dependence-aware support under calendar-equivalent semantics or merely more correlated rows.

Governance objective type: **`DATA_QUALITY`**. Primary authority remains Track A only: 2190 eligible matured training origins, 2190 matured eligible shadow origins, 336-row dependence blocks, 12 complete blocks required. Track B (365/365/56) and Track C (365/365/336) remain diagnostics only.

No ETH/SOL winner label, model fit, calibration fit, NLL/AUC/Brier, confidence threshold or portfolio economics is permitted under this ID.

The original `api.binance.com` capture transport produced zero rows because a U.S. GitHub-hosted runner received HTTP 451. Before any data exposure, Capture Source Amendment 1 prospectively changed only the public market-data REST base to Binance's official `data-api.binance.vision`, preserving `/api/v3/klines` and every scientific/data-integrity parameter.

The first complete valid payload was then captured in GitHub Actions run `31512578577`, job `93849786583`:

- source: Binance Spot official market-data-only `/api/v3/klines`
- interval: 4h UTC
- common coverage: `2020-08-11T04:00:00Z` through `2026-08-02T20:00:00Z`
- common bars: `13097`
- BTC raw bars: `13098`
- ETH raw bars: `13098`
- SOL raw bars: `13097`
- canonical payload SHA256: `471b54991ae648b79433285f073ea7bc813663319b6e2389c1682dad1a319135`
- payload size: `7030655` bytes
- internal 4h gaps: `0`
- no synthetic fill / no alternate venue

`MARKET_4H_PAYLOAD.json`, `MARKET_4H_EVIDENCE.json`, and `DATASET_DECLARATION.json` are now the immutable first-successful-capture evidence. The dataset is researcher-exposed DEVELOPMENT history.

**No Track A/B/C support funnel was computed during capture.** No support classification exists yet. The next permitted stage is deterministic support-funnel implementation against this exact hash-frozen payload.
