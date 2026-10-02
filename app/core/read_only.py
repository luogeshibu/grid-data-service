from __future__ import annotations

import re

_FORBIDDEN = (
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
)


def _without_comments(sql: str) -> str:
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    return re.sub(r"--[^\n\r]*", " ", sql)


def validate_read_only_sql(sql: str) -> str:
    if not sql or not sql.strip():
        raise ValueError("SQL is empty.")

    normalized = re.sub(r"\s+", " ", _without_comments(sql).strip()).upper()

    if ";" in normalized:
        raise ValueError("Multiple statements / semicolons are not allowed.")

    if not (normalized.startswith("SELECT ") or normalized.startswith("WITH ")):
        raise ValueError("Only SELECT and WITH ... SELECT statements are allowed.")

    for pattern in _FORBIDDEN:
        if re.search(pattern, normalized, flags=re.I):
            raise ValueError(f"Read-only SQL policy rejected: {pattern}")

    return sql
