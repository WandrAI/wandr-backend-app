from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1 import auth, trips, users
from app.core.config import settings
from app.core.exceptions import setup_exception_handlers

# Create FastAPI application
app = FastAPI(
    title="Wandr Backend API",
    description=(
        "Travel app backend with AI recommendations and real-time collaboration"
    ),
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    redirect_slashes=False,  # Disable automatic slash redirects
)

# Security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# Exception handlers
setup_exception_handlers(app)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(trips.router, prefix="/api/v1/trips", tags=["Trips"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])


# Health check endpoint
@app.get("/")
def root():
    return {
        "message": "Wandr Backend API is running",
        "version": "1.0.0",
        "status": "healthy",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "wandr-backend-api", "version": "1.0.0"}
