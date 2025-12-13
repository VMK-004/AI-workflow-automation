"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.core.config import settings
from app.api.routes import auth, workflows, nodes, edges, runs, vectors, execution

app = FastAPI(
    title=settings.APP_NAME,
    description="AI Workflow Builder API",
    version="1.0.0",
    debug=settings.DEBUG,
)

# CORS middleware - Allow specific origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])
app.include_router(nodes.router, prefix="/api/workflows", tags=["nodes"])
app.include_router(edges.router, prefix="/api/workflows", tags=["edges"])
app.include_router(runs.router, prefix="/api/workflows", tags=["runs"])
app.include_router(vectors.router, prefix="/api/vectors", tags=["vectors"])
app.include_router(execution.router, prefix="/api/runs", tags=["execution"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Serve static files (frontend build) - must be after API routes
static_dir = "/app/static"
if os.path.exists(static_dir):
    # Mount static assets (JS, CSS, images, etc. from Vite build)
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    
    # Serve index.html for all non-API routes (SPA routing)
    # This must be the last route to catch all unmatched paths
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Exclude API routes, docs, health check, and static assets
        excluded_prefixes = ["api", "docs", "redoc", "openapi.json", "health", "assets"]
        if any(full_path.startswith(prefix) for prefix in excluded_prefixes):
            return {"error": "Not found"}
        
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"error": "Frontend not built"}
