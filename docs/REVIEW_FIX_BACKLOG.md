# Review fix backlog

Actionable worklist derived from [`CODE_REVIEW_2026-08-04.md`](CODE_REVIEW_2026-08-04.md) and
[`CODE_REVIEW_FOLLOWUP_2026-08-05.md`](CODE_REVIEW_FOLLOWUP_2026-08-05.md).

Every item below states the file, the defect, and the intended end state. Items are ordered by
priority. **Nothing in this backlog authorizes a parameter search, a threshold change, or a new
trading target.** Items marked **[REGISTER]** change what a strategy does or what a gate accepts
and therefore need a new preregistered experiment ID before they run; everything else is
accounting, documentation, infrastructure or execution hardening.

Rule that applies to the whole list: **do not retune anything after seeing a result.** If a fix
changes a published number, record both the old and the new number and leave the old report in
place (discipline #3).

---

## Status index

Added 2026-08-06. Until then this list carried no completion tracking at all: 14 of 28 items were
finished across PRs #31/#34/#36/#37 but were textually indistinguishable from the ones nobody had
started, so "what is actually left?" could only be answered by reading git history. Update the row
when you close an item.

| # | Item | Status |
|---|---|---|
| F1 | Carry re-priced against risk-free | **Done** — PR #31, `carry_rf_0036r1/r2`; carry line stopped |
| F2 | CARRY-PM measurement integrity | **Done** — PR #31, superseded by `CARRY-PM-0037` (not run; carry stopped) |
| F3 | README headline window is 3.65y | **Done** — PR #34 |
| F4 | README funding-aware comparison in one table | **Done** — PR #34 |
| F5 | gross-1.42 vs "leverage last" contradiction | **Done** — PR #36 |
| F6 | README `capital_factor` clamp | **Moot** — the formula text no longer exists after the PR #34 rewrite |
| F7 | One metrics implementation | **Done** — PR #36, `research/common/metrics.py`. See F27's correction note: the module was then misused once, which is now pinned by a test |
| F8 | Reports/logs silently gitignored | **Done** — PR #36, PIT-ALPHA-0018 evidence recovered |
| F9 | Daily series for every PNL experiment | **Partly done** — PR #36 covered asym_beta_0021/0022/0024 + audit_0023/0025/0026. **`tsmom_data_0027` / `tsmom_pit_0028` still missing**, and must follow the diff-first protocol below |
| F10 | Shared statistical inference | **Done** — PR #36, `research/stats/inference.py`. Step 2 (emit PSR/CI into *every* `summary.json`) is **not** done; it is applied where claims are made, not universally |
| F11 | Workflow permissions | **Done** — PR #36, plus the artifact-path fix in `54e8db5` |
| F12 | Weighted covariance bias | **Closed, not fixed** — PR #37; measured at 0.15-0.94% variance understatement, immaterial |
| F13 | One drawdown implementation | **Done** — PR #36 |
| F14 | Dead forward-return leakage path | **Done** — PR #36 |
| F15 | Order idempotency | **Open** — `execution/` untouched in 107 commits |
| F16 | Partial fills treated as complete | **Open** |
| F17 | Non-atomic reversal, silent alert | **Open** |
| F18 | Size precision / rounding | **Open** |
| F19 | "No trade" vs "target unreachable" | **Open** |
| F20 | `api/cron.py` authorization | **Open** |
| F21 | Delete `ALLOW_STRONG_BETA` | **Open** — branch still present in `beta_bot/config.py` |
| F22 | Research/execution price + timing parity | **Open** |
| F23 | Funding filter scope **[REGISTER]** | **Open — highest-value remaining research item** |
| F24 | Dispersion estimator scale-invariance **[REGISTER]** | **Open, low priority** — verified not on the BRRK-0011 baseline path |
| F25 | Delisting stress in 0018 | **Deferred** by its own terms — PIT-ALPHA line stopped |
| F26 | PIT fetch error tolerance | **Open, low priority** — same reason as F24 |
| F27 | Risk-free rate / idle cash | **Measured** — PR #37 + correction 2026-08-06. Standing wiring into the four `metrics()` functions **not** done |
| F28 | Impact-cost term | **Open** — revisit as deployed size grows |

---

## P0 — before CARRY-PM-0035 spends live capital

### F1. Re-price CARRY-PNL-0031 and CARRY-STACK-0033 against the risk-free rate **[REGISTER]**

**Files:** `research/carry/run_carry_pnl_0031.py`, `research/carry/run_carry_stack_0033.py`,
`research/carry/CARRY-PNL-0031.json`

**Defect.** CARRY-PNL-0031 is delta-neutral, gross 1.0, fully collateralized. Its
`net_economics` qualification gate tests net return against **zero**. For a book that is itself a
synthetic cash instrument the hurdle must be cash. Over its own window (2020-09-15..2026-07-30)
the sleeve returns 2.740% CAGR against 3.165% for 3-month T-bills — $11,720 vs $12,007 on $10k,
an excess Sharpe of **-0.223** against the reported +1.428. 2021 alone contributed +16.80% of the
+17.20% cumulative; excluding 2021 the sleeve returned +0.34% over ~4.9 years, and post-2021 it
trails cash by 4.17 pp/yr.

**Do.**
1. Register a new experiment ID (e.g. `CARRY-RF-0036-RISK-FREE-HURDLE`) that changes **only** the
   benchmark, not the strategy. Freeze the rate source before running.
2. Add a daily risk-free series (FRED `DTB3` or SOFR) and report, alongside the existing metrics:
   `excess_cagr_over_rf`, `excess_sharpe_over_rf`, and an annual carry-vs-cash table.
3. Redefine the `net_economics` gate as `excess return over rf > 0` and re-evaluate 0031 and 0033
   under it. Report the pass/fail; do not adjust the gate afterwards.
4. If 0031 fails the corrected gate, stop the carry line under discipline #7 and mark
   CARRY-PM-0035 as not required. Do not attempt an asset/threshold/window rescue.

**Reference implementation:** `research/review_2026_08_04/verify_carry_vs_cash.py` reproduces the
figures above from committed JSON plus FRED.

**Do not:** drop BNB, filter by funding sign, add a basis threshold, or restrict the window. 0031's
own stopping rule already forbids these.

### F2. Make CARRY-PM-0035 unable to pass on a failed measurement

**File:** `research/carry/run_carry_pm_0035.py` (`compare_snapshots`, around lines 306-311)

**Defect.** `incremental_maintenance = max(0.0, raw_available_change)` means
`incremental_fraction == 0.0`, and therefore PASS, in three distinct situations: PM genuinely
released margin, PM consumed exactly zero, and **the measurement was corrupted by price drift
between the two snapshots**. The four snapshots are collected by four independent CLI invocations
with no bound on elapsed time or mark-price movement, while
`tokenToAvailableAfterMaintenance` depends on mark price. On a $500 probe a 2% BTC move is ~$10,
the same order as the quantity being measured. The existing
`spot_quantity_preserved_to_matched` check only catches "you bought more spot".

Note the `max(0, ...)` itself matches `CARRY-PM-0035.json`, so the code does not violate the
freeze — the gate design is what is wrong.

**Do.** All required fields are already captured (`observed_at_utc`, `market.ubtc_spot_mid`,
`market.btc_perp_mid`); only the checks are missing.
1. Add `snapshot_gap_within_bound`: elapsed time between the `spot` and `matched` snapshots below
   a bound frozen before the run.
2. Add `mid_drift_within_bound`: `abs(mid_matched / mid_spot - 1)` below a bound frozen before
   the run.
3. Report `raw_available_after_maintenance_change_usdc` as a first-class outcome and split the
   result into three explicit states instead of one clamped number:
   `PM_RELEASES_MARGIN` (raw change negative and drift checks pass),
   `PM_CONSUMES_MARGIN` (raw change positive), and
   `MEASUREMENT_INCONCLUSIVE` (drift checks fail).
4. Because this changes a frozen gate, supersede `CARRY-PM-0035.json` with a new preregistration
   rather than editing it in place. **[REGISTER]**

Also: give `post_info` bounded retries (six sequential calls currently have none, while the
research code retries), and document the `MAX_PROBE_NOTIONAL_USD * 1.05` 5% tolerance in the
README as well as the runbook.

**Keep as is:** the script is genuinely read-only (info endpoint only, no signing, SHA-256
address fingerprint), and `carry-pm-0035.yml` correctly isolates the secret behind
`if: github.event_name == 'workflow_dispatch'`.

---

## P1 — statements that currently mislead a reader

### F3. README: the headline window is 3.65 years, not "full historical result"

**File:** `README.md`, section "Canonical BRRK economics"

**Defect.** The table is labelled `Price-only **full historical result**`. Those numbers come from
`research/results/pit_disp_0015/validated_summary.json`, which records
`"start": "2022-12-10", "end": "2026-08-02"` — 3.65 years, against a panel starting 2020-08-11.
The same gross≤1 V1 construction started 2021-05-01 gives 36.44% CAGR / -59.72% MDD / Calmar
0.61 versus the published 61.31% / -37.63% / 1.63. The window itself is legitimate (it is set by
`min_train_days = 600`); the label is not.

**Do.**
1. Relabel to `Price-only result, 2022-12-10 .. 2026-08-02 (BRRK walk-forward OOS window)`.
2. Add a second row for V1 baseline over the full panel (2020-08-11 onward), which needs no
   walk-forward warm-up.
3. State once that all headline risk metrics describe a single crypto cycle beginning three weeks
   after the 2022-11-21 low.

**Reference:** `research/review_2026_08_04/verify_start_date_sensitivity.py`.

### F4. README: put the funding-aware comparison in one table

**File:** `README.md`, tables "Canonical strategy / implementation status" and
"Canonical BRRK economics"

**Defect.** Sharpe is leverage-invariant, and on the funding-aware basis discipline #6 calls
authoritative, ASYM-BETA-0024 scores **below** BRRK-0011 core on every risk-adjusted measure:

| funding-aware (strict router) | CAGR | MDD | Sharpe | Calmar |
|---|---:|---:|---:|---:|
| BRRK0011_CORE | 56.20% | -34.95% | **1.2286** | **1.6082** |
| ASYM_BETA_0024_DAILY_CAP | 64.82% | -41.44% | **1.1990** | **1.5644** |

So levering BRRK-0011 core to any target risk dominates ASYM-BETA-0024 after funding; the extra
sleeve converts a lower Sharpe into a higher CAGR. 0024's own attribution has it losing 5.8pp
more in 2024-04 (-25.67% vs -19.87%) and 2.3pp more in 2024-06 (-10.04% vs -7.73%). The README
currently quotes 0024's Sharpe 1.199 in one table and the core's 1.229 in another, so a reader
cannot see the comparison.

**Do.**
1. Merge into one funding-aware table with core and 0024 side by side, including Sharpe, Calmar
   and MDD.
2. Restate 0024's row to match its own `"promotion_evidence": false` and
   `"status": "LATENCY_FIX_VALIDATED_NOT_SHADOW_QUALIFIED"`. "机制有效 / 参数冻结；forward
   shadow only" currently reads as a pass.
3. Add the leverage-invariance note so the next extra-beta experiment is judged on Sharpe/Calmar
   rather than CAGR.

**Do not** re-run or retune 0021/0022/0024. This is a presentation fix.

### F5. Resolve the gross-1.42 vs "leverage remains last" contradiction

**Files:** `research/asym_beta/run_asym_beta_0024.py:46`, `README.md`, `docs/NEXT_STEPS.md`

**Defect.** `GROSS_CAP = 1.50` and `summary.json` records `max_final_held_gross = 1.4228`, versus
`research_gross_cap = 1.30` in `research/regime_kelly/config.py`. The previous README's P4 said
"Do not reopen 1.30–1.50 beta until funding-aware routing, reconciliation, slippage controls and
kill switches have forward evidence"; the current README still says "leverage remains last". None
of reconciliation, slippage veto or kill switch exists — `execution/` is unchanged.

**Do.** Pick one and make the repo consistent:
- either state explicitly that research above 1.30 gross is permitted while **deployment** stays
  capped until the execution gates exist, and say where the 1.30 research cap now lives; or
- reduce `GROSS_CAP` to 1.30 and re-run 0024 under a new experiment ID **[REGISTER]**.

Do not leave both claims in the README.

### F6. README: `capital_factor` formula is missing the clamp

**File:** `README.md`, section "P0 — CARRY-PM-0035"

The README writes `incremental_maintenance_consumption_usdc = available(spot) - available(matched)`
while both `CARRY-PM-0035.json` and the code use `max(0, ...)`. Align the README to the
preregistration. (If F2 lands first, align it to the three-state outcome instead.)

### F7. One metrics implementation for BRRK0011

**Files:** `research/results/pit_disp_0015/validated_summary.json` (0.6510389) vs
`research/results/asym_beta_0024/summary.json` (0.6516610)

Same `final_10k` (62247.3823), two CAGRs, because one uses `len(returns)/365.25` and the other
uses the calendar span. 0.07pp, no effect on conclusions, but "canonical" should have one value.
Pick the calendar-span definition, put it in one shared helper, and note the restatement.

---

## P2 — evidence infrastructure

### F8. Stop silently dropping experiment reports and logs

**Files:** `.gitignore`, `.github/workflows/pit-alpha-0018.yml`

**Defect.** `.gitignore` contains `*_report.json` and `*.log`. The 0018 workflow persists results
with `git add "$DEST"`, so `pit_alpha_0018_report.json` and `pit_alpha_0018.log` were **silently
discarded**. `research/results/pit_alpha_0018/` has neither, while `pit_alpha_0016`,
`audit_0017_pit_alpha_attribution` and `funding_pnl_0003` both. The README's 0018 conclusion has
no retained primary evidence, which violates discipline #3.

**Do.**
1. Narrow the ignore rules so they cover working directories only, e.g.
   ```gitignore
   research/**/*_outputs/**/*_report.json
   *.log
   !research/results/**/*.log
   ```
2. Re-run `pit-alpha-0018.yml` (or recover from the workflow artifact, retention permitting) and
   commit `pit_alpha_0018_report.json` and `pit_alpha_0018.log`.
3. If the numbers no longer reproduce exactly, commit the new report **and** record the delta;
   do not adjust anything to make them match.

### F9. Commit a daily series for every experiment that produces PNL

**Files:** `research/results/asym_beta_0021|0022|0024/`, `audit_0023_latency/`,
`audit_0025_april_trend/`, `audit_0026_semantic_risk/`, `tsmom_data_0027/`, `tsmom_pit_0028/`

These directories contain only `summary.json`. Because `pit_disp_0015/daily_equity.csv` exists,
the BRRK-0011 vs V1 claim could be tested independently (0.9948 correlation, Sharpe difference
95% CI [-0.046, +0.164]). The ASYM-BETA-0024 claim of a 0.030 Sharpe gap **cannot** be tested the
same way — the data is not committed.

**Do.** Have each PNL-producing runner write `daily_equity.csv` (one column per strategy) into its
results directory, and backfill for 0021/0022/0024. BRRK's equivalent is ~100KB for 1332 rows.

**Backfilled 2026-08-05, with a finding that changes how any future backfill must be done.**
`run_asym_beta_0021/0022/0024.py` and `run_audit_0023_latency.py` already wrote daily-granularity
CSVs (`daily_returns.csv`, `decisions.csv`, etc.) into their `OUTPUT` directory, which points
directly at the committed `research/results/<name>/` path — the code was never the problem, only
`summary.json` had been committed while the CSVs sitting right next to it were not.

Re-running each script to backfill those CSVs also **overwrites `summary.json` in place**, and
every one of these scripts hardcodes `"status": "FIRST_RUN_COMPLETE"` as a placeholder — the
committed `summary.json` files' real `status` (e.g. `REJECTED_STRUCTURALLY_INERT`,
`MECHANISM_VALIDATED_NOT_SHADOW_QUALIFIED`), their `decision` text, and fields like
`dominant_drawdown` are **hand-added after the run**, not reproduced by the script. A naive
backfill would have silently reverted a recorded rejection back to a placeholder and deleted the
decision reasoning. Every rerun was diffed field-by-field against the committed `summary.json`
first: all *numeric* metrics matched to float precision (confirming no code drift since the
original run), only the hand-annotated fields differed, and only the new CSV files were staged —
`summary.json` was restored to its committed version in every case. Anyone doing this for
`tsmom_data_0027`/`tsmom_pit_0028` (not yet backfilled) must repeat that diff, not just re-run and
commit.

