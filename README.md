# Configurable Grid Data Backend

A reusable, configuration-driven, **read-only** FastAPI backend for:

- power-grid hierarchy browsing
- stations / feeders / equipment / signals
- global search
- entity details
- upstream / downstream relationships
- path tracing
- topology data
- realtime signal values
- batch realtime reads
- project-specific named queries

The important design rule is:

> **Core code is generic. Project differences live in YAML profiles and SQL.**

So Jeddah / Jazan / Madinah / another ADMS project can reuse the same backend.

---

## 1. Directory layout

```text
adms-configurable-backend/
├─ app/
│  ├─ core/
│  ├─ db/
│  ├─ models/
│  ├─ routers/
│  ├─ services/
│  └─ main.py
├─ config/
│  └─ profiles/
│     ├─ example_oracle.yaml
│     └─ minimal_template.yaml
├─ scripts/
├─ tests/
├─ .env.example
├─ requirements.txt
└─ run.py
```

---

## 2. Design

```text
Browser / Other Project
          |
          v
      FastAPI v1
          |
          +---- Profile: jeddah.yaml
          |        |
          |        +---- model datasource (Oracle)
          |        +---- realtime datasource (optional Oracle)
          |
          +---- Profile: jazan.yaml
          |
          +---- Profile: madinah.yaml
```

Every profile can define:

- datasource connection
- hierarchy
- entity types
- tree SQL
- detail SQL
- signal SQL
- search SQL
- topology SQL
- upstream/downstream SQL
- realtime SQL
- arbitrary explicitly exposed named queries

---

## 3. Installation

Python 3.10+ recommended.

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Copy environment config:

```bash
# Windows
copy .env.example .env

# Linux
cp .env.example .env
```

Edit `.env`.

---

## 4. IMPORTANT: read-only Oracle account

Even though this backend rejects non-SELECT SQL in code, production must also use an Oracle account that has only SELECT permissions.

Recommended:

```text
APP
  -> READ-ONLY Oracle user
  -> SELECT grants only
```

Do not place DBA / owner credentials in `.env`.

This project intentionally does not provide INSERT / UPDATE / DELETE endpoints.

---

## 5. Start

```bash
python run.py
```

Open:

```text
http://127.0.0.1:8899/docs
```

---

## 6. API contract

Base URL:

```text
/api/v1
```

### System

```text
GET  /api/v1/health
GET  /api/v1/health/{profile_id}
POST /api/v1/admin/cache/clear
```

### Profiles / capabilities

```text
GET /api/v1/profiles
GET /api/v1/profiles/{profile_id}/capabilities
```

### Tree

```text
GET /api/v1/{profile_id}/tree/root

GET /api/v1/{profile_id}/tree/children
    ?node_type=station
    &node_id=123
```

Tree SQL should normalize each row to:

```json
{
  "id": "123",
  "name": "RMU14461",
  "type": "equipment",
  "subtype": "RMU",
  "has_children": 1
}
```

`subtype` is optional.

### Entity

```text
GET /api/v1/{profile_id}/entities/{entity_type}/{entity_id}
GET /api/v1/{profile_id}/entities/{entity_type}/{entity_id}/children
GET /api/v1/{profile_id}/entities/{entity_type}/{entity_id}/signals
GET /api/v1/{profile_id}/entities/{entity_type}/{entity_id}/path
GET /api/v1/{profile_id}/entities/{entity_type}/{entity_id}/upstream
GET /api/v1/{profile_id}/entities/{entity_type}/{entity_id}/downstream
```

Example:

```text
GET /api/v1/jeddah/entities/equipment/892331
```

### Topology

```text
GET /api/v1/{profile_id}/topology/{entity_type}/{entity_id}
```

Recommended SQL output:

```json
[
  {
    "record_type": "node",
    "id": "100",
    "label": "RMU14461",
    "node_type": "RMU",
    "source_id": null,
    "target_id": null
  },
  {
    "record_type": "edge",
    "id": "100-101",
    "label": null,
    "node_type": "connection",
    "source_id": "100",
    "target_id": "101"
  }
]
```

