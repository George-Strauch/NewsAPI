# from __future__ import annotations
#
# import os
# from typing import List, Optional, Literal, Dict, Any
# from fastapi import FastAPI, Query, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field
# from datetime import datetime
#
#
# APP_TITLE = "News Articles (Public Read-Only API)"
# APP_VERSION = "1.0.0"
#
# app = FastAPI(title=APP_TITLE, version=APP_VERSION)
#
# # CORS: adjust to your needs. Default is permissive read-only.
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=os.getenv("PUBLIC_API_CORS_ORIGINS", "*").split(","),
#     allow_credentials=False,
#     allow_methods=["GET", "HEAD", "OPTIONS"],
#     allow_headers=["*"],
# )
#
# # --------------------------- Pydantic response models --------------------------- #
#
# class Article(BaseModel):
#     url: str
#     title: Optional[str] = None
#     text: Optional[str] = None
#     publish_date: Optional[str] = None
#     author: Optional[str] = None
#     publisher: Optional[str] = None
#     image_urls: Optional[Any] = None
#     valid: Optional[bool] = None
#     reasons: Optional[Any] = None
#     created_at: Optional[str] = None
#     updated_at: Optional[str] = None
#
# class PublisherItem(BaseModel):
#     publisher: str
#     count: int
#
# class CountSummary(BaseModel):
#     total: int
#     valid: int
#     invalid: int
#     unknown: int
#
# class TimeBucketItem(BaseModel):
#     ts: str
#     count: int
#
# class PagedArticles(BaseModel):
#     items: List[Article]
#     limit: int
#     offset: int
#     next_offset: Optional[int] = None
#
# # --------------------------- DB handle (singleton) --------------------------- #
#
# # Let ArticleStorePG read env for PG connection.
# DB = ArticleStorePG(read_only=True)
#
# # --------------------------- Routes --------------------------- #
#
# @app.get("/health", tags=["meta"])
# def health():
#     return {"status": "ok", "version": APP_VERSION}
#
# @app.get("/v1/articles/recent", response_model=List[Article], tags=["articles"])
# def recent_articles(
#     n: int = Query(50, ge=1, le=500),
#     valid: Optional[bool] = Query(None, description="Filter by validity"),
# ):
#     return DB.get_most_recent(n=n, valid_only=valid)
#
# @app.get("/v1/articles", response_model=PagedArticles, tags=["articles"])
# def list_articles(
#     limit: int = Query(50, ge=1, le=500),
#     offset: int = Query(0, ge=0),
#     valid: Optional[bool] = Query(None),
#     date_field: Literal["publish_date", "created_at", "updated_at"] = "publish_date",
#     order: Literal["asc", "desc"] = "desc",
#     start: Optional[str] = Query(None, description="ISO8601 start (inclusive)"),
#     end: Optional[str] = Query(None, description="ISO8601 end (inclusive)"),
#     publisher: Optional[str] = Query(None),
# ):
#     items = DB.list_articles(
#         limit=limit,
#         offset=offset,
#         valid_only=valid,
#         date_field=date_field,
#         order=order,
#         start=start,
#         end=end,
#         publisher=publisher,
#     )
#     next_offset = offset + limit if len(items) == limit else None
#     return {"items": items, "limit": limit, "offset": offset, "next_offset": next_offset}
#
# @app.get("/v1/articles/by-date", response_model=List[Article], tags=["articles"])
# def by_date(
#     start: str = Query(..., description="ISO8601 start (inclusive)"),
#     end: str = Query(..., description="ISO8601 end (inclusive)"),
#     field: Literal["publish_date", "updated_at", "created_at"] = "publish_date",
#     valid: Optional[bool] = Query(None),
# ):
#     by_updated = (field == "updated_at")
#     if field == "created_at":
#         # reuse generic list with date filter for created_at
#         return DB.list_articles(
#             limit=1000,  # cap; caller can page via /v1/articles if needed
#             offset=0,
#             valid_only=valid,
#             date_field="created_at",
#             order="asc",
#             start=start,
#             end=end,
#         )
#     return DB.query_by_date_range(start, end, valid_only=valid, by_updated=by_updated)
#
# @app.get("/v1/articles/by-publisher", response_model=PagedArticles, tags=["articles"])
# def by_publisher(
#     publisher: str = Query(...),
#     limit: int = Query(50, ge=1, le=500),
#     offset: int = Query(0, ge=0),
#     valid: Optional[bool] = Query(None),
#     start: Optional[str] = Query(None, description="ISO8601 start (inclusive)"),
#     end: Optional[str] = Query(None, description="ISO8601 end (inclusive)"),
#     date_field: Literal["publish_date", "created_at", "updated_at"] = "publish_date",
#     order: Literal["asc", "desc"] = "desc",
# ):
#     items = DB.query_by_publisher(
#         publisher=publisher,
#         limit=limit,
#         offset=offset,
#         valid_only=valid,
#         start=start,
#         end=end,
#         date_field=date_field,
#         order=order,
#     )
#     next_offset = offset + limit if len(items) == limit else None
#     return {"items": items, "limit": limit, "offset": offset, "next_offset": next_offset}
#
# @app.get("/v1/articles/{url}", response_model=Article, tags=["articles"])
# def get_article(url: str, valid: Optional[bool] = Query(None)):
#     item = DB.get(url, valid_only=valid)
#     if not item:
#         raise HTTPException(status_code=404, detail="Article not found")
#     return item
#
# @app.get("/v1/publishers", response_model=List[PublisherItem], tags=["publishers"])
# def publishers(min_count: int = Query(0, ge=0)):
#     return DB.list_publishers(min_count=min_count)
#
# @app.get("/v1/publishers/{publisher}/articles", response_model=PagedArticles, tags=["publishers"])
# def publisher_articles(
#     publisher: str,
#     limit: int = Query(50, ge=1, le=500),
#     offset: int = Query(0, ge=0),
#     valid: Optional[bool] = Query(None),
#     start: Optional[str] = Query(None),
#     end: Optional[str] = Query(None),
#     date_field: Literal["publish_date", "created_at", "updated_at"] = "publish_date",
#     order: Literal["asc", "desc"] = "desc",
# ):
#     # thin wrapper around /v1/articles/by-publisher with path param
#     items = DB.query_by_publisher(
#         publisher=publisher,
#         limit=limit,
#         offset=offset,
#         valid_only=valid,
#         start=start,
#         end=end,
#         date_field=date_field,
#         order=order,
#     )
#     next_offset = offset + limit if len(items) == limit else None
#     return {"items": items, "limit": limit, "offset": offset, "next_offset": next_offset}
#
# @app.get("/v1/stats/counts", response_model=CountSummary, tags=["stats"])
# def stats_counts():
#     return DB.counts()
#
# @app.get("/v1/stats/time-buckets", response_model=List[TimeBucketItem], tags=["stats"])
# def stats_time_buckets(
#     start: str = Query(...),
#     end: str = Query(...),
#     field: Literal["publish_date", "created_at", "updated_at"] = "publish_date",
#     bucket: Literal["hour", "day", "week", "month"] = "day",
#     valid: Optional[bool] = Query(None),
#     publisher: Optional[str] = Query(None),
# ):
#     return DB.time_buckets(
#         start=start,
#         end=end,
#         field=field,
#         bucket=bucket,
#         valid_only=valid,
#         publisher=publisher,
#     )
