# ML Specification

## Target
Example configurable target:
`y_t = 1 if close(t+horizon) > close(t), else 0`

The horizon must be recorded with each experiment.

## Model progression
1. Majority/random baseline
2. Logistic Regression
3. Random Forest
4. XGBoost
5. Optional neural/sequence models after baselines

## Feature groups
- trend
- momentum
- volatility
- candle geometry
- rolling returns
- time context
- regime features

## Leakage controls
- no future candles in features
- preprocessing fit only on training
- careful label alignment
- chronological evaluation
- untouched final test period

## Evaluation
Classification:
precision, recall, F1, ROC-AUC where meaningful, PR-AUC where meaningful, Brier score, calibration error.

Research/trading:
signal count, hit rate, expectancy, profit factor, maximum drawdown, return distribution, consecutive losses, turnover, cost sensitivity.

Accuracy is not a proxy for profitability.

## Calibration
Evaluate whether predicted probabilities correspond to observed frequencies. Use validation/calibration data only for calibration methods.

## Model metadata
Store model version, dataset version, feature version, code SHA, hyperparameters, train/validation/test periods, metrics, artifact checksum.
