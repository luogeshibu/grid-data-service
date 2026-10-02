from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class NamedQueryRequest(BaseModel):
    params: dict[str, Any] = Field(default_factory=dict)


class RealtimeBatchRequest(BaseModel):
    point_ids: list[str] = Field(min_length=1)


class ErrorBody(BaseModel):
    code: str
    message: str
    request_id: str | None = None
