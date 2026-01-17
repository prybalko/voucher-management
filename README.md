# Voucher Management API

A simple REST API for managing discount vouchers built with FastAPI, SQLAlchemy, and PostgreSQL.

## Prerequisites

- Python 3.11+
- PostgreSQL (or Docker)

## Quick Start (Docker)

```bash
docker compose up -d
```

API available at http://localhost:8000

## Manual Setup

### 1. Start PostgreSQL

```bash
docker run -d --name vouchers-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=vouchers \
  -p 5432:5432 \
  postgres:16
```

Or set a custom connection string:
```bash
export DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/vouchers"
```

### 2. Install and Run

```bash
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

API available at http://localhost:8000

## Running Tests

Tests require PostgreSQL running (test database is created automatically):
```bash
pytest
```

Custom PostgreSQL connection:
```bash
POSTGRES_URL="postgresql+psycopg://user:pass@host:5432" pytest
```

## Linting & Formatting

```bash
ruff check .          # lint
ruff check --fix .    # lint and auto-fix
ruff format .         # format
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

| Method | Endpoint           | Description               |
|--------|--------------------|---------------------------|
| POST   | `/vouchers`        | Create a new voucher      |
| GET    | `/vouchers`        | List vouchers (paginated) |
| GET    | `/vouchers/{code}` | Get voucher by code       |
| PATCH  | `/vouchers/{code}` | Update a voucher          |
| DELETE | `/vouchers/{code}` | Deactivate a voucher      |

## Example Usage

**Create a voucher:**
```bash
curl -X POST http://localhost:8000/vouchers \
  -H "Content-Type: application/json" \
  -d '{"discount_percent": 20, "expires_at": "2026-12-31T23:59:59"}'
```

**List vouchers:**
```bash
curl http://localhost:8000/vouchers?skip=0&limit=10
```

**Get voucher by code:**
```bash
curl http://localhost:8000/vouchers/ABC12345
```

**Update a voucher:**
```bash
curl -X PATCH http://localhost:8000/vouchers/ABC12345 \
  -H "Content-Type: application/json" \
  -d '{"discount_percent": 25}'
```

**Deactivate a voucher:**
```bash
curl -X DELETE http://localhost:8000/vouchers/ABC12345
```
