# src/api/__init__.py
from __future__ import annotations

from fastapi import APIRouter

from . import  articles
from . import extras

# Root router for all /api endpoints
api_router = APIRouter(prefix="/api")

# Plug sub-routers into the root API router
# api_router.include_router(health.router)
api_router.include_router(articles.router)
api_router.include_router(extras.router)

__all__ = ["api_router"]