`audit_0026_semantic_risk` backfilled the same way, but its rerun surfaced a second, distinct
failure mode worth flagging separately: `run_audit_0026_semantic_risk.py`'s output schema has
genuinely grown since `summary.json` was committed (it now also emits `top_interval_increases`,
a `forward_by_descriptive_level` breakdown at the 0.25/0.75 thresholds in addition to 0.5, row
counts, and calendar bounds) — this is not just the placeholder-status pattern above, the script
itself now computes and reports more than it did at commit time. Every field that exists in
*both* versions was checked and matches (the `0.5`-threshold forward-return triple is
bit-identical; the handful of probability values differ only at the 11th-12th significant digit,
consistent with summation-order floating-point noise in the HMM/VB fit, e.g.
`1.6974310402923218e-41` vs `1.6974310402860743e-41`). Per the same rule, the richer output was
**not** merged into the committed record — `summary.json` was restored verbatim and only the two
genuinely new files (`daily_semantic_risk.csv`, `interval_summary.csv`) were staged. Promoting the
richer schema into the committed `summary.json` would be a legitimate follow-up, but it changes a
published file's structure and belongs in its own reviewed change, not silently bundled into a
CSV backfill.

### F10. Add shared statistical inference and wire it into every report

**New file:** `research/stats/inference.py`

