"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])
app.include_router(nodes.router, prefix="/api/workflows", tags=["nodes"])
app.include_router(edges.router, prefix="/api/workflows", tags=["edges"])
app.include_router(runs.router, prefix="/api/workflows", tags=["runs"])
app.include_router(vectors.router, prefix="/api/vectors", tags=["vectors"])
app.include_router(execution.router, prefix="/api/runs", tags=["execution"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AI Workflow Builder API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
