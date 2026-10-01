# Observability

## Logs
timestamp, level, service, environment, trace_id, event, duration, result.

Never log secrets.

## Metrics
Application: latency, errors, job duration, queue depth, DB latency.
ML: prediction count, confidence distribution, calibration, drift indicators.
Research: backtests completed, experiment failures, data-quality failures.
System: CPU/memory, worker health, DB health.

## Alerts
- repeated ingestion failure
- database unavailable
- stuck workers
- missing model artifact
- abnormal error rate
- security events
