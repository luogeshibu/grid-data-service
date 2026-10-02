from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class NamedQueryRequest(BaseModel):
    params: Dict[str, Any] = Field(default_factory=dict)


class RealtimeBatchRequest(BaseModel):
    point_ids: List[str] = Field(min_length=1)


class ReloadResponse(BaseModel):
    status: str
    profiles: int
