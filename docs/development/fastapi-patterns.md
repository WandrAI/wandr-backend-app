# FastAPI Development Patterns

## Overview
Development patterns and best practices for the Wandr backend API using FastAPI, SQLAlchemy, and async Python.

## Project Structure

```
app/
├── main.py                 # FastAPI application entry point
├── core/                   # Core configuration and utilities
│   ├── config.py          # Environment-based settings
│   ├── database.py        # Database connection and session management
│   ├── security.py        # JWT authentication and authorization
│   └── exceptions.py      # Custom exception handlers
├── api/v1/                # REST API endpoints
│   ├── __init__.py
│   ├── auth.py           # Authentication endpoints
│   ├── users.py          # User management endpoints
│   ├── trips.py          # Trip CRUD endpoints
│   ├── locations.py      # Location-based endpoints
│   └── ai.py             # AI chat endpoints
├── graphql/              # GraphQL implementation
│   ├── schema.py         # Main GraphQL schema
│   ├── types/            # GraphQL type definitions
│   └── resolvers/        # GraphQL resolvers
├── models/               # SQLAlchemy database models
│   ├── __init__.py
│   ├── base.py           # Base model with common fields
│   ├── user.py           # User and profile models
│   ├── trip.py           # Trip and collaboration models
│   └── location.py       # Location and geographic models
├── schemas/              # Pydantic request/response models
│   ├── __init__.py
│   ├── user.py           # User schemas
│   ├── trip.py           # Trip schemas
│   └── common.py         # Shared schemas
├── services/             # Business logic and external integrations
│   ├── __init__.py
│   ├── auth_service.py   # Authentication business logic
│   ├── ai_service.py     # AI provider integrations
│   ├── location_service.py # Location and mapping services
│   └── trip_service.py   # Trip management logic
├── workers/              # Celery background tasks
│   ├── __init__.py
│   ├── ai_tasks.py       # AI processing tasks
│   └── notification_tasks.py # Notification tasks
└── websocket/            # WebSocket handlers
    ├── __init__.py
    ├── connection_manager.py # WebSocket connection management
    └── handlers.py       # WebSocket message handlers
```

## FastAPI Application Setup

### Main Application (`app/main.py`)

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.api.v1 import auth, users, trips, locations, ai
from app.graphql.schema import graphql_app

