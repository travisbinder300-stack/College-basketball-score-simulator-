"""NBA sport configuration."""

from .base import SportConfig


NBA_CONFIG = SportConfig(
    sport="nba",
    league="National Basketball Association",
    prediction_target="total_score",
    rolling_window=10,
    rest_cap=14,
    feature_columns=[
        "home_rolling_total_10",
        "away_rolling_total_10",
        "home_rest_days",
        "away_rest_days",
        "home_win_pct_10",
        "away_win_pct_10",
        "home_opp_strength_10",
        "away_opp_strength_10",
        "is_neutral_site",
    ],
    min_train_games=50,
    model_dir="artifacts",
)
