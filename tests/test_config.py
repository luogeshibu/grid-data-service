from pathlib import Path

from app.core.config import ConfigStore


def test_jeddah_profile_loads():
    root = Path(__file__).resolve().parents[1]
    store = ConfigStore(root / "config")
    store.load()

    profile = store.get_profile("jeddah")
    source = profile.datasources["model"]

    assert source.user == "d5000"
    assert source.dsn == "172.16.21.45:1521/jedup8000"
    assert source.password