# Create FastAPI application
app = FastAPI(
    title="Wandr Backend API",
    description="Travel app backend with AI recommendations and real-time collaboration",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
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

# Include REST API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(trips.router, prefix="/api/v1/trips", tags=["Trips"])
app.include_router(locations.router, prefix="/api/v1/locations", tags=["Locations"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI Assistant"])

# Include GraphQL endpoint
app.mount("/graphql", graphql_app)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "wandr-backend-api"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
```

## Database Patterns

### Base Model (`app/models/base.py`)

```python
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Database Session Management (`app/core/database.py`)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=30,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency for getting database session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### Model Example (`app/models/trip.py`)

```python
from sqlalchemy import Column, String, Date, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Trip(BaseModel):
    __tablename__ = "trips"
    
    title = Column(String, nullable=False)
    description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String, default="planning")
    trip_data = Column(JSONB)  # Flexible trip details
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    creator = relationship("User", back_populates="created_trips")
    members = relationship("TripMember", back_populates="trip")
    activities = relationship("TripActivity", back_populates="trip")

class TripMember(BaseModel):
    __tablename__ = "trip_members"
    
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    role = Column(String, nullable=False)  # organizer, participant, viewer
    permissions = Column(JSONB)
    
    # Relationships
    trip = relationship("Trip", back_populates="members")
    user = relationship("User", back_populates="trip_memberships")
```

## API Endpoint Patterns

### REST API Router (`app/api/v1/trips.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.trip import TripCreate, TripUpdate, TripResponse
from app.services.trip_service import TripService

router = APIRouter()

@router.post("/", response_model=TripResponse)
async def create_trip(
    trip_data: TripCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TripResponse:
    """Create a new trip."""
    trip_service = TripService(db)
    trip = await trip_service.create_trip(trip_data, current_user.id)
    return TripResponse.from_orm(trip)

@router.get("/", response_model=List[TripResponse])
async def get_user_trips(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> List[TripResponse]:
    """Get trips for the current user."""
    trip_service = TripService(db)
    trips = await trip_service.get_user_trips(current_user.id, skip, limit)
    return [TripResponse.from_orm(trip) for trip in trips]

@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TripResponse:
    """Get a specific trip."""
    trip_service = TripService(db)
    trip = await trip_service.get_trip_by_id(trip_id, current_user.id)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
    return TripResponse.from_orm(trip)

@router.put("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: uuid.UUID,
    trip_update: TripUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TripResponse:
    """Update a trip."""
    trip_service = TripService(db)
    trip = await trip_service.update_trip(trip_id, trip_update, current_user.id)
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found or no permission"
        )
    return TripResponse.from_orm(trip)
```

## Service Layer Patterns

### Service Class (`app/services/trip_service.py`)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
import uuid

from app.models.trip import Trip, TripMember
from app.schemas.trip import TripCreate, TripUpdate

class TripService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_trip(self, trip_data: TripCreate, user_id: uuid.UUID) -> Trip:
        """Create a new trip with the user as organizer."""
        trip = Trip(
            title=trip_data.title,
            description=trip_data.description,
            start_date=trip_data.start_date,
            end_date=trip_data.end_date,
            created_by=user_id,
            trip_data=trip_data.trip_data or {},
        )
        self.db.add(trip)
        await self.db.flush()  # Get trip.id
        
        # Add creator as organizer
        trip_member = TripMember(
            trip_id=trip.id,
            user_id=user_id,
            role="organizer",
            permissions={"edit": True, "delete": True, "invite": True},
        )
        self.db.add(trip_member)
        
        await self.db.commit()
        await self.db.refresh(trip)
        return trip
    
    async def get_user_trips(
        self, 
        user_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Trip]:
        """Get trips where user is a member."""
        query = (
            select(Trip)
            .join(TripMember)
            .where(TripMember.user_id == user_id)
            .order_by(Trip.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_trip_by_id(
        self, 
        trip_id: uuid.UUID, 
        user_id: uuid.UUID
    ) -> Optional[Trip]:
        """Get trip by ID if user has access."""
        query = (
            select(Trip)
            .join(TripMember)
            .where(
                and_(
                    Trip.id == trip_id,
                    TripMember.user_id == user_id,
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
```

## Pydantic Schema Patterns

### Schema Models (`app/schemas/trip.py`)

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import date
import uuid

class TripBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        if v and values.get('start_date') and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v

class TripCreate(TripBase):
    trip_data: Optional[Dict[str, Any]] = Field(default_factory=dict)

class TripUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = Field(None, regex="^(planning|active|completed|cancelled)$")
    trip_data: Optional[Dict[str, Any]] = None

class TripResponse(TripBase):
    id: uuid.UUID
    status: str
    created_by: uuid.UUID
    trip_data: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
```

## Authentication Patterns

### JWT Security (`app/core/security.py`)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    query = select(User).where(User.id == uuid.UUID(user_id))
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise credentials_exception
    
    return user
```

## Error Handling Patterns

### Custom Exception Handlers (`app/core/exceptions.py`)

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

async def database_exception_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors."""
    logger.error(f"Database integrity error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": "Database constraint violation", "type": "integrity_error"}
    )

async def validation_exception_handler(request: Request, exc: ValueError):
    """Handle validation errors."""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc), "type": "validation_error"}
    )

def setup_exception_handlers(app: FastAPI):
    """Setup custom exception handlers."""
    app.add_exception_handler(IntegrityError, database_exception_handler)
    app.add_exception_handler(ValueError, validation_exception_handler)
```

## Testing Patterns

### Test Configuration (`tests/conftest.py`)

```python
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db
from app.models.base import Base

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_wandr"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def test_db(test_engine):
    """Create test database session."""
    TestSessionLocal = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture
async def client(test_db):
    """Create test client."""
    app.dependency_overrides[get_db] = lambda: test_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()
```

## Best Practices Summary

1. **Always use async/await** for database operations and external API calls
2. **Dependency injection** for database sessions, authentication, and services
3. **Service layer pattern** for business logic separation
4. **Comprehensive error handling** with meaningful HTTP responses
5. **Type hints everywhere** for better IDE support and validation
6. **Pydantic models** for all request/response validation
7. **Proper logging** throughout the application
8. **Environment-based configuration** for different deployment stages
9. **Database connection pooling** for production performance
10. **Comprehensive testing** with async test patterns 