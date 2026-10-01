# API Contract

Base path: `/api/v1`

GET `/health`
GET `/ready`

GET `/market/candles?asset=&timeframe=&from=&to=`
GET `/market/latest?asset=&timeframe=`

POST `/features/compute`

POST `/predictions`
GET `/predictions`

GET `/signals`
GET `/signals/{id}`
POST `/signals/evaluate`

POST `/backtests`
GET `/backtests/{id}`
GET `/backtests/{id}/metrics`

POST `/experiments`
GET `/experiments`
GET `/experiments/{id}`
POST `/experiments/{id}/run`

POST `/paper-trades`
GET `/paper-trades`
GET `/paper-trades/performance`

GET `/models`
GET `/models/{version}`
POST `/models/train`

GET `/system/agents`
GET `/system/metrics`

## API rules
- validate external input
- paginate collections
- use idempotency keys for jobs when needed
- never return credentials
- no internal stack traces
- explicit enums
- authentication/authorization before public write access
