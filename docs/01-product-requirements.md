# Product Requirements Document

## Product
ATRA: AI Trading Research & Analysis Platform.

## Problem
Market research is vulnerable to noisy data, leakage, overfitting, weak experiment tracking, and poor separation between prediction, risk, and execution. ATRA provides a reproducible research environment.

## Users
- Student/researcher
- Quant/ML developer
- Human trader seeking research assistance

## Functional requirements

### Data
FR-001 ingest permitted OHLC/time-series data.
FR-002 validate schema, timestamps, duplicates, gaps, and OHLC relationships.
FR-003 preserve raw data separately from processed data.
FR-004 version datasets and source metadata.

### Features
FR-010 configurable technical/statistical features.
FR-011 no future information in feature rows.
FR-012 deterministic/versioned feature pipeline.

### ML
FR-020 baseline and tree-based classifiers.
FR-021 chronological/walk-forward evaluation.
FR-022 calibrated probabilities.
FR-023 store dataset/feature/model/training metadata.

### Signals
FR-030 BUY/SELL/WAIT research signals.
FR-031 probability, confidence, regime, risk state, and reason.
FR-032 risk engine cannot be bypassed.
FR-033 human confirmation before external execution.

### Backtesting
FR-040 event-driven simulation.
FR-041 configurable costs, slippage, latency, and holding/expiry.
FR-042 drawdown, expectancy, hit rate, profit factor, distribution metrics.
FR-043 prevent look-ahead/survivorship/data leakage.

### Agents
FR-050 agents analyze/research/summarize/propose.
FR-051 typed allowlisted tools.
FR-052 no unrestricted credentials/filesystem/network.
FR-053 auditable actions.

### Dashboard
FR-060 market state, signals, models, backtests, experiments, paper trades, health.

## Non-functional requirements
NFR-001 secrets protected.
NFR-002 reproducible experiments.
NFR-003 structured observability.
NFR-004 automated testing.
NFR-005 modular architecture.
NFR-006 appropriate async I/O.
NFR-007 human-controlled Quotex execution.

## Success criteria
A new developer can clone the repository, configure a permitted data source, run tests, ingest sample data, train a baseline, run a backtest, inspect a signal, and reproduce the experiment from documentation.
