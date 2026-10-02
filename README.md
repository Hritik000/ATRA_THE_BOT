# ATRA (AI Trading Research & Analysis Platform)

[![CI Pipeline](https://github.com/Hritik000/ATRA_THE_BOT/actions/workflows/ci.yml/badge.svg)](https://github.com/Hritik000/ATRA_THE_BOT/actions/workflows/ci.yml)
[![Security Scanning](https://github.com/Hritik000/ATRA_THE_BOT/actions/workflows/codeql.yml/badge.svg)](https://github.com/Hritik000/ATRA_THE_BOT/actions/workflows/codeql.yml)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

ATRA is a rigorous, human-in-the-loop quantitative research and analysis platform engineered for market-data ingestion, probabilistic ML signals, market-regime classification, fail-closed risk controls, event-driven backtesting, and auditable trade research.

---

## :warning: Critical Execution Boundary (Quotex Policy)

> **ATRA STRICTLY DOES NOT AUTOMATE QUOTEX TRADE EXECUTION.**
>
> In compliance with Quotex platform policies and ethical engineering standards:
> - Automated browser clicking (Puppeteer, Playwright, Selenium) is strictly prohibited.
> - CAPTCHA bypass, session theft, private websocket tampering, or hidden API reverse engineering are explicitly out of scope.
> - ATRA generates analytical signals, probabilities, and paper trades. **All live execution decisions remain 100% human-approved and manual.**

---

## System Architecture

```text
Market Data ----> Validation Layer ----> Feature Store ----> ML / Regime Detection
                         |                                           |
                         v                                           v
                  Quality Database                             Signal Engine
                         |                                           |
                         v                                           v
                   Backtesting Engine                        Fail-Closed Risk
                         |                                           |
                         +------------> Paper Trading <--------------+
                                             |
                                             v
                                  Human Approval Interface
```

### Core Pipeline Modules
1. **Market Data Layer**: Clean, normalized OHLCV time-series store with precision Decimal financial types and UTC timestamps.
2. **Validation Engine**: Multi-tier data sanity auditing (OHLC relationship, price non-negativity, volume checks, timestamp continuity).
3. **Feature Engineering**: Deterministic statistical & technical indicators calculated with strict anti-leakage guarantees.
4. **Probabilistic Models**: Chronologically split, cross-validated machine learning models and market-regime classifiers.
5. **Risk Engine**: Independent, fail-closed risk checks decoupled from model predictions.
6. **Human Approval**: Clear, explainable signals presented for human review and manual execution.

---

## Repository Structure

```text
ATRA_THE_BOT/
├── .github/
│   ├── ISSUE_TEMPLATE/        # Standardized issue templates
│   ├── workflows/             # CI, CodeQL security, and Docker workflows
│   ├── dependabot.yml         # Automated dependency vulnerability updates
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/                      # Architectural specs & technical guidelines
├── alembic/                   # Database schema migrations
├── src/
│   └── atra_backend/
│       ├── api/               # FastAPI route controllers (v1)
│       ├── core/              # Settings, security & configuration
│       ├── crud/              # Typed database access operations
│       ├── db/                # Session and connection handling
│       ├── models/            # SQLAlchemy database models
│       └── validation/        # Data validation engine
├── tests/
│   ├── conftest.py            # Isolated fixtures & async mock session
│   └── unit/                  # Unit test suite
├── Dockerfile                 # Production multi-stage container
├── docker-compose.yml         # Local stack (PostgreSQL + FastAPI)
├── Makefile                   # Development automation commands
├── pyproject.toml             # Dependencies & tool configurations
└── README.md
```

---

## Getting Started

### Prerequisites
- **Python**: 3.10+ (tested on 3.10, 3.11, 3.12)
- **PostgreSQL**: 15+ (or run via Docker Compose)
- **Docker & Docker Compose** (optional, recommended)

### Quickstart

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Hritik000/ATRA_THE_BOT.git
   cd ATRA_THE_BOT
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Customize environment variables in .env as needed
   ```

3. **Install dependencies:**
   ```bash
   pip install -e ".[dev]"
   pre-commit install
   ```

4. **Run migrations & start server:**
   ```bash
   # Apply database migrations
   alembic upgrade head

   # Launch FastAPI development server
   make dev
   ```
   Interactive OpenAPI documentation will be live at:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

---

## Docker Quickstart

To run the entire stack (FastAPI backend + PostgreSQL) in isolated containers:

```bash
docker-compose up --build -d
```

View logs:
```bash
docker-compose logs -f
```

---

## Testing & Quality Control

ATRA maintains rigorous engineering standards. Tests run isolated and deterministic.

```bash
# Run complete test suite with coverage
make test

# Format code
make format

# Run linter
make lint

# Type check
make typecheck
```

---

## API Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health status check |
| `GET` | `/api/v1/market` | Paginated candle query with asset/timeframe filters |
| `POST` | `/api/v1/market` | Ingest single OHLCV candle |
| `POST` | `/api/v1/market/batch` | Batch ingest OHLCV candles |
| `GET` | `/api/v1/market/latest` | Fetch the latest candle for an asset/timeframe |
| `GET` | `/api/v1/validation` | Query candle validation results and quality metrics |
| `GET` | `/api/v1/validation/candle/{id}` | Fetch validation report for a specific candle |

---

## Contributing

We welcome contributions! Please review our guidelines before submitting pull requests:
- [CONTRIBUTING.md](CONTRIBUTING.md) — Git workflow, branch naming, and testing rules
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — Community standards
- [SECURITY.md](SECURITY.md) — Responsible vulnerability disclosure policy
- [AGENTS.md](AGENTS.md) — Engineering rules and safety specifications

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Frontend Development

The frontend is located in the `frontend/` directory and is a Next.js application with TypeScript and Tailwind CSS.

### Installing Frontend Dependencies

```bash
cd frontend
npm ci
```

### Running the Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at http://localhost:3000.

### Building for Production

```bash
cd frontend
npm run build
```

### Running Linting

```bash
cd frontend
npm run lint
```

### Running Tests

```bash
cd frontend
npm test
```

### Docker

The frontend is containerized and can be run via Docker Compose:

```bash
docker-compose up frontend
```

Then visit http://localhost:3000.