**Defect.** No experiment reports confidence on its headline comparison. On 3.65 years, MinTRL to
assert annualised Sharpe > 1.0 at 95% is **20.97 years** for BRRK-0011 and 30.10 years for V1.
PSR(SR\*=0) is 99.57%, so "Sharpe > 0" is solid — the *level* and the *ranking between variants*
are not. BRRK-0011 vs V1: daily correlation 0.9948, Sharpe difference +0.058 with 95% CI
[-0.046, +0.164], Calmar difference CI [-0.164, +0.599]; neither excludes zero.

**Do.**
1. Implement PSR, DSR, MinTRL (Bailey & López de Prado 2014) and a paired bootstrap for Sharpe
   and Calmar differences.
2. Emit `psr`, `mintrl_years`, and for any A/B comparison a bootstrap CI, into every experiment
   `summary.json`.
3. Make discipline #7 executable: a promotion claim of the form "X beats Y" must carry a CI that
   excludes zero.

`research/review_2026_08_04/verify_psr_dsr_mintrl.py` is a working starting point.

### F11. Converge the remaining workflow permissions

**Files:** `.github/workflows/funding-data-0001.yml`, `funding-crossvenue-0002.yml`,
`funding-pnl-0003.yml`, `pit-alpha-0018.yml`, `pit-disp-0015.yml`

