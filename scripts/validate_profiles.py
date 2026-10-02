from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.profile_manager import profiles


if __name__ == "__main__":
    profiles.load_all()
    loaded = profiles.list()
    print(f"OK: loaded {len(loaded)} enabled profile(s)")
    for p in loaded:
        print(f" - {p.id}: {p.name}")
