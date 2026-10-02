# Grid Data Service

**Version: v0.5.0**

Production-oriented, read-only FastAPI backend for a D5000 power-equipment catalog,
equipment details, topology relations and measurement points.

## Where customers configure the project

This is intentionally explicit:

```text
config/
├─ application.yaml          # API/runtime settings
├─ profiles/
│  └─ jeddah.yaml            # reusable Jeddah business model / SQL
└─ local/
   └─ jeddah.yaml            # actual Oracle connection settings
```

For the current Jeddah deployment, **Oracle connection information is configured in**:

```text
config/local/jeddah.yaml
```

If the Oracle IP, service or username changes, edit that file and restart. If the
password changes, update the `GRID_ORACLE_PASSWORD` process environment variable.
Do not modify Python source code or commit credentials.

`config/local/*.yaml` is ignored by Git so deployment credentials are not normally
committed when this project is later pushed to a repository.

## Architecture

```text
Client / Frontend
      |
      v
FastAPI API v1
      |
      +-- Endpoint layer
      |
      +-- Service layer
      |
      +-- Repository layer
      |
      +-- Async Oracle data layer
               |
               v
       Oracle commercial DB
```

Key design points:

- FastAPI official CLI entrypoint in `pyproject.toml`
- async FastAPI endpoints
- `python-oracledb` async connection pool
- application lifespan startup/shutdown
- API versioning (`/api/v1`)
- repository/service separation
- typed Pydantic v2 configuration
- lazy datasource initialization
- request IDs
- JSON structured logs
- liveness/readiness endpoints
- SQL bind variables
- configurable query cache
- strict read-only SQL policy
- Oracle `SET TRANSACTION READ ONLY`
- deployment-local configuration overlay
- reusable site profiles

## First setup on Windows

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup.ps1
```

No Oracle information is requested interactively. The Jeddah endpoint and username
are in `config/local/jeddah.yaml`; set `GRID_ORACLE_PASSWORD` in the process
environment before connecting.

Test Oracle:

```powershell
.\test-oracle.ps1
```

## Official FastAPI commands

The project has this in `pyproject.toml`:

```toml
[tool.fastapi]
entrypoint = "app.main:app"
```

Therefore development mode is simply:

```powershell
.\.venv\Scripts\fastapi.exe dev
```

Production-style local run:

```powershell
.\.venv\Scripts\fastapi.exe run --host 0.0.0.0 --port 8899
```

Or use the convenience wrapper:

```powershell
.\start.ps1
```

Development wrapper:

```powershell
.\start.ps1 -Dev
```

Swagger:

```text
http://127.0.0.1:8899/docs
```

ReDoc:

```text
http://127.0.0.1:8899/redoc
```

## Health endpoints

```text
GET /api/v1/health
GET /api/v1/health/live
GET /api/v1/health/ready
```

`live` checks the process. `ready` also checks configured datasource connectivity.

## Current API families

```text
GET  /api/v1/profiles
GET  /api/v1/profiles/{profile_id}/capabilities

GET  /api/v1/{profile_id}/catalog/roots
GET  /api/v1/{profile_id}/catalog/nodes/{node_id}/children
GET  /api/v1/{profile_id}/catalog/search

GET  /api/v1/{profile_id}/substations
GET  /api/v1/{profile_id}/bays?substation_id={id}
GET  /api/v1/{profile_id}/busbars?substation_id={id}&bay_id={id}
GET  /api/v1/{profile_id}/feeders?substation_id={id}
GET  /api/v1/{profile_id}/equipment?substation_id={id}&bay_id={id}
GET  /api/v1/{profile_id}/signals?substation_id={id}

GET  /api/v1/{profile_id}/equipment/{entity_type}/{entity_id}
GET  /api/v1/{profile_id}/equipment/{entity_type}/{entity_id}/signals

GET  /api/v1/{profile_id}/topology/{entity_type}/{entity_id}
```

The catalog is a physical hierarchy backed by the commercial D5000 model:

```text
substation
├── voltage_level
│   └── bay
│       ├── breaker
│       ├── disconnector
│       ├── ground_disconnector
│       ├── busbar_section
│       ├── energy_consumer
│       ├── single_terminal
│       └── ac_line_end
└── power_transformer
    └── transformer_winding

The explicit directory list endpoints are designed for frontend tree/grid pages:

- `substations` reads `SUBSTATION`.
- `bays` reads `BAY`, optionally scoped by `substation_id`.
- `busbars` reads `BUSBARSECTION`, optionally scoped by station or bay.
- `feeders` reads the live D5000 `DMS_FEEDER_DEVICE` table and is scoped by `ST_ID`.
- `equipment` reads allow-listed physical equipment tables and supports `entity_type`,
  station, bay and text filters.
- `signals` reads the union of `MEASPOINT` and `MEASANALOG`; use `substation_id`,
  or pair `entity_type` with `entity_id` for an efficient scoped query.

All list endpoints return the same envelope:

```json
{
  "items": [],
  "meta": {"offset": 0, "limit": 50, "returned": 0, "has_more": false}
}
```

`profile_id` is the configured profile name, currently `jeddah`; it is not a database
user or Oracle schema name.
```

Topology is intentionally exposed as a graph relation endpoint rather than being
forced into the physical directory tree. The service does not expose arbitrary SQL
or a generic named-query endpoint to clients.

## Read-only database policy

The service does not expose arbitrary SQL from clients.

Configured SQL accepts only:

```sql
SELECT ...
```

or:

```sql
WITH ...
SELECT ...
```

It rejects write/DDL/PLSQL constructs including INSERT, UPDATE, DELETE, MERGE,
CREATE, ALTER, DROP, TRUNCATE, CALL, EXEC and `FOR UPDATE`.

Each Oracle operation also runs inside:

```sql
SET TRANSACTION READ ONLY
```

and the connection is rolled back before it is returned to the pool.

For a final production deployment, a database account with SELECT-only grants is
still the strongest database-side permission boundary. Set the local secret through
the `GRID_ORACLE_PASSWORD` environment variable; do not place it in YAML or source.
