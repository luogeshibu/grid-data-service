from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.config import ConfigStore


def main() -> int:
    store = ConfigStore(ROOT / "config")
    store.load()

    profiles = store.profiles()
    if not profiles:
        raise RuntimeError("No enabled profiles found.")

    print("Configuration: OK")
    print("Profiles:", ", ".join(p.id for p in profiles))
    print("Oracle configuration file: config/local/jeddah.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
