from __future__ import annotations

from decimal import Decimal
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class DomainModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CatalogNode(DomainModel):
    id: str
    parent_id: str | None = None
    node_type: str
    entity_type: str
    source_id: str
    code: str | None = None
    name: str
    description: str | None = None
    level: int = Field(ge=0)
    sort_order: int = 0
    has_children: bool = False
    status: int | None = None
    run_state: int | None = None


class EquipmentSummary(DomainModel):
    id: str
    entity_type: str
    source_id: str
    code: str | None = None
    name: str
    description: str | None = None
    station_id: str | None = None
    bay_id: str | None = None
    voltage_level_id: str | None = None
    base_voltage_id: str | None = None
    status: int | None = None
    run_state: int | None = None
    rdf_id: str | None = None


class EquipmentDetail(EquipmentSummary):
    attributes: dict[str, Any] = Field(default_factory=dict)


class EquipmentSignal(DomainModel):
    id: str
    signal_type: str
    source_id: str
    code: str | None = None
    name: str | None = None
    data_type: int | None = None
    value: Decimal | int | float | str | None = None
    quality: int | None = None
    changed_at: str | None = None


class TopologyRelation(DomainModel):
    id: str
    source_id: str
    target_id: str | None = None
    breaker_id: str | None = None
    breaker_type: int | None = None
    relation_type: str = "topology"


T = TypeVar("T")


class PageMeta(DomainModel):
    offset: int = Field(ge=0)
    limit: int = Field(ge=1)
    returned: int = Field(ge=0)
    has_more: bool


class PageResult(DomainModel, Generic[T]):
    items: list[T]
    meta: PageMeta
