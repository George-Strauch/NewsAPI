from __future__ import annotations
from fastapi import APIRouter, HTTPException
from src.api.dll.article_interface import ArticleInterface

router = APIRouter(tags=["articles"])
ARTICLE_INTERFACE = ArticleInterface.get()


@router.get("/articles/recent")
async def recent_articles(n=10) -> dict:
    # placeholder – wire to your DB later
    return {"results": ARTICLE_INTERFACE.article_store.get_most_recent(n, valid_only=True)}


@router.get("/articles/{article_id}")
async def get_article(article_id: int) -> dict:
    # placeholder example
    if article_id < 0:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"id": article_id, "title": f"Article {article_id}"}
