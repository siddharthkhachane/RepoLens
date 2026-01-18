"""FastAPI application setup."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .api import router

# Create app
app = FastAPI(title="RepoLens", description="Repository analysis backend")

# Include router
app.include_router(router)


# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    """Serve the main HTML page."""
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"message": "Welcome to RepoLens API"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"ok": True}
