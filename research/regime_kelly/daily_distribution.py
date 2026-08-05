"""Semantic-state Markov transition matrix, shared by the walk-forward scenario
engine.

`DailyConditionalDistribution`, `fit_daily_conditional_distribution`,
`_nearest_psd`, `_weighted_mean_cov`, `expected_state_mix`,
`markov_mean_uncertainty`, `sample_markov_paths` and `portfolio_path_cdar95`
used to live here too. They were deleted (backlog F14) because nothing in the
repo called `fit_daily_conditional_distribution` -- the active scenario path
is `hybrid_meta.walkforward_v1_meta.fit_state_v1_distribution` /
`sample_v1_paths`, an independent, already-in-use implementation that
condenses each state to a scalar V1 return rather than a full asset
covariance. The deleted cluster was a parallel, unused multi-asset version;
everything downstream of it (`markov_mean_uncertainty`, `sample_markov_paths`,
`portfolio_path_cdar95`) had no callers of its own either.

`semantic_transition_matrix` is kept: `walkforward_v1_meta.py` imports and
calls it directly.
"""
import numpy as np

from regime_model_vb_nd import VariationalRegimeFitND
from regime_model import SEMANTIC_STATES


def semantic_transition_matrix(regime_fit: VariationalRegimeFitND) -> np.ndarray:
    k = len(SEMANTIC_STATES)
    out = np.zeros((k, k), dtype=float)
    for i, s1 in enumerate(SEMANTIC_STATES):
        r1 = regime_fit.semantic_to_raw[s1]
        for j, s2 in enumerate(SEMANTIC_STATES):
            r2 = regime_fit.semantic_to_raw[s2]
            out[i, j] = float(regime_fit.model.transmat_[r1, r2])
        out[i] = out[i] / max(out[i].sum(), 1e-12)
    return out
