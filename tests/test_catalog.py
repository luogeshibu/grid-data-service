import pytest

from app.services.cache import TTLCache
from app.services.catalog_service import CatalogInputError, CatalogService


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("substation:123", ("substation", 123)),
        ("transformer_winding:987654321", ("transformer_winding", 987654321)),
    ],
)
def test_parse_canonical_node_id(value, expected):
    assert CatalogService.parse_node_id(value) == expected


@pytest.mark.parametrize("value", ["123", "substation", "substation:0", ":123"])
def test_parse_canonical_node_id_rejects_invalid_values(value):
    with pytest.raises(CatalogInputError):
        CatalogService.parse_node_id(value)


def test_ttl_cache_has_bounded_size():
    cache = TTLCache(max_entries=2)
    cache.set(("a",), 1, 60)
    cache.set(("b",), 2, 60)
    cache.set(("c",), 3, 60)

    assert cache.get(("a",))[1] is False
    assert cache.get(("b",))[1] is True
    assert cache.get(("c",))[1] is True
