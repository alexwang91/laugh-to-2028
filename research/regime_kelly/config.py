from dataclasses import dataclass, field


@dataclass(frozen=True)
class RegimeKellyConfig:
    assets: tuple[str, ...] = ("BTC", "ETH", "SOL", "BNB", "XRP")
    majors: tuple[str, ...] = ("ETH", "BNB", "XRP")
    alts: tuple[str, ...] = ("ETH", "SOL", "BNB", "XRP")
    n_states: int = 4
    forecast_horizon_days: int = 20
    min_train_days: int = 600
    refit_every_days: int = 30
    purge_days: int = 20
    embargo_days: int = 5
    scenario_count: int = 5000
    random_seed: int = 20260804
    winsor_lower: float = 0.01
    winsor_upper: float = 0.99
    hmm_iter: int = 300
    hmm_tol: float = 1e-4
    hmm_restarts: int = 5
    sticky_diagonal_prior: float = 12.0
    sticky_offdiag_prior: float = 1.0
    gross_cap: float = 1.0
    research_gross_cap: float = 1.30
    asset_caps: dict[str, float] = field(default_factory=lambda: {
        "BTC": 1.00,
        "ETH": 0.40,
        "SOL": 0.25,
        "BNB": 0.20,
        "XRP": 0.20,
    })
    cvar_alpha: float = 0.95
    max_horizon_cvar_loss: float = 0.20
    turnover_penalty: float = 0.0025
    uncertainty_penalty: float = 0.10
    shrinkage_strength: float = 20.0


FEATURE_COLUMNS = (
    "btc_trend",
    "log_btc_rv30",
    "btc_drawdown_252",
    "btc_dom_30",
    "btc_dom_90",
    "major_breadth",
    "alt_breadth",
    "rel_strength_mean",
    "rel_strength_dispersion",
    "avg_corr30_btc",
)
