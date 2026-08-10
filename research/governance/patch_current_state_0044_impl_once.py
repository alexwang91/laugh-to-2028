from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
p = ROOT / "docs/CURRENT_STATE.md"
text = p.read_text(encoding="utf-8")
replacements = {
    "Handoff PR: **#156**": "Handoff PR: **#157**",
    "Handoff branch: `research/brrk-exhaustion-state-0044-prereg`": "Handoff branch: `research/brrk-exhaustion-state-0044-runonce`",
    "Authoritative baseline main at branch creation: `72765cc28d66204f7b5e01fee8cef31b7cf22841`": "Authoritative baseline main at branch creation: `223d00202242d2d7e8eeffc489367e8078408604`",
    "Latest merged research PR at branch creation: **#155**": "Latest merged research PR at branch creation: **#156**",
    "BRRK exhaustion state 0044       PREREGISTERED / NOT RUN / NO TRIGGER AUTHORITY": "BRRK exhaustion state 0044       IMPLEMENTED / NOT RUN / CONTRACT VALIDATION PENDING",
}
for old, new in replacements.items():
    if old not in text:
        raise SystemExit(f"missing CURRENT_STATE anchor: {old}")
    text = text.replace(old, new, 1)

marker = "## BRRK-EXHAUSTION-STATE-0044 — preregistered, not run\n"
if marker not in text:
    raise SystemExit("0044 section missing")
text = text.replace(marker, "## BRRK-EXHAUSTION-STATE-0044 — implemented, still not run\n", 1)
old_sentence = "PR #156 freezes the next result-informed exhaustion-state research stage before any 0044 result exists. The formal PROGRAM_GOVERNED_V1 path is `research/brrk_exhaustion_state_0044/`."
new_sentence = "PR #156 froze the result-informed exhaustion-state research stage before any 0044 result existed. PR #157 now implements the frozen runner, run interface, source-reproduction guard, episode-aware metrics and permanent contract tests. No 0044 result has been executed or viewed; `PRIMARY_RESULT.json` and `RUN_ONCE.marker` do not exist. The formal PROGRAM_GOVERNED_V1 path remains `research/brrk_exhaustion_state_0044/`."
if old_sentence not in text:
    raise SystemExit("0044 intro sentence missing")
text = text.replace(old_sentence, new_sentence, 1)

text = text.replace(
    "1. Merge PR #156 only after the final PROGRAM_GOVERNED_V1 registry, dataset-exposure, no-drift, Phase-6 and handoff checks are green.\n2. Preserve `BRRK-EXHAUSTION-STATE-0044` as `PREREGISTERED_NOT_RUN` on merge; no result-bearing file may exist in the preregistration PR.\n3. After merge only, create a separate implementation/execution branch from the new main and implement the frozen CORE4/CORE5 definitions exactly.\n4. Execute 0044 exactly once. CORE4 controls pass/fail; CORE5 is secondary-only and cannot rescue a failure.\n5. Do not define trigger thresholds, WATCH/RISK persistence, recovery hysteresis or any gross map unless 0044 fully passes and a new research ID is preregistered.\n6. Continue Phase-6 future-only observation independently. Production, signing and order-submission authority remain false.",
    "1. Keep PR #157 result-free until its frozen runner/interface/contract tests and all governance/no-drift/Phase-6/parity checks are green.\n2. Only after that pre-result implementation baseline is green may one temporary one-shot workflow execute 0044 exactly once.\n3. The execution must first reproduce the exact 0043 16-peak and fixed label counts; any mismatch is execution-invalid and produces no research PASS/FAIL.\n4. CORE4 alone controls pass/fail; CORE5 is secondary-only and cannot rescue a failure. No same-ID tuning or rerun is permitted.\n5. After a valid unique run, bind artifact/result hashes, create the permanent run-once marker, remove temporary workflow, update registry/handoff, and rerun final CI.\n6. Do not define trigger thresholds, WATCH/RISK persistence, recovery hysteresis or any gross map unless 0044 fully passes and a new research ID is preregistered. Phase 6 remains independent and all production/signing/order authority stays false."
)
# Avoid creating diff-check noise from Markdown hard-break whitespace.
text = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
p.write_text(text, encoding="utf-8")