Frontend can transform this directly into graph nodes/edges.

### Search

```text
GET /api/v1/{profile_id}/search?q=RMU14461
GET /api/v1/{profile_id}/search?q=10501&entity_type=signal&limit=100
```

Recommended search result:

```json
[
  {
    "id": "892331",
    "name": "RMU14461",
    "type": "equipment",
    "subtype": "RMU"
  }
]
```

### Realtime

Enable in the profile:

```yaml
realtime:
  enabled: true
```

Then:

```text
GET  /api/v1/{profile_id}/realtime/signals/{signal_id}
POST /api/v1/{profile_id}/realtime/batch
```

Batch body:

```json
{
  "point_ids": ["1001", "1002", "1003"]
}
```

Recommended realtime output:

```json
{
  "point_id": "1001",
  "value": "CLOSE",
  "quality": "GOOD",
  "timestamp": "2026-10-02T14:20:01"
}
```

### Configured named queries

A project can add a new reusable query without adding Python routes.

Profile:

```yaml
queries:
  my_project_query:
    source: model
    result: many
    exposed: true
    allowed_params: [station_id]
    required_params: [station_id]
    sql: |
      SELECT ...
      WHERE station_id = :station_id
```

Call:

```text
POST /api/v1/{profile_id}/queries/my_project_query
```

Body:

```json
{
  "params": {
    "station_id": "100"
  }
}
```

Only queries with `exposed: true` are callable through this generic endpoint.

---

## 7. How to create a new project

Do NOT copy the backend source.

Copy only:

```text
config/profiles/minimal_template.yaml
```

For example:

```text
config/profiles/jeddah.yaml
```

Change:

1. `id`
2. datasource environment variables
3. hierarchy mapping
4. entity type mapping
5. SQL
6. realtime config if needed

Then restart the backend.

The API path becomes:

```text
/api/v1/jeddah/...
```

Another project can use:

```text
/api/v1/jazan/...
```

Same frontend can switch profiles.

---

## 8. Why the SQL is configuration instead of field/table mapping

A pure table-name/column-name mapping system looks attractive at first, but ADMS schemas usually require:

- joins
- CASE expressions
- Oracle CONNECT BY
- filtering rules
- multiple tables for one entity
- project-specific naming
- point-table joins
- data cleansing

Therefore this backend uses a stable API contract plus configurable, parameterized SQL.

The backend never accepts raw SQL from the HTTP client.

That provides flexibility without creating a SQL execution API.

---

## 9. Security rules

The backend has several protections:

1. only configured SQL is executed
2. runtime SQL must begin with `SELECT` or `WITH`
3. DML / DDL / PL/SQL keywords are rejected
4. semicolons / multiple statements are rejected
5. parameters use Oracle bind variables
6. arbitrary client parameters are rejected
7. generic named queries require `exposed: true`
8. optional `X-API-Key`
9. production should use a database SELECT-only account

Set:

```env
APP_API_KEY=my-secret
```

Then clients send:

```text
X-API-Key: my-secret
```

---

## 10. Caching

Each configured query has:

```yaml
cache_ttl_seconds: 30
```

Suggested values:

```text
Regions / stations       300-600 sec
Feeders                  120-300 sec
Equipment tree            30-120 sec
Signal definition         30-120 sec
Search                     5-30 sec
Realtime value             0 sec
```

Realtime SQL normally uses `0`.

---

## 11. Recommended production separation

Recommended architecture:

```text
                 FastAPI
                    |
        +-----------+-----------+
        |                       |
        v                       v
 Model / Business Oracle     Realtime DB
        |                       |
station/feeder/equipment     value
signal definition            quality
relationships                timestamp
```

Frontend only talks to FastAPI.

Do not distribute Oracle usernames/passwords to desktop clients.

---

## 12. Next project-specific work

The included `example_oracle.yaml` is intentionally based on fake example tables:

```text
grid_region
grid_station
grid_feeder
grid_equipment
grid_signal
realtime_value
```

Replace those SQL statements with the real ADMS/SEC schema.

The FastAPI code can remain unchanged.
