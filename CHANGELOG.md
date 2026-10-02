# Changelog

## v0.5.0 - 2026-10-02

Added explicit read-only power-equipment directory list APIs.

- Added paginated substations, bays, busbars, feeders, equipment and signals endpoints.
- Mapped feeders to the live D5000 `DMS_FEEDER_DEVICE` table using `ST_ID`.
- Added station/bay/text filters and scoped signal listing.
- Exposed feeder nodes in catalog children and search results.
- Verified all new endpoints against the commercial Oracle database using read-only transactions.

## v0.4.0 - 2026-10-02

Major read-only power-equipment catalog refactor.

- Added typed catalog, equipment, topology and measurement-point domain models.
- Added D5000 Oracle mappings for substations, voltage levels, bays and equipment.
- Added bounded Oracle-compatible pagination and stable catalog responses.
- Removed the public generic named-query endpoint.
- Added production-safe catalog cache bounds and degraded readiness status.
- Moved the local Oracle password to `GRID_ORACLE_PASSWORD`.
- Added domain and API validation coverage.

## v0.3.0 - 2026-10-02

Major production-architecture refactor.

- Removed obsolete `configure-oracle.ps1`.
- Removed obsolete `set-oracle-secret.ps1`.
- Removed obsolete `remove-oracle-secret.ps1`.
- Removed keyring-based setup from the current deployment workflow.
- Customer Oracle configuration is now clearly located at
  `config/local/jeddah.yaml`.
- Added `config/application.yaml`.
- Added official FastAPI CLI entrypoint in `pyproject.toml`.
- Upgraded architecture to async FastAPI + async python-oracledb connection pools.
- Added API v1 package structure.
- Added repository/service layering.
- Added lifespan-managed resources.
- Added request ID middleware.
- Added JSON structured logging.
- Added liveness/readiness endpoints.
- Preserved strict read-only SQL and Oracle read-only transactions.
- Simplified root scripts to `setup.ps1`, `start.ps1`, and `test-oracle.ps1`.
