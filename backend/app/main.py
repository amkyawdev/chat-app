"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .routes import auth_router, user_router, chat_router, group_router, system_router
from .sockets.ws import websocket_endpoint


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # TODO: Start worker and scheduler
    # from .system import worker, batch_scheduler
    # await worker.start()
    # await batch_scheduler.start()
    
    yield
    
    # Shutdown
    print("Shutting down...")
    # await worker.stop()
    # await batch_scheduler.stop()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Chat application with async message processing",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(group_router, prefix="/api")
app.include_router(system_router, prefix="/api")


# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_route(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time notifications."""
    await websocket_endpoint(websocket, user_id)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


# Import all routes to ensure they're registered
__all__ = ["app"]