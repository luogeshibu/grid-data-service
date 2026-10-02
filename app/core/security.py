from fastapi import Header, HTTPException, status

from app.core.settings import get_settings


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """
    Optional API-key protection.
    If APP_API_KEY is empty, authentication is disabled.
    """
    expected = get_settings().api_key
    if not expected:
        return
    if x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key.",
        )
