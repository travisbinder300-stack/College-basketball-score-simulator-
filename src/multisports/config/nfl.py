"""NFL sport configuration stub."""

from .base import SportConfig


NFL_CONFIG = SportConfig(
    sport="nfl",
    league="National Football League",
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
    min_train_games=50,
    model_dir="artifacts",
)
