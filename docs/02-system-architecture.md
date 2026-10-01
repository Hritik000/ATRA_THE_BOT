# System Architecture

```text
Market Data Sources
       |
       v
+------------------+
| Data Ingestion   |
+------------------+
       |
       v
+------------------+       +----------------+
| Data Validation  |-----> | Raw Storage    |
+------------------+       +----------------+
       |
       v
+------------------+
| Feature Pipeline |
+------------------+
       |
       +------------------+
       |                  |
       v                  v
+-------------+    +---------------+
| ML Models   |    | Regime Engine |
+-------------+    +---------------+
       |                  |
       +--------+---------+
                v
        +---------------+
        | Signal Engine |
        +---------------+
                |
                v
        +---------------+
        | Risk Engine   |
        +---------------+
                |
                v
        +--------------------+
        | Human Approval     |
        +--------------------+
                |
                v
          Manual execution

Parallel:
Backtests -> Metrics -> Experiments -> Model Registry -> Research Agents
```

## Boundaries
- API layer: HTTP concerns only.
- Application services: use-case orchestration.
- Domain: business rules and deterministic calculations.
- Ports: interfaces.
- Infrastructure: DB, files, external data adapters.

## Rules
1. Domain logic does not depend on FastAPI.
2. Repositories do not contain strategy logic.
3. ML models cannot execute trades.
4. Risk is independently testable.
5. Agents use typed tools.
6. External integrations use adapters.
7. Predictions carry model versions.
8. Backtests carry dataset/strategy/model versions.
