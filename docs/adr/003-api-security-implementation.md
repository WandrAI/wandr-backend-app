# ADR-003: API Security Implementation

## Status

**ACCEPTED** - Security architecture for travel API

## Context

Implementing comprehensive security for a travel application API with requirements:

- **User authentication** for personal travel data access
- **Authorization controls** for group trip collaboration
- **Rate limiting** to prevent abuse and ensure fair usage
- **Data protection** for sensitive travel information (locations, preferences)
- **API security** against common attacks (CSRF, XSS, injection)
- **Audit logging** for security monitoring and compliance

## Decision 1: Authentication Mechanism

### Alternatives Considered

**Option 1: Session-based Authentication with Cookies**

- Pros: Familiar pattern, automatic CSRF protection, server-side control
- Cons: Stateful, scaling issues, poor mobile app experience
- Travel Context: Bad for mobile apps used in various locations/networks

**Option 2: API Keys for Service Authentication**

- Pros: Simple for service-to-service, no expiration complexity
- Cons: No user context, hard to revoke, not suitable for user auth
- Travel Context: Insufficient for personal travel data and collaboration

**Option 3: JWT with Refresh Token Pattern** ✅ **CHOSEN**

- Pros: Stateless, mobile-friendly, offline capable, scalable
- Cons: Token revocation complexity, payload size considerations
- Travel Context: Perfect for mobile travel apps with intermittent connectivity

**Decision Rationale**: Travel apps are primarily mobile and used in areas with poor connectivity. JWT tokens enable offline operation while providing secure authentication.

## Decision 2: Authorization Strategy

### Alternatives Considered

**Option 1: Role-Based Access Control (RBAC)**

- Pros: Standard pattern, well-understood, many libraries
- Cons: Rigid for travel scenarios, doesn't handle trip-specific permissions
- Travel Context: Doesn't match travel group dynamics (trip organizers, etc.)

**Option 2: Attribute-Based Access Control (ABAC)**

- Pros: Very flexible, context-aware, fine-grained control
- Cons: Complex implementation, hard to debug, performance overhead
- Travel Context: Over-engineered for typical travel app scenarios

**Option 3: Resource-Based Permissions with Scopes** ✅ **CHOSEN**

- Pros: Trip-scoped permissions, travel-specific roles, simple but flexible
- Cons: Custom implementation required
- Travel Context: Perfect for travel domain (trip organizers, participants, viewers)

**Decision Rationale**: Travel applications have specific permission patterns around trips and groups that standard RBAC doesn't handle well. Resource-based permissions match the travel domain.

## Decision 3: Rate Limiting Strategy

### Alternatives Considered

**Option 1: Simple Fixed Window Rate Limiting**

- Pros: Easy to implement, predictable behavior
- Cons: Burst traffic issues, unfair distribution
- Travel Context: Poor for travel peak usage patterns

**Option 2: Token Bucket Algorithm**

- Pros: Handles bursts well, smooth rate limiting
- Cons: More complex implementation, memory overhead
- Travel Context: Good for variable travel app usage

**Option 3: Sliding Window with Redis** ✅ **CHOSEN**

- Pros: Fair distribution, handles travel peaks, Redis integration
- Cons: More complex, requires Redis
- Travel Context: Excellent for travel apps with peak usage during travel seasons

**Decision Rationale**: Travel applications have highly variable usage patterns (peak during travel seasons, bursts during trip planning). Sliding window provides fair rate limiting.

## Decision 4: Data Protection Strategy

### Alternatives Considered

**Option 1: Application-Level Encryption**

- Pros: Full control, encrypted at rest and in transit
- Cons: Complex key management, performance impact
- Travel Context: May be overkill for most travel data

**Option 2: Database-Level Encryption Only**

- Pros: Transparent to application, good performance
- Cons: Limited control, doesn't protect sensitive fields specifically
- Travel Context: Insufficient for location privacy requirements

**Option 3: Hybrid Field-Level + Transport Encryption** ✅ **CHOSEN**

- Pros: Protects sensitive fields, good performance, flexible
- Cons: Selective encryption complexity
- Travel Context: Perfect for protecting location data while maintaining performance

**Decision Rationale**: Travel apps handle varying sensitivity levels of data. Location data needs protection while general preferences don't. Hybrid approach optimizes security vs. performance.

## Implementation Details

### JWT Configuration

```python
# app/core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets

class SecurityConfig:
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Password hashing
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token with user claims."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "type": "access"})

    return jwt.encode(to_encode, SecurityConfig.SECRET_KEY, algorithm=SecurityConfig.ALGORITHM)

def create_refresh_token(data: dict):
    """Create refresh token for extended sessions."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire, "type": "refresh"})

    return jwt.encode(to_encode, SecurityConfig.SECRET_KEY, algorithm=SecurityConfig.ALGORITHM)
```

### Resource-Based Authorization

