# main.py
from fastapi import FastAPI, HTTPException
from database.db_setup import  init_db, close_db_connections
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# from slowapi.middleware import SlowAPIMiddleware
from accessnode.api.routers import user, provisioning
from accessnode.auth import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db_connections()

app = FastAPI(lifespan=lifespan)


# For development, allow all origins. In production, specify exact origins.
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    # Temporarily allow all for debugging - REMOVE IN PRODUCTION
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add basic security headers middleware for development
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)

    # Basic security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    return response

# limiter = Limiter(key_func=get_remote_address)
# app.state.limiter = limiter
# app.add_exception_handler(HTTPException, _rate_limit_exceeded_handler)


app.include_router(auth_router)  # New secure authentication
app.include_router(user.router)
app.include_router(provisioning.router, prefix="/provision", tags=["Database Provisioning"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": "2025-09-17"
    }

# Test endpoint for CORS debugging
@app.get("/test-cors")
async def test_cors():
    return {"message": "CORS is working!", "timestamp": "2025-09-17"}

@app.options("/user/database/{db_id}/query")
async def query_options(db_id: int):
    return {"message": "OPTIONS request successful"}
