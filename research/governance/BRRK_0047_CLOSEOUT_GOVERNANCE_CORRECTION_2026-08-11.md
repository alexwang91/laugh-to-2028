# BRRK 0047 closeout governance correction — 2026-08-11

Status: **GOVERNANCE / EVIDENCE-IDENTITY CORRECTION ONLY — NO NEW RESEARCH EXECUTION**

This note records a repository-governance defect discovered while preparing the design-only `BRRK-LEADERSHIP-ROTATION-0048` architecture PR.

`BRRK-BETA-HANDOFF-EVENT-STUDY-0047` remains immutable:

```text
result_status                         FAIL_NO_RECURRENT_DURABLE_HANDOFF_STRUCTURE
target-eligible BTC-positive episodes 27
primary durable handoffs              12
prevalence                             12/27 = 44.4444%
ETH / SOL causes                       3 / 9
same-ID rerun                          false
same-ID retune                         false
same-ID rescue                         false
```

No 0047 scientific computation was rerun and no result/gate/method was changed.

## Defects corrected

1. `CLOSEOUT.json`, `RESULT.md`, and the standing closeout test contained three recovered-evidence hash identities that did not match the already-persisted authoritative `EVIDENCE_RECOVERY.json` and actual `PRIMARY_RESULT.json` bytes.
2. Two standing lifecycle tests still enforced the pre-result rule that result files must not exist, even though 0047 was already CLOSED and those immutable result files must now exist.
3. The stale write-enabled `.github/workflows/tmp-0047-closeout-finalize.yml` remained on `main` after closeout and was removed.

## Authoritative identities preserved

From the existing `research/brrk_beta_handoff_0047/EVIDENCE_RECOVERY.json`:

```text
PRIMARY_RESULT pre-serialization object SHA256
961ac99bd5a2d3d6556262b17411333bfbeead921616dccf120190ee1dd67c2a

PRIMARY_RESULT recovered raw JSON file SHA256
6c354b054bde2dfce12dbb1efe3809d59d371df02beddc613befe9373a17807d

PRIMARY_RESULT reparsed canonical SHA256
35f0ee3934d45e19b5b652fa13b0cfa1f328aac51843ac9432e8cc94d20dd6b8

EXECUTION pre-serialization object SHA256
a87e37ae41e20d71e61dd52fb0b20009a5a6c6ffeeb6d0eb3d6faab568604665

RUN_ONCE marker reconstructed object SHA256
9487c61867e9c2862d1d0a57396440382768c113596a280eff5fd0142c7efcc6
```

The pre-result `RUN_INTERFACE.json` is intentionally left unchanged as immutable pre-result evidence. Standing tests now preserve that historical contract while also requiring the CLOSED result/evidence files and continuing to forbid any same-ID hazard model, BOCPD rescue, portfolio implementation, rerun, retune, or production authority.

This correction has no bearing on the 0048 scientific architecture other than restoring repository governance consistency before 0048 proceeds.
