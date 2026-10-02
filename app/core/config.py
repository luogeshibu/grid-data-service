from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from app.models.profile import ProfileConfig

_ENV_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)(?::-([^}]*))?\}")


class ApiConfig(BaseModel):
    prefix: str = "/api/v1"
    title: str = "Grid Data Service"
    description: str = "Read-only power-grid data access API"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"


class RuntimeConfig(BaseModel):
    default_profile: str = "jeddah"
    query_timeout_seconds: int = 30
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    trusted_hosts: list[str] = Field(default_factory=lambda: ["*"])
    request_id_header: str = "X-Request-ID"


class ApplicationConfig(BaseModel):
    api: ApiConfig = Field(default_factory=ApiConfig)
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)


def _expand_env(value: Any) -> Any:
    if isinstance(value, str):

        def repl(match: re.Match[str]) -> str:
            key = match.group(1)
            default = match.group(2)
            if key in os.environ:
                return os.environ[key]
            if default is not None:
                return default
            raise RuntimeError(f"Required environment variable '{key}' is not set.")

        return _ENV_PATTERN.sub(repl, value)

    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}

    if isinstance(value, list):
        return [_expand_env(v) for v in value]

    return value


def deep_merge(base: Any, overlay: Any) -> Any:
    if isinstance(base, dict) and isinstance(overlay, dict):
        result = dict(base)
        for key, value in overlay.items():
            result[key] = deep_merge(result[key], value) if key in result else value
        return result
    return overlay


class ConfigStore:
    def __init__(self, config_dir: Path | None = None):
        self.config_dir = config_dir or Path(os.getenv("GRID_CONFIG_DIR", "./config"))
        self.application = ApplicationConfig()
        self._profiles: dict[str, ProfileConfig] = {}

    def load(self) -> None:
        self.application = self._load_application()
        self._profiles = self._load_profiles()

    def _load_application(self) -> ApplicationConfig:
        path = self.config_dir / "application.yaml"
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
        return ApplicationConfig.model_validate(_expand_env(raw or {}))

    def _local_overlay(self, profile_id: str) -> dict[str, Any]:
        for suffix in ("yaml", "yml"):
            path = self.config_dir / "local" / f"{profile_id}.{suffix}"
            if path.exists():
                raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                if not isinstance(raw, dict):
                    raise ValueError(f"Local profile overlay must be a mapping: {path}")
                return raw
        return {}

    def _load_profiles(self) -> dict[str, ProfileConfig]:
        result: dict[str, ProfileConfig] = {}
        profile_dir = self.config_dir / "profiles"
        profile_dir.mkdir(parents=True, exist_ok=True)

        paths = sorted([*profile_dir.glob("*.yaml"), *profile_dir.glob("*.yml")])
        for path in paths:
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if not isinstance(raw, dict):
                raise ValueError(f"Profile must be a mapping: {path}")

            profile_id = str(raw.get("id", "")).strip()
            if not profile_id:
                raise ValueError(f"Profile id is required: {path}")

            raw = deep_merge(raw, self._local_overlay(profile_id))
            raw = _expand_env(raw)
            profile = ProfileConfig.model_validate(raw)

            if not profile.enabled:
                continue
            if profile.id in result:
                raise ValueError(f"Duplicate profile id: {profile.id}")

            result[profile.id] = profile

        return result

    def profiles(self) -> list[ProfileConfig]:
        return list(self._profiles.values())

    def get_profile(self, profile_id: str) -> ProfileConfig:
        try:
            return self._profiles[profile_id]
        except KeyError as exc:
            raise KeyError(f"Unknown profile: {profile_id}") from exc


@lru_cache
def get_config_store() -> ConfigStore:
    store = ConfigStore()
    store.load()
    return store
