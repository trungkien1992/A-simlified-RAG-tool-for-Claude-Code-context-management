#!/usr/bin/env python3
"""
Security module for Astra RAG system
"""

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from .config import settings

# API Key header configuration
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)


async def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Validate API key from X-API-KEY header

    Args:
        api_key: API key from request header

    Returns:
        str: Validated API key

    Raises:
        HTTPException: If API key is missing or invalid
    """
    print(f"[DEBUG] Received API key: '{api_key}' | Expected: '{settings.api_key}'")
    if not api_key:
        raise HTTPException(
            status_code=403,
            detail="API key is required. Please provide X-API-KEY header.",
        )

    if api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API key. Access denied.")

    return api_key


# Dependency for securing endpoints
secure_endpoint = Security(get_api_key)
