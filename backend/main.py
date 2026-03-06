from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.config import settings
import os
import time

# Deferred imports to avoid blocking startup
from api.detection import router as detection_router
from api.honeypot import router as honeypot_router
from api.inoculation import router as inoculation_router
from api.voice import router as voice_router
from api.system import router as system_router
from api.auth import router as auth_router
from api.actions import router as actions_router
from api.forensic import router as forensic_router
from api.profiling import router as profiling_router
from core.security import security_logging_middleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Auto-create tables (safe — skips if already exists)
    from core.database import engine
    from models.database import Base
    try:
        print(f"[STARTUP] Initializing database engine...")
        # We wrap this to prevent blocking the entire event loop if DB is slow
        Base.metadata.create_all(bind=engine)
        print(f"[STARTUP] Database tables verified/created.")
    except Exception as e:
        print(f"[WARN] Database initialization skipped: {e}")
    
    yield
    # Shutdown: Clean up if needed
    print("[SHUTDOWN] Sentinel API shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Standard Security Middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    # Pass through to our logging utility
    return await security_logging_middleware(request, call_next)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(detection_router, prefix="/api/v1/detection", tags=["detection"])
app.include_router(honeypot_router, prefix="/api/v1/honeypot", tags=["honeypot"])
app.include_router(inoculation_router, prefix="/api/v1/inoculation", tags=["inoculation"])
app.include_router(voice_router, prefix="/api/v1", tags=["voice"])
app.include_router(system_router, prefix="/api/v1/system", tags=["system"])
app.include_router(actions_router, prefix="/api/v1/actions", tags=["actions"])
app.include_router(forensic_router, prefix="/api/v1/forensic", tags=["forensic"])
app.include_router(profiling_router, prefix="/api/v1/profiling", tags=["profiling"])

@app.get("/")
async def root():
    return {"message": "Sentinel 1930 (BASIG) API is online. Protection active."}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "engine": "SENTINEL-v1.0"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Production Server on port {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port)
