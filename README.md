# ATRA

![License](https://img.shields.io/badge/license-MIT-blue.svg)

## AI Trading Research & Analysis Platform

ATRA is a human-in-the-loop quantitative research platform for market-data analysis, probabilistic ML signals, market-regime detection, risk controls, backtesting, paper trading, experiment tracking, and AI-assisted research.

### Critical execution boundary
ATRA does not automate Quotex trade execution. Quotex's published rules currently prohibit automated mechanisms/algorithms/specialized software performing operations without direct client participation. Re-check current platform terms before any future integration.

### Goals
- Reproducible market research
- Time-series-safe ML
- Robust backtesting
- Independent risk controls
- Paper trading
- Explainable signals
- Auditable experiments
- Controlled AI agents
- Industry-grade engineering

### Non-goals
- Automated Quotex clicking
- CAPTCHA bypass
- Session theft
- Private API reverse engineering
- Guaranteed profits
- Martingale loss recovery
- Fake Git activity

### Suggested stack
Backend: Python, FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL.
ML: NumPy, pandas, scikit-learn, XGBoost, optional Optuna/MLflow.
Frontend: Next.js, TypeScript, Tailwind CSS, charting library.
DevOps: Docker, GitHub Actions, secret/dependency scanning.

### Architecture
```text
Data -> Validation -> Features -> ML/Regime -> Signal -> Risk -> Human Approval
                    |                         |
                    +-> Backtesting ----------+
                    +-> Paper Trading --------+
                    +-> Research Agents ------+
```

See `/docs` for the complete specification.

## Development Setup

### Prerequisites
- Python 3.9+
- Docker and Docker Compose (optional)
- Make (optional)

### Local Development

1. Clone the repository
2. Copy environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
3. Install dependencies:
   ```bash
   make install
   ```
4. Run the development server:
   ```bash
   make dev
   ```
5. The API will be available at http://localhost:8000

### Docker Development

1. Copy environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
2. Start all services:
   ```bash
   make docker-up
   ```
3. The API will be available at http://localhost:8000

### Testing

```bash
make test
```

### Code Quality

```bash
make lint
make format
make typecheck
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "describe your changes"

# Apply migrations
alembic upgrade head
```