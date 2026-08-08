# STABLECOIN-LIQUIDITY-0001

Status: `PREREGISTERED_NOT_RUN`  
Authority: research only; `production_authorized=false`

This directory is the prospectively owned formal path registered by `STABLECOIN-LIQUIDITY-0001` before path creation.

## Layering

```text
DefiLlama source
    ↓ exact HTTP bytes
raw vintage + manifest (immutable, SHA256)
    ↓ fail-closed parser
PIT-normalized atomic observations
    ↓ exact frozen transform
STABLECOIN_LIQUIDITY_STATE_V1
    ↓ later, separately frozen run interface
Stage-1 incremental-information test
```

This change implements only the **source/data/PIT boundary**. It does not execute the bottom two research layers.

## Files

- `DATA_CONTRACT.json` — frozen source identity, coverage rule, field/unit binding, PIT semantics, feature definition and explicit non-actions.
- `SOURCE_AUDIT.md` — source provenance and known PIT limitations.
- `source_defillama.py` — one-shot raw HTTP adapter; no parsing, retry search or result logic.
- `raw_vintage.py` — SHA256 + create-only local/CI reference storage and verification.
- `data_contract.py` — fail-closed schema parser and frozen coverage/PIT helpers.
- `test_data_contract.py` — synthetic offline regressions only; no live API call.

## Storage boundary

`raw_vintage/` is gitignored. Real recurring forward collection must use durable external create-only/versioned storage. The local filesystem writer is only the reference semantics used by CI and development; it is not durable production storage authority.

## No-result boundary

Until a later, separately controlled step explicitly performs the first historical capture:

- `config/dataset_exposure_registry.json` remains without a Stablecoin slice;
- no real Stablecoin feature series exists in-repo;
- no Stage-1 model or prediction is produced;
- no research result or Edge Registry entry exists;
- no BRRK or production authority changes.
