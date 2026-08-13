from pathlib import Path

p = Path('docs/CURRENT_STATE.md')
text = p.read_text(encoding='utf-8')
text = text.replace('Last updated: **2026-08-13**', 'Last updated: **2026-08-14**', 1)
text = text.replace('Current `main` research merge: **`d9759316d80ea67390c9b2f65334f30d52fad19c`**', 'Current `main` research merge: **`aa3fa9c1814c4113918e0d012636db44a1f89659`**', 1)
text = text.replace('Current research branch: **`research/0062-btc-risk-signal-atlas-design`**', 'Current research branch: **`research/0062-prereg-v1`**', 1)
old = 'BRRK BTC risk signal atlas 0062        DESIGN FROZEN / PREREG ABSENT / NOT RUN'
new = 'BRRK BTC risk signal atlas 0062        PREREGISTERED / IMPLEMENTATION ABSENT / NOT RUN'
if text.count(old) != 1:
    raise RuntimeError(f'expected one 0062 status line, got {text.count(old)}')
text = text.replace(old, new, 1)
marker = '\n---\n\n## 2. 0048 immutable scientific result'
handoff = '''

## 0062 numerical/data preregistration handoff

```text
research id                             BRRK-BTC-RISK-SIGNAL-ATLAS-0062
design merge                            aa3fa9c1814c4113918e0d012636db44a1f89659
stage                                   PREREGISTERED / NOT RUN
Tier-A family count                     17
frozen candidate cells                  185
frozen family-track hypotheses          34
horizons                                5 / 10 / 20 / 40 sessions
Tier-B/C F15-F20                        DATA_UNAVAILABLE / NOT SUBSTITUTABLE POST HOC
F22 latent-state                        NOT EVALUATED IN 0062
historical 0062 outcomes                NOT COMPUTED
actual variants evaluated               0
RUN_ATTEMPT.marker                      ABSENT
portfolio economics                     FORBIDDEN
canonical BRRK-0011                     NO CHANGE
Phase 6                                 NO CHANGE
production_authorized                   false
signature_authorized                    false
order_submission_authorized             false
```

Exact candidate geometry, target formulas, family-track mapping, support gates, temporal recurrence, plateau gate and dependence-aware simultaneous MBB inference are frozen in `research/brrk_btc_risk_signal_atlas_0062/PREREGISTRATION.json`. The immutable Tier-A evidence wrapper remains researcher-exposed DEVELOPMENT history and is not independent OOS. No 0062 historical target, signal association or family ranking was computed during preregistration.
'''
if text.count(marker) != 1:
    raise RuntimeError(f'expected one insertion marker, got {text.count(marker)}')
text = text.replace(marker, handoff + marker, 1)
p.write_text(text, encoding='utf-8')
