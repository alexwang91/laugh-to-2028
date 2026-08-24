# 0084 Stage6 — CONTROLLED EXECUTION BOUNDARY

Research ID: `BRRK-CRYPTO-CROSS-SECTIONAL-FACTOR-ATLAS-REPLACEMENT-0084`

Parent Stage5 merge: `61b7e3a45c82604520ea9f76c6878a2707481fc2`.

## Purpose

Stage6 freezes the exact controlled-execution boundary before any 0084 scientific payload value is opened. It earns no scientific result and consumes no controlled attempt.

## Frozen execution invariants

- controlled attempt remains `0/1` until a future Stage8 durable `RUN_ATTEMPT.marker` is created and remotely verified;
- each authorized historical object may be opened at most once in the unique Stage8 attempt;
- scientific engine call budget is exactly `1/1` at Stage8 and `0` before then;
- Stage8 scientific source-network fetch budget is exactly `0`;
- marker-before-read is mandatory;
- result persistence is create-only and must end with `RUN_ONCE.marker`;
- marker creation, controlled reads, scientific execution, result computation, retune, rescue, source substitution, history extension and candidate replacement are forbidden in Stage6.

## Frozen scientific identity

Stage6 binds the already-frozen Stage3/Stage4/Stage5 science without modification: point-in-time ordinary `*USDT` universe semantics; 16 factors; two representations; 5/20-session horizons; exactly 64 trials; MBB block 20 / 4000 replicates / seed 750075; family-wise Holm alpha 0.05; frozen robustness partitions; G0-G11; terminal-classification vocabulary.

## Controlled-source families

The only source families eligible for authorized-object enumeration are the frozen official Binance archive families already declared by Stage3:

1. Binance spot monthly 1d archives for point-in-time eligible `*USDT` symbols;
2. Binance USD-M perpetual monthly 1d archives for the same eligible symbol/month where available;
3. Binance USD-M funding-rate archives for the same eligible symbol/month where available.

Candidate months remain `2021-01` through `2026-07`. Any missing, extra, duplicate, checksum mismatch, payload-hash mismatch, malformed archive, identity ambiguity or source-family drift must fail closed.

## Stage6 completion gate

Stage6 is not complete merely because this contract exists. Before merge the branch must also persist, without exposing scientific payload values:

- exact point-in-time symbol-universe identity evidence;
- exact authorized-object manifest with role, object path, paired official checksum identity and payload SHA-256;
- exact per-object read budget (`<=1` at Stage8, `0` before Stage8);
- durable offline staging/readability evidence proving Stage8 requires no scientific source-network fetch;
- exact frozen execution-interface identities from merged Stage4/Stage5;
- proof that `RUN_ATTEMPT.marker`, result bundle and `RUN_ONCE.marker` are absent;
- CURRENT_STATE handoff with attempt/read/engine/network budgets all zero.

Stage6 and Stage7 must not extract or inspect scientific payload values. ZIP/archive integrity checks may validate byte identity and structural readability only.

## Next legal stage

Only after this Stage6 PR is complete, exact-head mandatory CI is terminal green, and the PR is expected-head merged may an independent Stage7 ZERO-RESULT PREFLIGHT begin. Stage7 must prove that the durable attempt marker is literally the only remaining action before the already-frozen callable can execute.
