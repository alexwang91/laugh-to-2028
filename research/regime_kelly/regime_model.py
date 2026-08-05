"""Shared semantic-state labels for the regime models in this package.

`fit_regime_model`, `RegimeFit` and `_semantic_mapping` used to live here.
They were deleted (backlog F14) because nothing in the repo called them --
the active regime-fitting path is `regime_model_vb_nd.fit_variational_regime_model_nd`,
which labels states from contemporaneous features only.

`fit_regime_model`'s deleted `_semantic_mapping` helper labelled HMM states
using `train_forward_returns` (20-day-ahead returns). If a caller ever passed
in forward returns that reached the end of the training window, the last
`forecast_horizon_days` rows of that label fit would have used out-of-window
prices -- exactly what `RegimeKellyConfig.purge_days` / `embargo_days` exist
to prevent. Those two config fields were also deleted (nothing referenced
them either): a declared-but-unused safety setting reads as protection that
is in force, which was the actual risk, not the dead code path itself.

If a forward-return-labelled regime fit is wanted again, reimplement it with
an explicit purge/embargo argument enforced in the function signature, not as
an unused config default a caller could silently skip.
"""

SEMANTIC_STATES = ("RISK_OFF", "BTC_LEAD", "MAJOR_ROTATION", "ALT_EXPANSION")
