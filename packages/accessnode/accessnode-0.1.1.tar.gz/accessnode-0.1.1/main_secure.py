# main_secure.py - Production-ready FastAPI application
import os
from fastapi import FastAPI, HTTPException
from database.db_setup import init_db, close_db_connections
from contextlib import asynccontextmanager

# Import routers
from accessnode.api.routers import user, provisioning
from accessnode.auth import auth_router
from accessnode.auth.production import ProductionSecurityConfig


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting AccessNode...")

    # Validate production configuration if in production
    environment = os.getenv("ENVIRONMENT", "development")
    if environment == "production":
        print("📋 Validating production configuration...")
        validation = ProductionSecurityConfig.validate_environment()
        if not validation["is_production_ready"]:
            print("❌ Production validation failed:")
            for issue in validation["issues"]:
                print(f"  - {issue}")
            raise RuntimeError("Production configuration validation failed")
        print("✅ Production configuration validated")

    # Initialize database
    await init_db()
    print("✅ Database initialized")

    yield

    # Shutdown
    print("🛑 Shutting down AccessNode...")
    await close_db_connections()
    print("✅ Database connections closed")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    # Create FastAPI app with enhanced security configuration
    app = FastAPI(
        title="AccessNode",
        description="Secure and flexible database management system",
        version="2.0.0",
        lifespan=lifespan,
        docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
        redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None
    )

    # Configure security middleware based on environment
    environment = os.getenv("ENVIRONMENT", "development")

    if environment == "production":
        # Use production security configuration
        ProductionSecurityConfig.configure_security_middleware(app)
    else:
        # Development CORS configuration
        from fastapi.middleware.cors import CORSMiddleware

        origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8080",
            "http://127.0.0.1:8080"
        ]

        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            allow_headers=["*"],
            expose_headers=["*"],
        )

    return app


# Create the FastAPI application
app = create_app()

# Include routers
app.include_router(auth_router)  # New secure authentication
app.include_router(user.router)  # Existing user routes (will be updated)
app.include_router(provisioning.router, prefix="/provision", tags=["Database Provisioning"])


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": "2025-09-17"
    }


# Development endpoints (disabled in production)
if os.getenv("ENVIRONMENT") != "production":
    @app.get("/test-cors")
    async def test_cors():
        return {"message": "CORS is working!", "timestamp": "2025-09-17"}

    @app.options("/user/database/{db_id}/query")
    async def query_options(db_id: int):
        return {"message": "OPTIONS request successful"}


# Global exception handler for security
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler to prevent information leakage"""
    # In production, don't expose internal error details
    if os.getenv("ENVIRONMENT") == "production":
        return {"detail": "Internal server error"}
    else:
        # In development, show detailed errors
        raise exc


if __name__ == "__main__":
    import uvicorn

    # Configuration based on environment
    environment = os.getenv("ENVIRONMENT", "development")

    if environment == "production":
        # Production configuration
        uvicorn.run(
            "main_secure:app",
            host="0.0.0.0",
            port=8000,
            ssl_keyfile=os.getenv("SSL_KEYFILE"),
            ssl_certfile=os.getenv("SSL_CERTFILE"),
            access_log=False,  # Use structured logging instead
            server_header=False,
            date_header=False
        )
    else:
        # Development configuration
        uvicorn.run(
            "main_secure:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            access_log=True
        )