# Technical Design

## Backend
Python 3.12+, FastAPI, Pydantic, SQLAlchemy 2.x, Alembic, PostgreSQL, pytest, Ruff, mypy, pre-commit.

## ML
NumPy, pandas, scikit-learn, XGBoost. Add Optuna/MLflow only when justified.

## Frontend
Next.js, TypeScript, Tailwind CSS, charting library.

## DevOps
Docker, Docker Compose, GitHub Actions, dependency and secret scanning.

## Layering
```text
API
 |
Application Services
 |
Domain
 |
Ports / Interfaces
 |
Infrastructure
```

## Standards
- type hints on public functions
- Pydantic at boundaries
- UTC internally
- Decimal for monetary accounting where required
- structured logging
- explicit enums
- fail-closed risk decisions
- no network calls from model classes
- no DB access inside indicator functions

## Error types
DataValidationError
UnsupportedAssetError
ModelNotFoundError
BacktestConfigurationError
RiskBlockedError
PermissionDeniedError

Do not expose stack traces or secrets via APIs.

## Configuration
Environment/config injection only. Never commit secrets. Protect AI coding-agent context from `.env` and credential files.