These five still declare `permissions: contents: write` on a `pull_request` trigger that checks
out `github.event.pull_request.head.sha` and runs PR code, so a write-scoped token is live in a
step executing untrusted code. The 13 newer workflows already use `contents: read`.

**Do.** Split each into a `contents: read` job that runs the research and a separate persist job
(`workflow_run`, or `push` on the branch) that holds the write scope — matching the newer
convention.

### F12. Weighted covariance is biased low — relocated, checked, immaterial

**Originally:** `research/regime_kelly/daily_distribution.py:37`. That function
(`fit_daily_conditional_distribution`) was deleted as dead code by F14 — it had zero callers, so
this exact line no longer exists anywhere.

**But the same defect class is live elsewhere.** The active scenario engine moved to
`research/hybrid_meta/walkforward_v1_meta.py::fit_state_v1_distribution` (a scalar V1-return
version, not a full covariance matrix), and it has the identical gap at line 162:
```python
var_raw = float(np.sum(((arr - mu_raw) ** 2) * w))   # missing * n_eff / (n_eff - 1)
n_eff = float(1.0 / np.sum(w ** 2))                   # computed right below, unused for this
```
This function is not a side line — `run_dispersion_overlay.py::build_brrk0011_scale` calls it
directly, feeding `sample_v1_paths` → `choose_scale_corrected`, which produces the actual
`brrk_scale` time series that `BRRK0011_BASELINE = v1_raw.mul(brrk_scale, axis=0)` uses. It is on
the critical path of the canonical, currently-recommended BRRK-0011 number.

