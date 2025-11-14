#!/usr/bin/env python
"""
Usage:

    # Option 1: run via Python
    python main.py

    # Option 2: run via uvicorn (recommended in production)
    uvicorn main:app --host 0.0.0.0 --port 8000

This file:
- Defines the FastAPI app and routes (your existing code).
- Starts scheduled threaded jobs on startup and stops them on shutdown.
"""

from __future__ import annotations

import logging
import os
import uvicorn



def setup_logging() -> None:
    """
    Basic logging setup for the entire application.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(threadName)s] %(name)s: %(message)s",
    )


setup_logging()
logger = logging.getLogger("main")


@app.on_event("startup")
def on_startup() -> None:
    print("Starting up...")


@app.on_event("shutdown")
def on_shutdown() -> None:
    print("Shutting down...")

# ---------------------------------------------------------------------------
# Local entrypoint (for `python main.py`)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logger.info("Starting uvicorn from main.py")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=False,  # set True for local dev hot-reload if desired
    )
