# 0076 Stage4 IMPLEMENTATION

Status: `COMPLETE_FROZEN_END_TO_END_INTERFACE / ZERO_CONTROLLED_HISTORY`.

Stage3 merge: `c0c587929af9fa71fab8ddb8a69d58ef03f36101`.

The Stage4 implementation intentionally exposes one scientific entrypoint only: `engine.run_scientific_engine(payloads, authorized_hashes, context=...)`. The caller performs no scientific transformation. After a future durable Stage8 marker, the caller may load each Stage6-authorized object byte sequence once and hand the complete byte map plus frozen SHA-256 map to this entrypoint.

The entrypoint itself verifies object authorization/hash/read accounting; parses the exact Binance USD-M monthly 1d-kline and fundingRate ZIP/CSV families; constructs the lagged point-in-time universe; computes the one MOM60 candidate; forms deterministic 20/20 long-short tails; computes lagged rolling beta and the exact dollar/beta-neutral projection; simulates fixed-position weekly perpetual PnL with archived funding and C0/C1/C2 transaction-cost semantics; calculates daily economics, block bootstrap, PSR/one-trial DSR, regime/year robustness, capacity and contribution concentration; evaluates G0-G11; returns exactly one terminal classification; and produces canonical create-only `PRIMARY_RESULT.json`, `EVIDENCE.json`, and `EXECUTION.json` bytes.

Unlike 0084, Stage8 does not need a new scientific harness, adapter, trial-construction layer, or terminal-classification layer. Stage5 must now prove that statement with nonhistorical synthetic PASS/FAIL/INCONCLUSIVE/INVALID fixtures. If Stage5 finds a mismatch with the already-frozen Stage3 contract, Stage4 implementation may be corrected only to match that frozen contract. Stage3 science cannot be retuned.

No controlled historical/scientific payload was opened in Stage4. No scientific engine was run on real history. No source-network scientific fetch occurred. Attempt remains `0/1`; controlled reads `0`; scientific engine `0/1`; Stage8 scientific source-network fetches `0`; no marker exists.