**Checked 2026-08-05, before doing anything: how big is it?** `n_eff` at the state level depends
on how concentrated the posterior state-membership weights are, not on the training-window length
directly. A read-only diagnostic (fit the real variational regime model at 8 decision dates spread
across the full 2022-12-10..2026-08-02 walk-forward, sample every semantic state) found `n_eff`
consistently in the **200-665** range, giving a bias-correction factor `n_eff/(n_eff-1)` of
**1.0015 to 1.0094** — i.e. the missing correction understates variance by **0.15%-0.94%**, mean
0.39%, across all 32 (date, state) samples. That is two orders of magnitude smaller than the
effects this repo already treats as immaterial (e.g. F7's 0.07pp CAGR convention gap), and far
inside the noise of a Monte Carlo scale choice.

**Decision: not doing this.** Per the standing rule (a fix only earns a registered rerun if it has
a plausible chance of changing a trading-relevant number), a <1% variance correction is not worth
the [REGISTER] overhead of a new experiment ID and a full re-run. Closing without a code change.
Reopen only if `fit_state_v1_distribution` is ever changed to condition on a much narrower/more
concentrated posterior (small `n_eff`), where this correction would start to matter.

### F13. One drawdown implementation

**Files:** `research/hybrid_meta/walkforward_v1_meta.py:194`,
`research/regime_kelly/daily_distribution.py:174`

Both compute `peaks = np.maximum.accumulate(nav, axis=1)` without prepending the decision-time
wealth of 1.0, so a first-day loss is invisible to the path drawdown.
`research/risk_metric_fix/corrected_risk.py` fixes this and is already used by
`run_dispersion_overlay.py` and the 0021/0022/0024 line — the canonical path is correct. The
uncorrected version remains reachable from `walkforward_v1_meta.py`, an executable entry point.

**Do.** Have `walkforward_v1_meta.py` import from `corrected_risk`, delete the local duplicate,
and add a header note that BRRK-MVP-0005's historical numbers came from the uncorrected version
(see `BRRK_0011_CDAR_CORRECTION`). Delete `portfolio_path_cdar95` in `daily_distribution.py` — it
has no callers.

### F14. Delete the dead forward-return leakage path

**Files:** `research/regime_kelly/regime_model.py` (`fit_regime_model`, `_semantic_mapping`),
`research/regime_kelly/features.py` (`forward_log_returns`),
`research/regime_kelly/config.py:13-14`

`_semantic_mapping` labels HMM states using 20-day forward returns; if the caller passes forward
returns reaching the end of the training window, the last 20 rows use out-of-window prices.
`purge_days = 20` and `embargo_days = 5` exist to prevent exactly this and are **never referenced
anywhere in the repo**. The active path (`regime_model_vb_nd.semantic_mapping_no_dominance`) uses
contemporaneous features only, so the leak is latent, not live.

**Do.** Delete `fit_regime_model`, `fit_daily_conditional_distribution`, `forward_log_returns` and
`portfolio_path_cdar95` (all callerless), and remove `purge_days`/`embargo_days` from the config.
A declared-but-unused safety setting reads as protection that is in force. If any is kept, add an
assertion that the caller has already purged.

---

## P3 — execution hardening (unchanged since the first review; research now runs at 1.42x gross)

**Triage note, 2026-08-05.** Explicitly not touched in this pass, and why: F15/F16/F17 (order
idempotency, partial-fill detection, non-atomic reversal with a silent-alert gap) are real
capital-safety risk — the "avoid liquidation on top of CAGR" side of the priority the strategy
work is supposed to serve — but `execution/plan-b-bot` is live-money-moving code with an unclear
deploy trigger (possibly auto-deploy on push to `main`), so pushing changes here is a materially
different kind of action than a research/measurement PR and deserves its own explicit round rather
than being folded into a backlog sweep. F18-F21 are lower-severity execution polish. F23 (funding
filter scope) is [REGISTER] research work, not hardening, and is high-value given FUNDING-PNL-0003
already measured -25.19%/-13.40% additive drag concentrated exactly where the current filter is
blind — it is the strongest remaining candidate for the next *research* round. None of F15-F23 are
abandoned; they are sequenced behind getting explicit sign-off on touching the execution layer.

### F15. Order idempotency — highest single operational risk

**Files:** `execution/plan-b-bot/beta_bot/executor.py`, `api/cron.py`, `vercel.json`

No `cloid`, no persisted order state, no dedupe. `vercel.json` sets `maxDuration: 60`. If an order
is accepted but the HTTP response times out, the next cron reads a possibly stale `current_qty`
and **resubmits**.

**Do.** Generate a deterministic `cloid` per intended target, persist submitted-order state
outside the function invocation, and refuse to submit when an in-flight order for the same target
exists.

### F16. Partial fills are treated as complete

**File:** `execution/plan-b-bot/beta_bot/executor.py:25` (`_extract_status`)

Only `statuses[0]` is inspected, and any `filled` is reported as success. Hyperliquid market IOC
orders return a `totalSz` that can be below the request.

**Do.** Compare `totalSz` against the requested size, inspect every status, re-read
`clearinghouseState` after submission, and surface a residual-gap result instead of `"filled"`.

### F17. Reversal is non-atomic and fails silently

**File:** `execution/plan-b-bot/beta_bot/executor.py:84-93`; `beta_bot/service.py`

The reversal path calls `market_close` then `market_open`. If the second call raises, the
exception propagates and `send_telegram(...)` at the end of `run_strategy` **never executes** —
the account is left flat with no alert.

**Do.** Wrap the run in `try/finally` so the notification always fires, and report a distinct
`half_executed_reversal` state carrying both legs' outcomes.

### F18. Size precision and rounding

**File:** `execution/plan-b-bot/beta_bot/executor.py:12` (`_round_size`)

`decimals: int = 5` is hardcoded rather than read from `meta`'s `szDecimals`, and Python's
`round()` is banker's rounding, which can round **up** and exceed available margin at maximum
size.

**Do.** Read `szDecimals` from `metaAndAssetCtxs` and truncate toward zero for reduce orders.

### F19. Distinguish "no trade needed" from "target unreachable"

**File:** `execution/plan-b-bot/beta_bot/portfolio.py` (`build_portfolio_plan`)

When the `max_platform_leverage * equity` clamp binds, `delta_notional` collapses toward zero and
the plan reports `rebalance_reason = "below_min_trade"`. The system says "nothing to do" when it
means "target is unreachable".

**Do.** Add a `target_clamped_by_leverage` flag, a separate reason string, and an alert.

### F20. `api/cron.py` authorization

**File:** `execution/plan-b-bot/api/cron.py:12,16`

`auth == f"Bearer {settings.cron_secret}"` is a non-constant-time comparison. Worse, absent a
secret, shadow-mode authorization is `headers.get("User-Agent") == "vercel-cron/1.0"` — a
caller-controlled header. Anyone can invoke `/api/cron` and read `nav_usd`,
`hyperliquid_equity_usd`, `current_perp_qty` and `external_spot_btc_qty`, and trigger a Telegram
push.

**Do.** Make `CRON_SECRET` unconditionally required (fail closed in `Settings.validate`), use
`hmac.compare_digest`, drop the User-Agent branch, and stop returning `str(exc)` to the caller.

### F21. Delete the unbacktested `ALLOW_STRONG_BETA` branch

**File:** `execution/plan-b-bot/beta_bot/model.py:84-85`

`strong_trend = trend_score >= 0.70 and realized_vol_30 <= 0.45` raising the cap to 1.50 has **no
counterpart in `research/core/crypto_rotation_backtest.py`**. It is off by default but
env-toggleable.

**Do.** Remove the branch and the `ALLOW_STRONG_BETA` / `HARD_BETA_CAP` settings until a
registered experiment supports them. (Coordinate with F5.)

### F22. Research/execution price-source and timing parity

**Files:** `execution/plan-b-bot/beta_bot/market.py`, `vercel.json`

Two independent mismatches:
- the backtest signal is computed on **Binance spot** daily closes; the bot computes it on
  **Hyperliquid perp** `candleSnapshot`. The frozen trend score is not source-invariant.
- `vercel.json` cron is `10 1 * * *` = **01:10 UTC**, while the backtest assumes execution at the
  00:00 UTC boundary — ~70 minutes of unmodelled daily lag, roughly 0.9% of price uncertainty at
  4% daily vol.

**Do.**
1. During shadow, log the target beta computed from **both** sources every day and track the
   difference as a first-class metric. If the distribution is material, redefine the frozen signal
   on the source execution actually uses **[REGISTER]**.
2. Move the cron to just after 00:0x UTC, or model the lag explicitly in the backtest.

### F23. Scope the funding filter to where the drag actually is **[REGISTER]**

**File:** `execution/plan-b-bot/beta_bot/model.py:91` (`apply_funding_filter`)

```python
if raw_beta <= 1.0 or funding_apr <= 0.10:
    return raw_beta, "none"
```

The filter only acts above beta 1.0. FUNDING-PNL-0003 measured BTC at **-25.19%** and SOL at
**-13.40%** additive funding contribution over the common window, and the strategy sits between
0.18 and 1.0 gross for most of it — the measured drag is almost entirely in the range the filter
cannot reach. The 0.10 / 0.15 / 0.25 APR thresholds have no backtest or registered experiment
behind them.

**Do.** Register an experiment that defines the funding response over the whole beta range using
expected rather than trailing-24h funding, and note that Hyperliquid's funding clamps saturate in
stress (see Zhang 2026 in the literature review). Do not tune the existing thresholds.

---

## P3b — methodology, needs registration

**Triage note, 2026-08-05.** Traced whether F24/F26 actually touch the canonical, currently-
recommended number before prioritizing them: `run_dynamic_dispersion.py::main` builds
`BRRK0011_BASELINE = v1_raw.mul(brrk_scale, axis=0)` from `build_brrk0011_scale` alone —
`dynamic_dispersion()` (F24's target) only feeds the separate `*_DISP0015` overlay candidates
(`V1_PLUS_DYNAMIC_UNIVERSE_DISP0015`, `BRRK0011_PLUS_DYNAMIC_UNIVERSE_DISP0015`), which the
script's own `decision` field already says are not promoted. Confirmed by reading the code, not
assumed. Same for F26 (PIT fetch error tolerance) as it applies to that dynamic-universe fetch —
the fixed V1/BRRK-0011 core (BTC/ETH/SOL/BNB) does not depend on the wider dynamic panel resolving
cleanly. Both stay correctly low-priority: real defects, but currently isolated to a
not-yet-promoted research line, not the baseline the README recommends. F25 is explicitly
deferred by its own text ("if the PIT-ALPHA line stays stopped, do this when it is next touched").
F28 (impact cost / capacity) matters more as deployed size grows; revisit if that changes.

### F24. Make the dispersion estimator scale-invariant **[REGISTER]**

**File:** `research/pit_universe/run_dynamic_dispersion.py` (`dynamic_dispersion`)

The fixed-panel and dynamic-universe dispersion scales correlate **0.064** — two implementations
of one concept that disagree almost completely. The eligible cross-section runs from 4 to 143
names, with yearly medians 8 → 20 → 39 → 30 → 15, and `dynamic_dispersion` averages 0.245 against
the fixed panel's 0.087. A cross-sectional standard deviation over a universe that quintuples in
size is not comparable across time; the signal tracks universe composition, not risk.

**Do.** Choose one and register it: a fixed cross-section size (top N by quote volume), a
size-invariant statistic (cross-sectional MAD ratio, or an n-bias correction), or per-name
volatility standardisation before taking cross-sectional dispersion.

### F25. Restore delisting stress in 0018

**File:** `research/pit_universe/run_entry_rank_eligibility_exit.py` (`evaluate_stateful`)

`run_dynamic_alpha.evaluate_array` has a `missing_haircut` parameter and stresses 0 / -25% / -50%.
`evaluate_stateful` dropped it, and `np.nan_to_num(returns, nan=0.0)` means a delisted asset is
held at 0% and exited at par — delisting is free. Published crypto estimates put equal-weighted
delisting bias at up to ~62% annualised.

**Do.** Restore the parameter, and extend the ladder to -100%. If the PIT-ALPHA line stays
stopped, do this when it is next touched rather than reopening it now.

### F26. Zero-tolerance on PIT fetch errors

**File:** `research/pit_universe/run_dynamic_alpha.py:311`

`if len(errors) > max(10, int(0.05 * len(symbols)))` silently tolerates ~32 dropped symbols. The
symbols most likely to fail are the ones most likely to have gone to zero, so the attrition is
selective and favourable. `run_entry_rank_eligibility_exit.py` already uses `if errors: raise`.

**Do.** Match the stricter behaviour, and persist the failed-symbol list in the report either way.

### F27. Model the risk-free rate and idle cash consistently — measured, restated numbers below

**Files:** `research/core/crypto_rotation_backtest.py` (`metrics`),
`research/pit_universe/run_dynamic_alpha.py` (`metrics`),
`research/hybrid_meta/walkforward_v1_meta.py` (`metrics`),
`research/funding_router/run_frozen_holdings_funding_pnl.py` (`metrics`)

Every Sharpe uses rf = 0, and idle cash earns nothing. Mean idle cash over the 2022-12-10 window
was estimated at **20.5%**, with a preliminary estimate that crediting 4.5% would raise CAGR by
~1.5pp while *lowering* excess Sharpe from 1.295 to 1.215.

**Do.** Credit unused cash at the daily risk-free rate and report Sharpe on excess returns. Share
the rate series with F1. Report restated numbers next to the originals.

**Two constraints carried over from the F1 implementation** (see
[`RISK_FREE_METRIC_CONVENTIONS.md`](RISK_FREE_METRIC_CONVENTIONS.md)):

- Use `load_fred_daily_risk_free_investment_basis`, **not**
  `load_fred_daily_risk_free`. The latter accrues DTB3's bank-discount quote as if it were an
  investment yield, understating cash by ~0.082 pp/yr. F1 could keep it because understating cash
  made its STOP conclusion conservative; here the sign flips — understating cash inflates both the
  credited idle-cash return and the resulting excess Sharpe.
- Use `excess_return_metrics`, not `compare_to_cash` (frozen R1 evidence), and quote
  `preferred_ratio_field`. Several F27 comparisons will be between highly correlated variants of
  the same strategy, which is the regime where a geometric excess/volatility ratio stops being a
  Sharpe ratio.

**Measured 2026-08-05** with `research/review_2026_08_04/verify_idle_cash_credit.py`, following
both constraints above exactly (investment-basis rate, `excess_return_metrics`,
`preferred_ratio_field`), against the committed PIT-DISP-0015 `daily_equity.csv` /
`daily_weights.csv` (2022-12-10..2026-08-02, no re-fit — gross exposure read directly from the
committed weights, cash fraction is `1 - gross`, credited at the daily investment-basis rate):

| | V1 baseline | BRRK-0011 core |
|---|---:|---:|
| mean idle-cash fraction | 20.5% | 24.6% |
| CAGR, raw → credited | 61.313% → 62.663% | 65.166% → 66.807% |
| CAGR delta | **+1.351 pp** | **+1.641 pp** |
| Sharpe (rf=0), raw → credited | 1.2950 → 1.3138 | 1.3532 → 1.3756 |
| Sharpe (excess over rf), raw → credited | 1.2724 → 1.3029 | 1.3667 → 1.4039 |
| Max drawdown, raw → credited | -37.63% → -36.60% | -33.72% → -33.55% |

> **Corrected 2026-08-06.** The first published version of this table read
> 61.373% / 65.233% for the raw CAGRs, with deltas +1.348 / +1.637 pp. Those raw
> figures were wrong, and wrong in a way this backlog already has an item about:
> the script built its return series with `pct_change().dropna()`, which drops
> `daily_equity.csv`'s first row. That row is not a placeholder — V1 opens at
> 9999.459168, already one day of trading from the $10,000 base — so dropping it
> discarded a day of PNL *and* shortened the series' calendar span from 1331 to
> 1330 days, inflating CAGR by ~0.06 pp. The result was a **third** BRRK-0011
> CAGR (65.233%) sitting next to the two F7 exists to explain (65.10%
> observation-count, 65.17% calendar-span). The script now seeds the first
> return off the $10,000 base — the convention `verify_psr_dsr_mintrl.py`
> already used and `test_metrics.py` already pinned — and asserts on startup
> that its raw BRRK-0011 CAGR reproduces the published 0.6516609785 to 1e-6,
> so this cannot silently regress. **Every conclusion below survived the
> correction unchanged**: Sharpe still rises on crediting for both variants, and
> the BRRK-vs-V1 gap shift is still +0.0036.

The CAGR direction and rough size (+1.3-1.6pp) match the preliminary estimate. **The Sharpe
direction does not**: both variants' Sharpe *rises* on crediting, on both the rf=0 and the
excess-over-rf basis — it does not fall from 1.295 to 1.215 the way the preliminary estimate
assumed. This is mechanically expected once you account for *when* the idle cash sits: median
idle fraction is 0% for both variants (most days are close to fully invested), and the mean is
pulled up by episodes where the regime-Kelly / trend-following exposure pulls back toward cash —
which are disproportionately the same higher-realized-volatility, drawdown-adjacent periods.
Crediting a smooth, positive, low-volatility return exactly on the days the strategy is
defensively out of the market is diversifying, not diluting; both variants' max drawdown also
improves slightly, consistent with this. The "1.295 to 1.215" figure predates
`excess_return_metrics`/the investment-basis rate and was a preliminary estimate from the initial
review, not a reproduced number — treat the table above as the current source of truth and this
note as its correction, per discipline #3 (both are kept, not silently merged).

**Net effect on the BRRK-0011 vs V1 comparison:** the Sharpe gap moves from +0.0582 (raw) to
+0.0618 (credited) — a shift of +0.0036, far smaller than F10's bootstrap CI width
`[-0.046, +0.164]`. Idle-cash crediting does not change which side of zero that comparison sits
on, and does not change the "not statistically significant" conclusion.

**What this does change:** both variants' true achievable CAGR is 1.3-1.6pp higher than the
headline numbers show, at zero additional strategy or leverage risk, if idle margin is actually
swept into a yield-bearing instrument (a T-bill ladder, or a spot-collateral yield where
applicable) instead of sitting at 0%. This is the one restatement in this pass with a direct,
low-risk profitability read: it is not a reason to change the strategy, but it is a reason to make
sure idle margin is not literally earning nothing in execution.

**Not yet done:** wiring this into the four `metrics()` functions listed above as a standing
feature (this measurement was done as an external overlay on committed evidence, matching the
"report restated numbers next to the originals" instruction, without touching any frozen
function). Doing that for every experiment, not just the BRRK-0011-vs-V1 headline pair, is future
work if it turns out to matter for a specific promotion decision.

### F28. Cost model has no impact term

**Files:** all runners using `COST_BPS = 5.0`

Cost is linear in L1 turnover and size-independent. The ROUTER-DATA-0004 depth figure is a single
snapshot, and the PIT-ALPHA line rotates dozens of small-cap alts where linear cost understates
materially. Crypto metaorder impact follows an approximately square-root law.

**Do.** Move to `spread/2 + k·σ·sqrt(Q/V)` and re-run the capacity analysis at $100k / $1M / $10M.
`research/results/audit_0017_pit_alpha_attribution/capacity_proxy.csv` already exists to hook
into. **[REGISTER]** if it changes a promotion decision.

---

## Verified not to be a defect — do not "fix"

**`apply_band` weight drift.** `run_portfolio` treats `held` as a constant weight vector between
rebalances and charges turnover as `held.diff().abs()`, which does not bill the daily trading that
holding constant weights actually requires. Measured over 2021-05-01..2026-08-03: repo-convention
turnover 158.29 vs drift-consistent 159.93, CAGR 44.70% vs 45.30%. The gap is ~1% of turnover,
about 0.1%/yr at 5bps, and its sign favours the drift-consistent run. Because the beta target
moves daily, the band triggers most days and drift never accumulates.

The research and execution **band semantics** still differ (backtest compares target against the
last adopted target; the bot compares target against actual beta) — that is tracked under F22 as a
parity issue, not a cost issue.

Reproduce with `research/review_2026_08_04/verify_band_drift.py`.
