from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.session import engine, Base
import app.db.models  # Ensures all ORM models are registered before metadata creation
from app.api.crm_routes import router as crm_router
from app.api.proxy_routes import router as proxy_router
from app.api.audit_routes import router as audit_router
from app.api.agent_routes import router as agent_router
from app.api.auth_routes import router as auth_router
from app.services.crm_service import CRMService
from app.services.auth_service import AuthService
from app.db.session import SessionLocal

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler to create database tables and seed demo data on startup."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        CRMService.seed_initial_data(db)
        AuthService.seed_initial_users(db)
    finally:
        db.close()
    yield

def create_application() -> FastAPI:
    """Factory function to initialize and configure the FastAPI application instance."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=(
            "AI Governance Tool Permission Proxy. Intercepts AI Agent tool calls, "
            "enforces fine-grained JSON permission manifests, records audit trails, "
            "and triggers security alerts."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Configure CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API Routers
    app.include_router(crm_router, prefix=settings.API_V1_STR)
    app.include_router(proxy_router, prefix=settings.API_V1_STR)
    app.include_router(audit_router, prefix=settings.API_V1_STR)
    app.include_router(agent_router, prefix=settings.API_V1_STR)
    app.include_router(auth_router, prefix=settings.API_V1_STR)

    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint returning basic service metadata."""
        return {
            "status": "online",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "docs": "/docs"
        }

    @app.get("/health", tags=["Health Check"])
    async def health_check():
        """Liveness/Readiness probe endpoint for container orchestrators (Kubernetes/AWS ECS)."""
        return {"status": "healthy"}

    return app

app = create_application()
