# src/api/__init__.py
from __future__ import annotations

from fastapi import APIRouter

from . import  articles

# Root router for all /api endpoints
api_router = APIRouter(prefix="/api")

# Plug sub-routers into the root API router
# api_router.include_router(health.router)
api_router.include_router(articles.router)

__all__ = ["api_router"]
