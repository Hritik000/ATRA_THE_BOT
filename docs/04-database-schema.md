# Database Schema

## candles
id UUID PK
asset VARCHAR
timeframe VARCHAR
timestamp TIMESTAMPTZ
open NUMERIC
high NUMERIC
low NUMERIC
close NUMERIC
volume NUMERIC NULL
source VARCHAR
dataset_version VARCHAR
created_at TIMESTAMPTZ

Unique: asset + timeframe + timestamp.

## feature_sets
id UUID PK
candle_id UUID FK
feature_version VARCHAR
rsi DOUBLE PRECISION
ema_fast DOUBLE PRECISION
ema_slow DOUBLE PRECISION
macd DOUBLE PRECISION
atr DOUBLE PRECISION
bb_width DOUBLE PRECISION
volatility DOUBLE PRECISION
momentum DOUBLE PRECISION
created_at TIMESTAMPTZ

## predictions
id UUID PK
timestamp TIMESTAMPTZ
asset VARCHAR
timeframe VARCHAR
model_version VARCHAR
feature_version VARCHAR
up_probability DOUBLE PRECISION
down_probability DOUBLE PRECISION
calibrated_probability DOUBLE PRECISION NULL
predicted_class VARCHAR
created_at TIMESTAMPTZ

## signals
id UUID PK
prediction_id UUID FK
timestamp TIMESTAMPTZ
asset VARCHAR
signal VARCHAR
confidence DOUBLE PRECISION
regime VARCHAR
risk_state VARCHAR
reason JSONB
strategy_version VARCHAR
created_at TIMESTAMPTZ

## experiments
id UUID PK
name VARCHAR
hypothesis TEXT
dataset_version VARCHAR
feature_version VARCHAR
model_version VARCHAR
config JSONB
metrics JSONB
status VARCHAR
created_at TIMESTAMPTZ

## backtests
id UUID PK
experiment_id UUID FK
strategy_version VARCHAR
start_time TIMESTAMPTZ
end_time TIMESTAMPTZ
config JSONB
metrics JSONB
artifact_uri VARCHAR NULL
created_at TIMESTAMPTZ

## paper_trades
id UUID PK
signal_id UUID FK
entry_time TIMESTAMPTZ
exit_time TIMESTAMPTZ NULL
asset VARCHAR
direction VARCHAR
entry_price NUMERIC
exit_price NUMERIC NULL
result VARCHAR NULL
pnl NUMERIC NULL
simulation_config JSONB

## audit_events
id UUID PK
timestamp TIMESTAMPTZ
actor_type VARCHAR
actor_id VARCHAR NULL
action VARCHAR
resource_type VARCHAR
resource_id VARCHAR NULL
metadata JSONB
success BOOLEAN

Add indexes for asset/timeframe/timestamp, model version, experiment status, and recent audit events.
