# STABLECOIN-LIQUIDITY-0001

Status: `PREREGISTERED_NOT_RUN`  
Authority: research only; `production_authorized=false`

This directory is the prospectively owned formal path registered by `STABLECOIN-LIQUIDITY-0001` before path creation.

## Layering

```text
DefiLlama source
    ↓ exact HTTP bytes
first-capture gate
    ↓ persist before interpretation
raw vintage + manifest (immutable, SHA256)
    ↓ verify persisted bytes
fail-closed parser
    ↓
PIT-normalized atomic observations
    ↓ exact frozen transform
STABLECOIN_LIQUIDITY_STATE_V1
    ↓ later, separately frozen run interface
Stage-1 incremental-information test
```

The source/data/PIT contract and the first-capture gate are implemented, but the first real historical capture has **not** been executed. No result-bearing research layer is active.

## Files

- `DATA_CONTRACT.json` — frozen source identity, coverage rule, field/unit binding, PIT semantics, feature definition and explicit non-actions.
- `CAPTURE_GATE.json` — frozen one-shot first-history capture sequence, metadata-only output and registry/manifest ownership boundary.
- `SOURCE_AUDIT.md` — source provenance and known PIT limitations.
- `source_defillama.py` — one-shot raw HTTP adapter; no parsing, retry search or result logic.
- `raw_vintage.py` — SHA256 + create-only local/CI reference storage and verification.
- `data_contract.py` — fail-closed schema parser and frozen coverage/PIT helpers.
- `capture_once.py` — only allowed first-history orchestration: fetch once → persist raw/manifest → verify → parse persisted bytes → emit metadata only.
- `test_data_contract.py` / `test_capture_gate.py` — synthetic offline regressions only; no live API call.

## Storage boundary

`raw_vintage/` is gitignored. Real first capture and recurring forward collection must use durable external create-only/versioned storage. `capture_once.py` rejects a storage root inside the repository and requires explicit live-execution and durable-storage attestation flags. The filesystem writer enforces deterministic create-only reference semantics; the operator remains responsible for selecting an actually durable external mount/object-store-backed location.

If any first-capture artifact already exists under the selected storage root, the gate refuses another network fetch until manual reconciliation. A schema-invalid response is preserved as raw + manifest evidence and is not silently replaced by a second fetch.

## Registry / manifest boundary

`config/dataset_exposure_registry.json` owns the stable dataset-slice identity (`dataset_version`, source, fields, start/end, transformation, PIT semantics, budget/contamination state). It does **not** have a `raw_hash` property under governance-v1 schema.

Exact raw SHA256, byte length, retrieval timestamp, response headers, raw object location and parser version remain manifest/provenance properties. A later Dataset Registry entry may reference that immutable provenance through allowed evidence references; it must not add an unregistered `raw_hash` field.

## No-result boundary

Until a later, separately controlled step explicitly performs the first historical capture:

- `config/dataset_exposure_registry.json` remains without a Stablecoin slice;
- no real Stablecoin feature series exists in-repo;
- no Stage-1 model or prediction is produced;
- no research result or Edge Registry entry exists;
- no BRRK or production authority changes.
