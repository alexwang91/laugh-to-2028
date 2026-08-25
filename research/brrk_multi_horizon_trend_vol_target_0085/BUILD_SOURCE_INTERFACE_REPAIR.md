# BRRK Multi-Horizon Trend Vol-Target 0085 — BUILD source-interface repair

Gate: `BUILD` mechanical repair before `ARM`.

Status: `SOURCE_INTERFACE_REPAIR_PENDING_EXACT_HEAD_CI`.

## Root cause

The merged BUILD implementation accepts pre-normalized `btc_daily.json`, `eth_daily.json`, and `sol_daily.json`. Live governance-visible controlled history is instead durably staged as Binance USD-M perpetual 1d monthly ZIP objects. Creating the normalized JSON objects before `RUN_ATTEMPT.marker` would require opening/decompressing controlled history before the marker, which is forbidden. ARM therefore must not bind fabricated/preprocessed JSON objects.

This repair adds a deterministic `ControlledArchiveTrendEngine` adapter. The qualified common runner first creates the durable attempt marker, performs its single verified outer payload read pass, and then invokes this engine exactly once. Inside that already-marked invocation the adapter opens each ARM-bound monthly kline ZIP once, relies on ZIP member read CRC validation, converts timestamp/close rows to the existing frozen JSON interface in memory, and delegates to the unchanged `run_from_sources` implementation.

Only the existing staged perpetual 1d kline family is accepted by this adapter. Funding-rate ZIPs and unknown paths fail closed. No network access or source discovery occurs.

## Qualification requirements

Synthetic tests must prove:

- exact staged path recognition for BTCUSDT/ETHUSDT/SOLUSDT perpetual 1d monthly ZIP objects;
- one inner CSV member per monthly ZIP;
- CRC/corrupt inner ZIP failure closes execution;
- month/date identity mismatch fails closed;
- duplicate/alias/unknown source identity fails closed;
- all three assets are required;
- deterministic conversion into the original `btc_daily.json` / `eth_daily.json` / `sol_daily.json` interface;
- the unchanged frozen Trend engine can execute on the converted synthetic support with no controlled history reads.

The common runner fault matrix and its >=20 consecutive synthetic lifecycle qualification remain authoritative and unchanged.

## What did not change

- No controlled scientific/history payload was opened, decompressed or parsed while making this repair.
- 0085 attempt remains `0/1`; controlled scientific/history reads remain `0`; scientific engine budget remains `0/1`; scientific source-network fetches remain `0`.
- The BTC/ETH/SOL universe, 20/60/120/240 horizons, 3-of-4 activation rule, trailing 20-session realized volatility, 25% portfolio-volatility target, gross cap 1.0, long/cash constraint, daily UTC timing and t-close -> t+1 causality remain unchanged.
- The 10/20/30 bps cost panels, support floor, benchmarks, diagnostics, PASS gates and terminal classifications remain unchanged.
- No result-informed tuning, source-value inspection, candidate selection, threshold rescue, history extension or scientific source substitution occurred.
- `CONTROLLED_RESEARCH_RUNNER_V1` marker-before-read, exactly-once, create-only and failure semantics remain unchanged.
- 0074 remains immutable `INVALID_EXECUTION`; 0076 remains sealed at 6/10 after its pre-marker read-boundary incident; 0072/0073 remain closed/paused; 0083 remains immutable FAIL.
- Production/signature/order/withdrawal/transfer authority remains false.

## ARM implication

ARM may proceed only after this repair reaches exact-head terminal-green CI and merges. ARM must then bind the exact staged perpetual-kline object identities, hashes, sizes and read budgets and must bind `ControlledArchiveTrendEngine` as the exact execution interface. ZERO-RESULT PREFLIGHT remains metadata-only. It may inspect central-directory metadata and declared manifest hashes/sizes, but it may not call `testzip()`, decompress an inner ZIP, open a CSV, parse a row, or otherwise expose controlled payload content before the durable marker.
