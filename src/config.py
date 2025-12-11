"""Configuration settings for the betting system"""

# Model settings
MODEL_TYPES = ['logistic_regression', 'random_forest', 'xgboost', 'gradient_boosting']
ENSEMBLE_METHOD = 'weighted_average'
TRAIN_TEST_SPLIT = 0.2
RANDOM_STATE = 42

# Feature engineering
ROLLING_WINDOW = 5  # Games to consider for moving averages
MIN_GAMES_THRESHOLD = 5  # Minimum games needed for predictions

# Betting strategy
MIN_EDGE_THRESHOLD = 0.03  # Minimum 3% edge to place bet
MAX_EDGE_THRESHOLD = 0.15  # Maximum edge (sanity check)
KELLY_FRACTION = 0.25  # Quarter Kelly for conservative betting
MAX_BET_SIZE = 0.05  # Maximum 5% of bankroll per bet
MIN_BET_SIZE = 0.01  # Minimum 1% of bankroll per bet

# Odds settings
AMERICAN_ODDS_FORMAT = True
JUICE_ADJUSTMENT = 0.05  # Typical sportsbook vig

# Data settings
DATA_DIR = 'data'
MODELS_DIR = 'models'

# Model weights (based on historical performance)
MODEL_WEIGHTS = {
    'logistic_regression': 0.15,
    'random_forest': 0.25,
    'xgboost': 0.35,
    'gradient_boosting': 0.25
}

# Performance thresholds
MIN_ROI = 0.05  # Minimum 5% ROI to recommend system
MIN_ACCURACY = 0.54  # Minimum accuracy to beat the market (accounting for juice)
