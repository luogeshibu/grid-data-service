from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict

import yaml

from app.core.read_only import validate_read_only_sql
from app.core.settings import get_settings
from app.models.profile import ProfileConfig


_ENV_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)(?::-([^}]*))?\}")


def _expand_env(value):
    if isinstance(value, str):
        def repl(match: re.Match) -> str:
            name = match.group(1)
            default = match.group(2)

            if name in os.environ:
                return os.environ[name]

            if default is not None:
                return default

            raise RuntimeError(
                f"Environment variable '{name}' is required by profile config."
            )

        return _ENV_PATTERN.sub(repl, value)

    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}

    if isinstance(value, list):
        return [_expand_env(v) for v in value]

    return value


class ProfileManager:
    def __init__(self):
        self._profiles: Dict[str, ProfileConfig] = {}

    def _load_file(self, path: Path) -> ProfileConfig:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

        if raw.get("enabled", True) is False:
            return ProfileConfig.model_validate(
                {
                    **raw,
                    "datasources": {
                        name: {
                            **cfg,
                            "user": cfg.get("user", "disabled"),
                            "password": cfg.get("password", "disabled"),
                            "dsn": cfg.get("dsn", "disabled"),
                        }
                        for name, cfg in raw.get("datasources", {}).items()
                    },
                }
            )

        raw = _expand_env(raw)
        profile = ProfileConfig.model_validate(raw)

        for query_name, query in profile.queries.items():
            try:
                validate_read_only_sql(query.sql)
            except ValueError as exc:
                raise ValueError(
                    f"{path.name}: query '{query_name}' failed read-only validation: "
                    f"{exc}"
                ) from exc

        return profile

    def load_all(self) -> None:
        config_dir = Path(get_settings().config_dir)
        profiles_dir = config_dir / "profiles"
        profiles_dir.mkdir(parents=True, exist_ok=True)

        loaded: Dict[str, ProfileConfig] = {}

        paths = sorted(list(profiles_dir.glob("*.yaml")) + list(profiles_dir.glob("*.yml")))

        for path in paths:
            profile = self._load_file(path)
            if profile.enabled:
                if profile.id in loaded:
                    raise ValueError(f"Duplicate profile id: {profile.id}")
                loaded[profile.id] = profile

        self._profiles = loaded

    def reload(self) -> None:
        self.load_all()

    def list(self):
        return list(self._profiles.values())

    def get(self, profile_id: str) -> ProfileConfig:
        try:
            return self._profiles[profile_id]
        except KeyError as exc:
            raise KeyError(f"Unknown profile: {profile_id}") from exc


profiles = ProfileManager()
