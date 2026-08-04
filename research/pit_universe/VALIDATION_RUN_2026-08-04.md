# PIT-DISP-0015 validation run request

Date: 2026-08-04

Purpose: trigger and observe the first valid execution of the frozen survivorship-aware dynamic-universe dispersion experiment in the canonical repository.

No model, universe, signal, execution or cost parameter is changed by this file.

The run must retain the preregistered rules in `PIT-DISP-0015-DYNAMIC-UNIVERSE.json` and produce exact daily equity, held weights, dynamic-universe counts, dispersion scales, inactive-symbol eligibility audit and an exact daily NAV SVG.

A CI or data-engineering failure is not a model result. No PNL conclusion may be recorded unless the Python model step completes and the report/artifacts are produced.
