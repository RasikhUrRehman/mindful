from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.routes import (
    auth_routes,
    habit_routes,
    mood_routes,
    goal_routes,
    reminder_routes,
    note_routes,
    user_routes,
    analytics_routes,
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Mindful Progress App",
    docs_url="/docs",
    openapi_url="/openapi.json",
)


def custom_openapi():
    """Create a custom OpenAPI schema that includes a global Bearer auth scheme.

    This will add an "Authorize" control in Swagger UI and mark endpoints as
    secured by default. Public endpoints (auth, root, health, openapi) are
    excluded so signup/login remain usable without a token.
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add Bearer security scheme
    openapi_schema.setdefault("components", {})
    openapi_schema["components"].setdefault("securitySchemes", {})
    openapi_schema["components"]["securitySchemes"]["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }

    # Apply security globally
    openapi_schema.setdefault("security", [{"BearerAuth": []}])

    # Exclude some public paths from requiring auth (e.g., /auth/*, /, /health, /openapi.json)
    public_prefixes = ("/auth", "/openapi.json", "/docs", "/", "/health")
    for path, path_item in openapi_schema.get("paths", {}).items():
        if any(path.startswith(p) for p in public_prefixes):
            # remove security requirement for all methods on this path
            for method in path_item.keys():
                if isinstance(path_item[method], dict) and "security" in path_item[method]:
                    path_item[method].pop("security", None)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Attach custom openapi generator
app.openapi = custom_openapi

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth_routes.router)
app.include_router(habit_routes.router)
app.include_router(mood_routes.router)
app.include_router(goal_routes.router)
app.include_router(reminder_routes.router)
app.include_router(note_routes.router)
app.include_router(user_routes.router)
app.include_router(analytics_routes.router)


@app.get("/", tags=["root"])
def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Mindful Progress API",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
