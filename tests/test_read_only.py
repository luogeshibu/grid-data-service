import pytest

from app.core.read_only import validate_read_only_sql


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM dual",
        "WITH x AS (SELECT 1 AS n FROM dual) SELECT * FROM x",
    ],
)
def test_read_only_allows_queries(sql):
    assert validate_read_only_sql(sql) == sql


@pytest.mark.parametrize(
    "sql",
    [
        "UPDATE t SET a = 1",
        "DELETE FROM t",
        "INSERT INTO t VALUES (1)",
        "MERGE INTO t USING s ON (1=1) WHEN MATCHED THEN UPDATE SET a=1",
        "SELECT * FROM t FOR UPDATE",
        "BEGIN NULL; END",
    ],
)
def test_read_only_rejects_writes(sql):
    with pytest.raises(ValueError):
        validate_read_only_sql(sql)
