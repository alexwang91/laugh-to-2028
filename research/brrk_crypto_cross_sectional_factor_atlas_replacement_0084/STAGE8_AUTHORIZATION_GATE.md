# Stage8 Authorization Gate

Task: `BRRK-CRYPTO-CROSS-SECTIONAL-FACTOR-ATLAS-REPLACEMENT-0084`

Status: `BLOCKED_PENDING_EXPLICIT_USER_AUTHORIZATION`

Lifecycle position: Stage7 merged at `641ccf6bcd358c0255f65546bfcde1c06e861b51`; Stage8 authorization gate is active. Formal completion remains 7/10 until Stage8 completes.

Budgets before authorization and before marker:
- attempt: `0/1`
- controlled scientific-history reads: `0`
- scientific engine calls: `0/1`
- Stage8 scientific source-network fetches: `0`

The completed Stage7 preflight earned `PREFLIGHT_PASS_ZERO_RESULT` without reading nested scientific CSV member content or producing scientific results.

Stage8 may not create `RUN_ATTEMPT.marker`, read controlled history, invoke the scientific engine, or persist a scientific result bundle until fresh, exact-scope contemporaneous user authorization for 0084 is obtained and persisted.

After valid authorization, the only legal irreversible order is:
1. Re-establish live main and identity-only zero-result preflight facts.
2. Persist authorization state on this branch.
3. Create and remotely verify durable `RUN_ATTEMPT.marker`; this consumes attempt `1/1`.
4. Read each authorized historical object at most once under the frozen controlled-read budget.
5. Invoke the frozen scientific engine exactly once.
6. Keep scientific source-network fetches at zero.
7. Persist the create-only result bundle and seal with `RUN_ONCE.marker`.

After marker creation, no rerun, retune, rescue, source substitution, history extension, candidate replacement, or recomputation is permitted.

The authorization granted for 0073 does not transfer to 0084. No frozen-science rule changes in this gate.

Project drift: `DRIFT_0`.
