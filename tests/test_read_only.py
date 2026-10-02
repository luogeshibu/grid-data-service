import pytest

from app.core.read_only import validate_read_only_sql


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM dual",
        "WITH x AS (SELECT 1 a FROM dual) SELECT * FROM x",
    ],
)
def test_allow_select(sql):
    assert validate_read_only_sql(sql) == sql


@pytest.mark.parametrize(
    "sql",
    [
        "UPDATE t SET a=1",
        "DELETE FROM t",
        "SELECT * FROM t FOR UPDATE",
        "BEGIN NULL; END",
        "SELECT * FROM dual; DELETE FROM t",
    ],
)
def test_reject_write(sql):
    with pytest.raises(ValueError):
        validate_read_only_sql(sql)
