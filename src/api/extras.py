from __future__ import annotations
from fastapi import APIRouter, HTTPException
from src.api.dll.article_interface import ArticleInterface
from src.api.dll.source_interface import SourceInterface

router = APIRouter(tags=["extras"])
ARTICLE_INTERFACE = ArticleInterface.get()
SOURCE_INTERFACE = SourceInterface.get()


@router.get("/stats/counts", tags=["stats"])
async def stats_counts():
    article_counts = ARTICLE_INTERFACE.get_counts()
    domain_counts = SOURCE_INTERFACE.get_domain_counts()
    return {
        "total_articles": article_counts,
        "total_domains": domain_counts,
    }
