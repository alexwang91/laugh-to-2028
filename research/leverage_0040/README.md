# LEVERAGE-0040

Status: **PREREGISTERED BEFORE FIRST RUN**

This experiment replaces the stopped-before-run `LEVERAGE-0039` architecture.

The frozen BRRK defensive selector remains strictly bounded to `[0,1]`. P4 leverage is a separate downstream multiplier:

```text
final_scale = frozen_defensive_scale × leverage_multiplier
```

No leverage search has been run. No candidate has been selected. No production leverage is authorized.

Before the first run:

- this preregistration must be merged;
- the official Hyperliquid margin snapshot must remain frozen;
- the two-layer runner must be implemented independently of the frozen defensive selector;
- cap `1.00` must reproduce the frozen BRRK historical path exactly.

After those gates pass, the preregistered study may run once without post-result retuning.
