# College Basketball Betting System 🏀

A sophisticated machine learning system designed to identify value betting opportunities in college basketball by predicting game outcomes and comparing them against sportsbook lines.

## 🎯 Overview

This system uses ensemble machine learning models to predict college basketball game outcomes with higher accuracy than the betting market, enabling profitable betting strategies. It implements:

- **Data Collection**: Historical game statistics and team performance metrics
- **Feature Engineering**: Advanced statistical features including rolling averages, differential stats, and team strength indicators
- **Ensemble ML Models**: Multiple algorithms (Logistic Regression, Random Forest, XGBoost, Gradient Boosting) combined for robust predictions
- **Value Betting**: Identifies bets where the model's probability significantly differs from market odds
- **Kelly Criterion**: Optimal bet sizing based on edge and bankroll management
- **Backtesting Framework**: Historical performance analysis with comprehensive metrics

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/travisbinder300-stack/College-basketball-score-simulator-.git
cd College-basketball-score-simulator-

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Run the complete system with sample data
python main.py

# Run with visualizations and save models
python main.py --visualize --save-models --save-data

# Use custom bankroll
python main.py --bankroll 5000

# Load your own data
python main.py --data-file data/my_games.csv
```

## 📊 How It Works

### 1. Data Collection
The system collects and processes:
- Team statistics (PPG, FG%, 3P%, rebounds, assists, turnovers)
- Historical game results
- Betting lines and spreads

### 2. Feature Engineering
Creates predictive features:
- Rolling averages (last 5 games)
- Differential statistics (home vs away team)
- Win percentages
- Home court advantage factors

### 3. Model Training
Trains multiple ML models:
- **Logistic Regression**: Fast baseline model
- **Random Forest**: Captures non-linear relationships
- **XGBoost**: High-performance gradient boosting
- **Gradient Boosting**: Additional ensemble perspective

Models are weighted based on historical performance and combined into a single ensemble prediction.

### 4. Betting Strategy
The system:
- Calculates expected probabilities for each game
- Compares against market-implied probabilities
- Identifies bets with positive expected value (edge ≥ 3%)
- Sizes bets using Kelly Criterion for optimal bankroll growth
- Manages risk with conservative betting (1/4 Kelly)

### 5. Backtesting
Validates strategy on historical data:
- Simulates betting on past games
- Tracks bankroll progression
- Calculates ROI, win rate, and other metrics
- Generates performance visualizations

## 📈 Performance Metrics

The system tracks key metrics:
- **Win Rate**: Percentage of successful bets
- **ROI**: Return on investment
- **Accuracy**: Model prediction accuracy
- **AUC**: Area under ROC curve
- **Expected Value**: Per-bet profit expectation
- **Sharpe Ratio**: Risk-adjusted returns

### Market-Beating Criteria
To beat the sportsbook market, the system aims for:
- **Win Rate > 54%** (accounting for typical -110 juice)
- **ROI > 5%** for long-term profitability
- **Positive Expected Value** on all recommended bets

## 🏗️ Project Structure

```
College-basketball-score-simulator-/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   ├── data/
│   │   ├── collector.py   # Data collection and generation
│   │   └── features.py    # Feature engineering
│   ├── models/
│   │   └── predictor.py   # ML model training and prediction
│   ├── betting/
│   │   ├── strategy.py    # Betting strategy and Kelly Criterion
│   │   └── backtest.py    # Backtesting framework
│   └── utils/
│       └── visualization.py  # Plotting and visualization
└── data/                  # Data directory (created on first run)
```

## 🔧 Configuration

Edit `src/config.py` to customize:

```python
# Betting Strategy
MIN_EDGE_THRESHOLD = 0.03    # Minimum 3% edge to bet
KELLY_FRACTION = 0.25        # Conservative 1/4 Kelly
MAX_BET_SIZE = 0.05          # Max 5% of bankroll per bet

# Model Settings
MODEL_TYPES = ['logistic_regression', 'random_forest', 'xgboost', 'gradient_boosting']
ROLLING_WINDOW = 5           # Games for rolling averages

# Performance Thresholds
MIN_ROI = 0.05              # Target 5% ROI
MIN_ACCURACY = 0.54         # Beat the vig threshold
```

## 📊 Example Output

```
BACKTEST RESULTS
================================================================
Betting Performance:
  Total Bets: 156
  Wins: 89
  Losses: 67
  Win Rate: 57.05%

Bankroll Performance:
  Initial Bankroll: $1000.00
  Final Bankroll: $1287.45
  Total Profit: $287.45
  ROI: 28.75%

✓ SYSTEM BEATS THE MARKET!
  This system shows positive expected value and
  outperforms typical sportsbook requirements.
================================================================
```

## 🎓 Key Concepts

### Value Betting
A bet has value when your model's probability of an outcome is higher than the market-implied probability. The "edge" is the difference between these probabilities.

### Kelly Criterion
Optimal bet sizing formula that maximizes long-term bankroll growth:
```
f = (bp - q) / b
```
Where:
- f = fraction of bankroll to bet
- b = odds - 1
- p = probability of winning
- q = probability of losing

We use 1/4 Kelly for more conservative, variance-reduced betting.

### Ensemble Learning
Combining multiple models reduces overfitting and provides more robust predictions than any single model.

## ⚠️ Important Disclaimers

1. **Past Performance ≠ Future Results**: Historical backtests do not guarantee future profitability
2. **Educational Purpose**: This system is for educational and research purposes
3. **Responsible Gambling**: Only bet what you can afford to lose
4. **Legal Compliance**: Ensure sports betting is legal in your jurisdiction
5. **No Guarantees**: No betting system can guarantee profits
6. **Variance**: Short-term results can vary significantly from expected values

## 🔬 Advanced Usage

### Custom Data Format
If using your own data, CSV should include:
```
date,home_team,away_team,home_score,away_score,home_ppg,away_ppg,
home_fg_pct,away_fg_pct,home_3p_pct,away_3p_pct,home_reb,away_reb,
home_ast,away_ast,home_to,away_to,betting_spread
```

### Model Tuning
Adjust model weights in `src/config.py`:
```python
MODEL_WEIGHTS = {
    'logistic_regression': 0.15,
    'random_forest': 0.25,
    'xgboost': 0.35,
    'gradient_boosting': 0.25
}
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Live data integration with sports APIs
- Additional features (player injuries, home/away splits, etc.)
- More sophisticated betting strategies
- Real-time odds comparison
- Web interface for predictions

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Remember: Bet Responsibly. This is an educational tool, not financial advice.**
