# Superseded TSMOM artifacts

Preserved under discipline #3 ("先登记、后运行，失败版本必须保留") when the working
branches that held them were deleted. Same treatment as the unused
`research/carry/CARRY-RF-0036.json` preregistration.

**None of these produced a committed result, and none may be cited as evidence.**

| Artifact | Status | Superseded by |
|---|---|---|
| `TSMOM-0029-FIRST-MECHANISM.json` | `PREREGISTERED_BEFORE_FIRST_RUN` — never run | `TSMOM-ALPHA-0029.json` |
| `run_tsmom_0029_first_mechanism.py` | runner for the above | `run_tsmom_alpha_0029.py` |
| `test_tsmom_0029_first_mechanism.py` | its deterministic tests | `test_tsmom_alpha_0029.py` |
| `run_tsmom_0027_pretest.py` | pretest runner, no registered result | `run_tsmom_perp_universe_audit.py` under `TSMOM-DATA-0027-PIT-PERP-UNIVERSE.json` |

The TSMOM line that did run is `TSMOM-ALPHA-0029`, and it was **rejected**:
CAGR -4.12%, MDD -88.30%. See
[`research/results/TSMOM_ALPHA_0029_RESULT_2026-08-05.md`](../results/TSMOM_ALPHA_0029_RESULT_2026-08-05.md).
No rescue of that line is authorized.

`run_tsmom_0029_first_mechanism.py` also shipped a local copy of
`crypto_rotation_backtest.py` on its branch. That copy is **not** preserved — the
canonical module is `research/core/crypto_rotation_backtest.py`, and a duplicated
copy of a frozen strategy foundation is a hazard rather than evidence. The
superseded runner is kept for the record and is not expected to import cleanly.
