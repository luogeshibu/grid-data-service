from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any, TypeVar

from app.domain.models import (
    CatalogNode,
    EquipmentDetail,
    EquipmentSignal,
    EquipmentSummary,
    PageMeta,
    PageResult,
    TopologyRelation,
)
from app.models.profile import ProfileConfig
from app.repositories.catalog_repository import CatalogRepository
from app.services.cache import TTLCache


class CatalogInputError(ValueError):
    pass


T = TypeVar("T")


class CatalogService:
    def __init__(
        self,
        profiles: dict[str, ProfileConfig],
        repository: CatalogRepository,
        cache: TTLCache,
    ):
        self.profiles = profiles
        self.repository = repository
        self.cache = cache

    def profile(self, profile_id: str) -> ProfileConfig:
        try:
            profile = self.profiles[profile_id]
        except KeyError as exc:
            raise KeyError(f"Unknown profile: {profile_id}") from exc
        if not profile.catalog.enabled:
            raise KeyError(f"Catalog is disabled for profile '{profile_id}'")
        return profile

    @staticmethod
    def _limit(profile: ProfileConfig, limit: int | None) -> int:
        return min(limit or profile.catalog.default_page_size, profile.catalog.max_page_size)

    @staticmethod
    def _validate_entity_type(entity_type: str) -> None:
        if entity_type not in CatalogRepository.supported_entity_types():
            raise CatalogInputError(f"Unsupported entity type: {entity_type}")

    @staticmethod
    def _page(
        rows: list[dict[str, Any]], offset: int, limit: int, mapper: Callable[[dict[str, Any]], T]
    ) -> PageResult[T]:
        items = [mapper(row) for row in rows[:limit]]
        return PageResult(
            items=items,
            meta=PageMeta(
                offset=offset,
                limit=limit,
                returned=len(items),
                has_more=len(rows) > limit,
            ),
        )

    @staticmethod
    def _cache_key(*parts: Any) -> tuple[str, ...]:
        return tuple(json.dumps(part, sort_keys=True, default=str) for part in parts)

    @staticmethod
    def _node(row: dict[str, Any]) -> CatalogNode:
        return CatalogNode.model_validate(row)

    @staticmethod
    def _summary(row: dict[str, Any]) -> EquipmentSummary:
        return EquipmentSummary.model_validate(
            {
                "id": f"{row['entity_type']}:{row['source_id']}",
                **row,
            }
        )

    @staticmethod
    def _detail(row: dict[str, Any]) -> EquipmentDetail:
        attributes = {
            key.removeprefix("attr_"): value
            for key, value in row.items()
            if key.startswith("attr_") and value is not None
        }
        common = {key: value for key, value in row.items() if not key.startswith("attr_")}
        return EquipmentDetail.model_validate(
            {
                "id": f"{row['entity_type']}:{row['source_id']}",
                **common,
                "attributes": attributes,
            }
        )

    async def roots(
        self, profile_id: str, offset: int, limit: int | None
    ) -> PageResult[CatalogNode]:
        profile = self.profile(profile_id)
        resolved_limit = self._limit(profile, limit)
        key = self._cache_key("roots", profile_id, offset, resolved_limit)
        cached, found = self.cache.get(key)
        if found:
            return cached
        rows = await self.repository.roots(profile_id, offset, resolved_limit)
        result = self._page(rows, offset, resolved_limit, self._node)
        self.cache.set(key, result, profile.catalog.cache_ttl_seconds)
        return result

    async def children(
        self,
        profile_id: str,
        node_id: str,
        offset: int,
        limit: int | None,
    ) -> PageResult[CatalogNode]:
        profile = self.profile(profile_id)
        node_type, source_id = self.parse_node_id(node_id)
        resolved_limit = self._limit(profile, limit)
        key = self._cache_key(
            "children", profile_id, node_type, source_id, offset, resolved_limit
        )
        cached, found = self.cache.get(key)
        if found:
            return cached
        rows = await self.repository.children(
            profile_id, node_type, source_id, offset, resolved_limit
        )
        result = self._page(rows, offset, resolved_limit, self._node)
        self.cache.set(key, result, profile.catalog.cache_ttl_seconds)
        return result

    async def detail(
        self,
        profile_id: str,
        entity_type: str,
        entity_id: int,
    ) -> EquipmentDetail:
        self.profile(profile_id)
        self._validate_entity_type(entity_type)
        row = await self.repository.detail(profile_id, entity_type, entity_id)
        if row is None:
            raise KeyError(f"Equipment not found: {entity_type}:{entity_id}")
        return self._detail(row)

    async def search(
        self,
        profile_id: str,
        text: str,
        entity_type: str | None,
        offset: int,
        limit: int | None,
    ) -> PageResult[CatalogNode]:
        profile = self.profile(profile_id)
        resolved_limit = self._limit(profile, limit)
        key = self._cache_key("search", profile_id, text, entity_type, offset, resolved_limit)
        cached, found = self.cache.get(key)
        if found:
            return cached
        rows = await self.repository.search(
            profile_id, text.strip(), entity_type, offset, resolved_limit
        )
        result = self._page(rows, offset, resolved_limit, self._node)
        self.cache.set(key, result, profile.catalog.cache_ttl_seconds)
        return result

    async def signals(
        self,
        profile_id: str,
        entity_type: str,
        entity_id: int,
        limit: int,
    ) -> list[EquipmentSignal]:
        self.profile(profile_id)
        self._validate_entity_type(entity_type)
        rows = await self.repository.signals(profile_id, entity_type, entity_id, limit)
        return [EquipmentSignal.model_validate(row) for row in rows]

    async def topology(
        self,
        profile_id: str,
        entity_type: str,
        entity_id: int,
        limit: int,
    ) -> list[TopologyRelation]:
        self.profile(profile_id)
        self._validate_entity_type(entity_type)
        rows = await self.repository.topology(profile_id, entity_id, limit)
        return [TopologyRelation.model_validate(row) for row in rows]

    @classmethod
    def parse_node_id(cls, node_id: str) -> tuple[str, int]:
        try:
            node_type, raw_id = node_id.split(":", 1)
            source_id = int(raw_id)
        except (TypeError, ValueError) as exc:
            raise CatalogInputError(
                "node_id must use the canonical form '<node_type>:<numeric_id>'"
            ) from exc
        if not node_type or source_id <= 0:
            raise CatalogInputError("node_id contains an invalid type or numeric id")
        return node_type, source_id
