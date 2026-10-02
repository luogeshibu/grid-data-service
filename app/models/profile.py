from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator


class PoolConfig(BaseModel):
    min: int = 1
    max: int = 5
    increment: int = 1
    timeout: int = 60


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
    cache_ttl_seconds: int = 0
    exposed: bool = False
    allowed_params: List[str] = Field(default_factory=list)
    required_params: List[str] = Field(default_factory=list)


class HierarchyConfig(BaseModel):
    root_query: str = "tree_root"
    children_queries: Dict[str, str] = Field(default_factory=dict)


class EntityTypeConfig(BaseModel):
    detail_query: Optional[str] = None
    children_query: Optional[str] = None
    signals_query: Optional[str] = None
    path_query: Optional[str] = None
    upstream_query: Optional[str] = None
    downstream_query: Optional[str] = None
    topology_query: Optional[str] = None


class SearchConfig(BaseModel):
    query: str = "search"
    max_limit: int = 200
    default_limit: int = 50


class RealtimeConfig(BaseModel):
    enabled: bool = False
    batch_query: Optional[str] = None
    signal_query: Optional[str] = None
    max_batch_size: int = 1000


class ProfileConfig(BaseModel):
    id: str
    name: str
    description: str = ""
    enabled: bool = True

    datasources: Dict[str, DataSourceConfig]
    queries: Dict[str, QueryConfig]

    hierarchy: HierarchyConfig = Field(default_factory=HierarchyConfig)
    entities: Dict[str, EntityTypeConfig] = Field(default_factory=dict)
    search: SearchConfig = Field(default_factory=SearchConfig)
    realtime: RealtimeConfig = Field(default_factory=RealtimeConfig)

    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_references(self):
        for name, q in self.queries.items():
            if q.source not in self.datasources:
                raise ValueError(
                    f"Query '{name}' references unknown datasource '{q.source}'."
                )

        referenced = [self.hierarchy.root_query, self.search.query]
        referenced += list(self.hierarchy.children_queries.values())

        if self.realtime.enabled:
            if self.realtime.batch_query:
                referenced.append(self.realtime.batch_query)
            if self.realtime.signal_query:
                referenced.append(self.realtime.signal_query)

        for entity_cfg in self.entities.values():
            referenced.extend(
                [
                    entity_cfg.detail_query,
                    entity_cfg.children_query,
                    entity_cfg.signals_query,
                    entity_cfg.path_query,
                    entity_cfg.upstream_query,
                    entity_cfg.downstream_query,
                    entity_cfg.topology_query,
                ]
            )

        for qname in [x for x in referenced if x]:
            if qname not in self.queries:
                raise ValueError(f"Referenced query '{qname}' does not exist.")

        return self
