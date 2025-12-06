# Sports Analytics Repository

This repository contains advanced sports analytics systems for multiple leagues.

## NHL Spread and Total Analytics

A comprehensive NHL (National Hockey League) analytics system that provides spread and total predictions with **70% confidence intervals** using real NHL data.

### Features
- **Real-time NHL data** from official NHL API
- **Spread predictions** with statistical confidence intervals
- **Total (Over/Under) predictions** with 70% confidence
- **Statistical modeling** using team strength ratings and performance metrics
- **Multiple analysis modes**: CLI, Python API, and JSON export

### Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the analytics:
```bash
python nhl_analytics.py
```

3. See examples:
```bash
python examples.py
```

### Documentation

See [NHL_README.md](NHL_README.md) for detailed documentation including:
- Complete API reference
- Team abbreviations
- Statistical methodology
- Usage examples
- Confidence interval calculations

### Testing

Run the comprehensive test suite:
```bash
python test_nhl_analytics.py
```

All tests validate:
- Data fetching and processing
- Prediction accuracy and structure
- Statistical confidence intervals
- Edge cases and error handling

## Future Additions

- College Basketball Score Simulator (planned)
- Additional sports analytics modules

## License

See LICENSE file for details.
