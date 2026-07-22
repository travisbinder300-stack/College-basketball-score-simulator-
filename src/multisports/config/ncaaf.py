"""NCAA Men's Football (NCAAF) sport configuration."""

from .base import SportConfig

NCAAF_CONFIG = SportConfig(
    sport="ncaaf",
    league="NCAA Division I Men's Football (FBS)",
    prediction_target="total_score",
    rolling_window=6,
    rest_cap=21,
    feature_columns=[
        "home_rolling_total_6",
        "away_rolling_total_6",
        "home_rest_days",
        "away_rest_days",
        "home_win_pct_6",
        "away_win_pct_6",
        "home_opp_strength_6",
        "away_opp_strength_6",
        "is_neutral_site",
    ],
    min_train_games=30,
    model_dir="artifacts",
)
