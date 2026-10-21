"""
security.py - Security and Access Control Dependencies for Energy Mirror.

Provides:
- Constant-time secret comparison (secrets.compare_digest) to prevent timing attacks.
- Administrative mutation verification (verify_admin_access):
    1. If ADMIN_API_KEY is configured in the environment:
       Enforces header `X-Admin-Key` matching `ADMIN_API_KEY` via constant-time comparison.
       Rejects missing or invalid tokens with HTTP 401 Unauthorized.
    2. If ADMIN_API_KEY is NOT configured:
       - In production: Rejects with HTTP 403 Forbidden.
       - In development/testing: Restricts mutations strictly to local loopback hosts (127.0.0.1, ::1, localhost, testclient).
         Remote IP addresses are rejected with HTTP 403 Forbidden.
- IP extraction accounting for X-Forwarded-For if behind a reverse proxy.
"""

import secrets
from typing import Optional
from fastapi import Header, HTTPException, Request, status
from app.config import settings

LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost", "testclient"}


def get_client_ip(request: Request) -> str:
    """Extract client IP, taking X-Forwarded-For into account if behind a reverse proxy."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # Take the leftmost (original client) IP in the chain
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def verify_admin_access(
    request: Request,
    x_admin_key: Optional[str] = Header(default=None, alias="X-Admin-Key"),
) -> bool:
    """
    Enforce authorization for administrative mutations (POST, PATCH, DELETE /appliances).

    Strategy:
    - If ADMIN_API_KEY is set in environment:
        Requires X-Admin-Key header matching ADMIN_API_KEY via secrets.compare_digest.
        Missing or incorrect key -> 401 Unauthorized.
    - If ADMIN_API_KEY is NOT set:
        - In production: 403 Forbidden (administrative mutations disabled without explicit key).
        - In development / testing:
            Allow ONLY if request originates from local loopback (127.0.0.1, ::1, localhost, testclient).
            Remote clients -> 403 Forbidden.
    """
    if settings.ADMIN_API_KEY:
        if not x_admin_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing X-Admin-Key header. Administrative mutation requires authentication.",
            )
        if not secrets.compare_digest(x_admin_key, settings.ADMIN_API_KEY):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid X-Admin-Key header. Unauthorized administrative mutation.",
            )
        return True

    # If ADMIN_API_KEY is not configured:
    if settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative mutations are disabled in production when ADMIN_API_KEY is not configured.",
        )

    # In development/test mode: restrict to loopback
    client_ip = get_client_ip(request)
    if client_ip not in LOOPBACK_HOSTS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Remote administrative access from '{client_ip}' is forbidden. "
                "In development mode without an ADMIN_API_KEY, appliance administration is restricted to local loopback. "
                "Configure ADMIN_API_KEY in .env to allow authorized remote administration."
            ),
        )

    return True