```python
# app/core/permissions.py
from enum import Enum
from typing import List, Optional
import uuid

class TripRole(str, Enum):
    ORGANIZER = "organizer"
    PARTICIPANT = "participant"
    VIEWER = "viewer"

class Permission(str, Enum):
    VIEW_TRIP = "view_trip"
    EDIT_TRIP = "edit_trip"
    DELETE_TRIP = "delete_trip"
    INVITE_MEMBERS = "invite_members"
    MANAGE_MEMBERS = "manage_members"
    VIEW_EXPENSES = "view_expenses"
    EDIT_EXPENSES = "edit_expenses"

ROLE_PERMISSIONS = {
    TripRole.ORGANIZER: [
        Permission.VIEW_TRIP,
        Permission.EDIT_TRIP,
        Permission.DELETE_TRIP,
        Permission.INVITE_MEMBERS,
        Permission.MANAGE_MEMBERS,
        Permission.VIEW_EXPENSES,
        Permission.EDIT_EXPENSES,
    ],
    TripRole.PARTICIPANT: [
        Permission.VIEW_TRIP,
        Permission.EDIT_TRIP,  # Can edit trip details
        Permission.VIEW_EXPENSES,
        Permission.EDIT_EXPENSES,  # Can add expenses
    ],
    TripRole.VIEWER: [
        Permission.VIEW_TRIP,
        Permission.VIEW_EXPENSES,
    ],
}

async def check_trip_permission(
    user_id: uuid.UUID,
    trip_id: uuid.UUID,
    required_permission: Permission,
    db: AsyncSession,
) -> bool:
    """Check if user has permission for trip action."""
    # Get user's role in trip
    query = select(TripMember.role).where(
        and_(
            TripMember.user_id == user_id,
            TripMember.trip_id == trip_id,
        )
    )
    result = await db.execute(query)
    role = result.scalar_one_or_none()

    if not role:
        return False

    return required_permission in ROLE_PERMISSIONS.get(TripRole(role), [])
```

### Rate Limiting Implementation

```python
# app/core/rate_limiting.py
import redis
import time
from fastapi import HTTPException, Request
from typing import Optional

class RateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int,
        identifier: str = "api"
    ) -> bool:
        """Sliding window rate limiter using Redis."""
        now = time.time()
        pipeline = self.redis.pipeline()

        # Remove old entries
        pipeline.zremrangebyscore(key, 0, now - window_seconds)

        # Count current requests
        pipeline.zcard(key)

        # Add current request
        pipeline.zadd(key, {f"{now}-{identifier}": now})

        # Set expiry
        pipeline.expire(key, window_seconds + 1)

        results = pipeline.execute()
        current_requests = results[1]

        return current_requests < limit

# Rate limiting dependency
async def rate_limit_dependency(request: Request):
    """FastAPI dependency for rate limiting."""
    client_ip = request.client.host
    user_id = getattr(request.state, "user_id", None)

    # Use user ID if authenticated, otherwise IP
    identifier = str(user_id) if user_id else client_ip
    key = f"rate_limit:{identifier}"

    rate_limiter = RateLimiter(redis_client)

    if not await rate_limiter.check_rate_limit(key, limit=100, window_seconds=3600):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": "3600"}
        )
```

### Security Middleware

```python
# app/core/middleware.py
from fastapi import Request, HTTPException
from fastapi.security.utils import get_authorization_scheme_param
import logging

logger = logging.getLogger(__name__)

async def security_middleware(request: Request, call_next):
    """Security middleware for logging and basic protection."""
    start_time = time.time()

    # Log request for security monitoring
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host}"
    )

    # Basic security headers
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # Log response time for monitoring
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    return response
```

## Security Configuration

### Environment Variables

```bash
# Security Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# Rate Limiting
REDIS_URL=redis://localhost:6379/0
RATE_LIMIT_REQUESTS_PER_HOUR=1000

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
ALLOWED_HOSTS=["localhost", "yourdomain.com"]

# Database Security
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/wandr
DATABASE_SSL_MODE=require  # For production
```

### FastAPI Security Setup

```python
# app/main.py security configuration
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# Rate limiting middleware
@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    await rate_limit_dependency(request)
    response = await call_next(request)
    return response
```

## Consequences

### Positive

- **Comprehensive Security**: Multi-layered security approach for travel data
- **Mobile Optimized**: JWT tokens work well with mobile app patterns
- **Travel Domain Fit**: Resource-based permissions match travel use cases
- **Scalable**: Redis-based rate limiting scales horizontally
- **Auditable**: Comprehensive logging for security monitoring

### Negative

- **Complexity**: Multiple security layers require careful coordination
- **Token Management**: JWT refresh token rotation adds complexity
- **Redis Dependency**: Rate limiting requires Redis infrastructure

### Risks & Mitigations

- **Token Compromise**: Mitigated by short access token expiry and refresh rotation
- **Rate Limiting Bypass**: Mitigated by multiple rate limiting strategies
- **Permission Escalation**: Mitigated by explicit permission checks and audit logging

## Related ADRs

- [ADR-001: Backend Architecture Decisions](001-backend-architecture-decisions.md)
- [ADR-002: Database Schema Design](002-database-schema-design.md)

---

**Date**: June 2025
**Status**: Accepted
**Decision Makers**: Backend Team
