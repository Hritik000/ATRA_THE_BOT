# Testing Strategy

## Unit
Indicators, features, labels, calibration, signals, risk, backtest accounting, metrics.

## Integration
API/service/repository, migrations, workers, model registry, backtest persistence.

## Data quality
Duplicates, gaps, invalid OHLC, timezone consistency, nulls, anomalies.

## ML
Preprocessing determinism, leakage, feature schema, model input compatibility, artifact loading, calibration.

## Security
Dependency scanning, secret scanning, auth tests, injection tests, rate limits, unsafe tool-call tests.

## Regression
Every important discovered bug becomes a regression test.

## Definition of done
Implementation, tests, docs, observability, security review, and CI all pass.
