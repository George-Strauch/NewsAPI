from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI
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
    # If you serve the frontend and API from the same origin (localhost:8000),
    # CORS isn't strictly necessary for that, but keep this if you also hit
    # the API from localhost:5173 or another domain.
    # allow_origins=[
    #     "http://localhost:5173",
    #     "http://localhost:8000",
    #     "https://yourdomain.com",
    # ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


# --------------------------------------------------------------------
# Frontend static serving (Vite build)
# --------------------------------------------------------------------

# Important: we mount the ENTIRE dist directory at "/".
# This way:
#   /              -> dist/index.html     (via html=True)
#   /assets/...    -> dist/assets/...
#   /vite.svg      -> dist/vite.svg
#
# The API routes are defined BEFORE this mount, so /api/* requests
# will be handled by FastAPI, not by StaticFiles.
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
