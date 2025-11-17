from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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

BASE_DIR = Path(__file__).resolve().parent              # .../newsAPI/src
PROJECT_ROOT = BASE_DIR.parent                          # .../newsAPI
FRONTEND_DIST = PROJECT_ROOT / "NewsFE" / "dist"        # .../newsAPI/NewsFE/dist
INDEX_HTML = FRONTEND_DIST / "index.html"

logger.info("BASE_DIR=%s", BASE_DIR)
logger.info("FRONTEND_DIST=%s", FRONTEND_DIST)
logger.info("INDEX_HTML=%s", INDEX_HTML)

assert INDEX_HTML.exists(), "index.html not found at %s. Did you run `npm run build` in NewsFE?"

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


@api_router.get("/articles/latest")
async def latest_articles():
    # placeholder – wire to your DB later
    return {"articles": []}


app.include_router(api_router)

# --------------------------------------------------------------------
# Frontend static assets + SPA fallback
# --------------------------------------------------------------------

if FRONTEND_DIST.exists() and INDEX_HTML.exists():
    # Serve Vite-built assets under /assets (JS, CSS, etc.)
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        logger.info("Mounting frontend assets from %s at /assets", assets_dir)
        app.mount(
            "/assets",
            StaticFiles(directory=str(assets_dir), html=False),
            name="assets",
        )
    else:
        assert False, "assets directory not found"

    # Optional: favicon, vite.svg, etc., if present
    favicon_path = FRONTEND_DIST / "favicon.ico"
    vite_svg_path = FRONTEND_DIST / "vite.svg"

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        if favicon_path.exists():
            return FileResponse(favicon_path)
        raise HTTPException(status_code=404, detail="Not Found")

    @app.get("/vite.svg", include_in_schema=False)
    async def vite_svg():
        if vite_svg_path.exists():
            return FileResponse(vite_svg_path)
        raise HTTPException(status_code=404, detail="Not Found")

    # Root route: serve index.html
    @app.get("/", include_in_schema=False)
    async def spa_root():
        """
        Always serve the React SPA for the root path.
        """
        return FileResponse(INDEX_HTML)

    # Catch-all: any non-/api path returns index.html so React Router can handle it.
    # Because /api routes are registered above, they take precedence.
    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_catch_all(full_path: str):
        """
        Serve the React SPA for any path that isn't handled by /api.
        This fixes refresh / deep-linking on /home, /apidocs, etc.
        """
        # Defensive: if someone somehow hits /api/* here, 404 instead of serving SPA
        if full_path.startswith("api/") or full_path == "api":
            raise HTTPException(status_code=404, detail="Not Found")

        return FileResponse(INDEX_HTML)
else:
    logger.warning(
        "Frontend dist directory or index.html missing; "
        "React app will not be served. FRONTEND_DIST=%s",
        FRONTEND_DIST,
    )
