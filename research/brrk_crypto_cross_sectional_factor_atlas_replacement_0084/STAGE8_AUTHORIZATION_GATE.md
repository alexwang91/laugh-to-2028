# Stage8 Authorization Gate

Task: `BRRK-CRYPTO-CROSS-SECTIONAL-FACTOR-ATLAS-REPLACEMENT-0084`

Status: `AUTHORIZED_TO_PROCEED / ATTEMPT 0/1 / PRE-MARKER`

Lifecycle position: Stage7 merged at `641ccf6bcd358c0255f65546bfcde1c06e861b51`; Stage8 authorization gate merged at `d449475350a38df75c3a08bffc626beeff0ebc9d`; Stage8 controlled-attempt branch is `research/0084-stage8-controlled-attempt-v1`. Formal completion remains 7/10 until Stage8 completes.

Contemporaneous authorization:
- user explicitly authorized the 0084 Stage8 controlled attempt on 2026-08-24 in the current conversation;
- scope is exactly `BRRK-CRYPTO-CROSS-SECTIONAL-FACTOR-ATLAS-REPLACEMENT-0084` Stage8 controlled execution;
- this authorization does not relax frozen science, exactly-once, marker-before-read, no-result-informed-rescue, source-substitution, history-extension, candidate-replacement, or recomputation prohibitions;
- production, signing, trading, and order authority remain unchanged and absent.

Budgets before marker:
- attempt: `0/1`
- controlled scientific-history reads: `0`
- scientific engine calls: `0/1`
- Stage8 scientific source-network fetches: `0`

Fresh identity-only recheck after authorization:
- live main: `d449475350a38df75c3a08bffc626beeff0ebc9d`;
- Stage7 classification remains `PREFLIGHT_PASS_ZERO_RESULT`;
- bound artifact id/name: `9495175701` / `0075-stage6-authorized-payloads-v1`;
- artifact digest remains `sha256:8040282ff412b2d3fd360173e4745ebfd048796eb9e9c2ad49fa0901e5cedf56`;
- artifact is present and unexpired at the recheck;
- no nested scientific CSV member content was opened during this recheck;
- controlled scientific-history reads remain `0` and scientific engine calls remain `0/1`.

The only legal irreversible order from this state is:
1. Remotely verify this authorization-persistence commit on the Stage8 execution branch.
2. Create and remotely verify durable `RUN_ATTEMPT.marker`; this consumes attempt `1/1`.
3. Read each authorized historical object at most once under the frozen controlled-read budget.
4. Invoke the frozen scientific engine exactly once.
5. Keep scientific source-network fetches at zero.
6. Persist the create-only result bundle and seal with `RUN_ONCE.marker`.

After marker creation, no rerun, retune, rescue, source substitution, history extension, candidate replacement, or recomputation is permitted.

Project drift: `DRIFT_0`.
