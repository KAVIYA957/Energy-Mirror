# Energy Mirror - Backend Service

FastAPI-powered energy telemetry ingestion and NILM disaggregation service.

## Architecture

- **Framework**: FastAPI (Python 3.11) with Pydantic v2 validation models.
- **Persistence**: SQLAlchemy 2.0 with SQLite database (`energy_mirror.db`).
- **Telemetry Invariants**:
  - `aggregate_power_w = sum(appliances.estimated_power_w) + unattributed_power_w`
  - All readings strictly tagged with `data_source` (`LIVE`, `SIMULATED`, `NILM_ESTIMATED`, `STALE`, `UNAVAILABLE`).
  - No negative residuals; unattributed percentages bounded to `[0.0, 100.0]`.

## Endpoints

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Health status and SQLite connectivity check |
| `GET` | `/api/v1/telemetry/live` | Current aggregate household load reading |
| `GET` | `/api/v1/telemetry/history?minutes=60` | Timestamped historical load trace with transition events |
| `GET` | `/api/v1/nilm/live-disaggregation` | Disaggregated appliance constellation estimates |

## Running the Server

```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Run server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Running Tests

```powershell
python -m pytest -v
```
