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
copy of a frozen strategy foundation is a hazard rather than evidence.

Dropping the duplicate is strictly an improvement here. The runner already puts
`research/core` on `sys.path`, so `import crypto_rotation_backtest` now resolves
to the canonical module and the file imports cleanly — verified. On its branch
the local copy would have shadowed it, because `HERE` is inserted last and
therefore searched first.

No CI job imports these files: the tsmom workflows name
`test_tsmom_alpha_0029.py` and `run_tsmom_alpha_0029_repaired.py` explicitly
rather than discovering modules.

## Deliberately not preserved

Their source branches also carried `.github/workflows/tsmom-0029.yml` and
`.github/workflows/tsmom-0027-pretest.yml`. Neither is preserved, and that is a
decision rather than an oversight.

Both trigger on `research/tsmom/**`. Carrying them into `main` would make every
future change under that directory re-run a superseded experiment — including
edits to this very file. CI wiring is not experiment evidence: discipline #3
preserves registrations and results, and both of those are above. The runners
can still be invoked by hand if anyone needs to inspect them.
