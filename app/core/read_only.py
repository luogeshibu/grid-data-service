from __future__ import annotations

import re


_FORBIDDEN_PATTERNS = [
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bMERGE\b",
    r"\bUPSERT\b",
    r"\bCREATE\b",
    r"\bALTER\b",
    r"\bDROP\b",
    r"\bTRUNCATE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bCOMMENT\b",
    r"\bAUDIT\b",
    r"\bNOAUDIT\b",
    r"\bCALL\b",
    r"\bEXEC(?:UTE)?\b",
    r"\bBEGIN\b",
    r"\bDECLARE\b",
    r"\bCOMMIT\b",
    r"\bROLLBACK\b",
    r"\bSAVEPOINT\b",
    r"\bLOCK\s+TABLE\b",
    r"\bFOR\s+UPDATE\b",
    r"\bDBMS_[A-Z0-9_]+\b",
    r"\bUTL_[A-Z0-9_]+\b",
]


def _strip_comments(sql: str) -> str:
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    sql = re.sub(r"--[^\n\r]*", " ", sql)
    return sql


def validate_read_only_sql(sql: str) -> str:
    """
    Defense-in-depth guard. The database account should ALSO be read-only.

    Allowed:
      SELECT ...
      WITH ... SELECT ...

    Rejected:
      DML / DDL / PL/SQL / FOR UPDATE / multiple statements / semicolon.
    """
    if not sql or not sql.strip():
        raise ValueError("SQL is empty.")

    normalized = re.sub(r"\s+", " ", _strip_comments(sql).strip()).upper()

    if ";" in normalized:
        raise ValueError("Semicolons / multiple statements are not allowed.")

    if not (normalized.startswith("SELECT ") or normalized.startswith("WITH ")):
        raise ValueError("Only SELECT or WITH ... SELECT statements are allowed.")

    for pattern in _FORBIDDEN_PATTERNS:
        if re.search(pattern, normalized, flags=re.I):
            raise ValueError(f"Read-only SQL check rejected pattern: {pattern}")

    if normalized.startswith("WITH ") and " SELECT " not in f" {normalized} ":
        raise ValueError("WITH statement must contain a SELECT.")

    return sql
