# Backtesting Specification

## Goal
Deterministic simulation without future information.

## Event order
At each timestamp:
1. read available data
2. calculate features
3. predict
4. generate signal
5. apply risk rules
6. simulate paper trade if allowed
7. resolve outcomes only when future information becomes available
8. advance

## Configuration
asset, timeframe, date range, feature version, model version, strategy version, signal threshold, holding/expiry rule, costs, slippage, latency, starting paper balance.

## Anti-leakage tests
- future-column perturbation must not change earlier predictions
- feature timestamps <= prediction timestamp
- model fitting excludes test data
- labels unavailable at prediction time
- future prices cannot alter earlier signals

## Reports
- equity curve
- drawdown
- trade list
- return distribution
- period summaries
- regime breakdown
- confidence buckets
- cost sensitivity

Backtests are research evidence, not promises.
