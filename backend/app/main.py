from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.routes.auth import router as auth_router
from app.api.routes.project import router as project_router
from app.api.routes.targets import router as targets_router
from app.api.routes.scans import router as scans_router
from app.api.routes.recon import router as recon_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.admin import router as admin_router
from app.core.middleware import SecurityHeadersMiddleware

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="ReconXplorer API")

# CORS configuration - MUST be defined and added FIRST
# Use allow_origin_regex for maximum flexibility in dev environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Register Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# Register Rate Limiter Exception Handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Global Exception Handler to prevent leakage
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the error internally here
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"},
    )

@app.get("/")
def root():
    return {
        "message": "ReconXplorer API is operational",
        "version": "1.0.0",
        "health_check": "/health"
    }

@app.get("/health")
@limiter.limit("5/minute")
def health_check(request: Request):
    return {"status": "healthy"}

app.include_router(auth_router)
app.include_router(project_router, prefix="/projects", tags=["Projects"])
app.include_router(targets_router)
app.include_router(scans_router)
app.include_router(recon_router)
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(admin_router)