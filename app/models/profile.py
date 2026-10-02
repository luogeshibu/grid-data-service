from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from app.core.read_only import validate_read_only_sql


class PoolConfig(BaseModel):
    min: int = Field(default=1, ge=0)
    max: int = Field(default=8, ge=1)
    increment: int = Field(default=1, ge=0)
    timeout: int = Field(default=60, ge=1)
    wait_timeout_ms: int = Field(default=10_000, ge=1)


class DataSourceConfig(BaseModel):
    driver: Literal["oracle"] = "oracle"
    user: str
    password: str
    dsn: str
    pool: PoolConfig = Field(default_factory=PoolConfig)


class QueryConfig(BaseModel):
    source: str
    sql: str
    result: Literal["many", "one", "scalar"] = "many"
    cache_ttl_seconds: int = Field(default=0, ge=0)
    exposed: bool = False
    allowed_params: list[str] = Field(default_factory=list)
    required_params: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_sql(self):
        validate_read_only_sql(self.sql)
        if not set(self.required_params).issubset(set(self.allowed_params)):
            raise ValueError("required_params must be a subset of allowed_params")
        return self


class HierarchyConfig(BaseModel):
    root_query: str = "tree_root"
    children_queries: dict[str, str] = Field(default_factory=dict)


class CatalogConfig(BaseModel):
    """Typed domain configuration for the power equipment catalog."""

    enabled: bool = True
    source: str = "model"
    default_page_size: int = Field(default=50, ge=1, le=500)
    max_page_size: int = Field(default=200, ge=1, le=5000)
    cache_ttl_seconds: int = Field(default=15, ge=0)


class EntityTypeConfig(BaseModel):
    detail_query: str | None = None
    children_query: str | None = None
    signals_query: str | None = None
    path_query: str | None = None
    upstream_query: str | None = None
    downstream_query: str | None = None
    topology_query: str | None = None


class SearchConfig(BaseModel):
    query: str = "search"
    max_limit: int = Field(default=200, ge=1)
    default_limit: int = Field(default=50, ge=1)


class RealtimeConfig(BaseModel):
    enabled: bool = False
    signal_query: str | None = None
    batch_query: str | None = None
    max_batch_size: int = Field(default=1000, ge=1)


class ProfileConfig(BaseModel):
    id: str
    name: str
    description: str = ""
    enabled: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    datasources: dict[str, DataSourceConfig]
    queries: dict[str, QueryConfig]

    catalog: CatalogConfig = Field(default_factory=CatalogConfig)
    hierarchy: HierarchyConfig = Field(default_factory=HierarchyConfig)
    entities: dict[str, EntityTypeConfig] = Field(default_factory=dict)
    search: SearchConfig = Field(default_factory=SearchConfig)
    realtime: RealtimeConfig = Field(default_factory=RealtimeConfig)

    @model_validator(mode="after")
    def validate_references(self):
        for query_name, query in self.queries.items():
            if query.source not in self.datasources:
                raise ValueError(
                    f"Query '{query_name}' references unknown datasource '{query.source}'."
                )

        if self.catalog.source not in self.datasources:
            raise ValueError(f"Catalog references unknown datasource '{self.catalog.source}'.")

        refs = [self.hierarchy.root_query, self.search.query]
        refs.extend(self.hierarchy.children_queries.values())

        for entity in self.entities.values():
            refs.extend(
                q
                for q in (
                    entity.detail_query,
                    entity.children_query,
                    entity.signals_query,
                    entity.path_query,
                    entity.upstream_query,
                    entity.downstream_query,
                    entity.topology_query,
                )
                if q
            )

        if self.realtime.enabled:
            refs.extend(
                q
                for q in (
                    self.realtime.signal_query,
                    self.realtime.batch_query,
                )
                if q
            )

        missing = sorted({q for q in refs if q not in self.queries})
        if missing:
            raise ValueError(f"Referenced queries do not exist: {missing}")

        return self
