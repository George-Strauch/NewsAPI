from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# --------------------------------------------------------------------
# Logging setup
# --------------------------------------------------------------------

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("app")

# --------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------

# This file is src/main_ex.py
BASE_DIR = Path(__file__).resolve().parent              # .../newsAPI/src
PROJECT_ROOT = BASE_DIR.parent                          # .../newsAPI
FRONTEND_DIST = PROJECT_ROOT / "NewsFE" / "dist"        # .../newsAPI/NewsFE/dist
INDEX_HTML = FRONTEND_DIST / "index.html"

logger.info("BASE_DIR=%s", BASE_DIR)
logger.info("FRONTEND_DIST=%s", FRONTEND_DIST)
logger.info("INDEX_HTML=%s", INDEX_HTML)

if not INDEX_HTML.exists():
    logger.warning("index.html not found at %s. Did you run `npm run build` in NewsFE?", INDEX_HTML)

# --------------------------------------------------------------------
# FastAPI app
# --------------------------------------------------------------------

app = FastAPI(title="React + FastAPI App")

# CORS (for dev; adjust for prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------
# API router (all under /api)
# --------------------------------------------------------------------

api_router = APIRouter(prefix="/api", tags=["api"])


@api_router.get("/health")
async def health_check():
    return {"status": "ok"}


# Example sub-route: /api/articles/latest
@api_router.get("/articles/latest")
async def latest_articles():
    # placeholder – wire to your DB later
    return {"articles": []}


app.include_router(api_router)

# --------------------------------------------------------------------
# Frontend static serving (Vite build)
# --------------------------------------------------------------------

# Mount the ENTIRE dist directory at "/".
# - /              -> dist/index.html     (via html=True)
# - /assets/...    -> dist/assets/...
# - /vite.svg      -> dist/vite.svg
#
# Because we included the /api router above, any /api/* paths are handled
# by FastAPI, and everything else falls through to the React app.
if FRONTEND_DIST.exists() and INDEX_HTML.exists():
    logger.info("Mounting frontend from %s at /", FRONTEND_DIST)
    app.mount(
        "/",
        StaticFiles(directory=str(FRONTEND_DIST), html=True),
        name="frontend",
    )
else:
    logger.warning(
        "Frontend dist directory or index.html missing; "
        "React app will not be served. FRONTEND_DIST=%s",
        FRONTEND_DIST,
    )
