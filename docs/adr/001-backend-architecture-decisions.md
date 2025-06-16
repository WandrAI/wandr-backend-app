# ADR-001: Backend Architecture Decisions

## Status
**ACCEPTED** - Core backend architecture for Wandr travel API

## Context

Building a scalable backend API for a travel application with the following requirements:
- **Real-time collaboration** for group travel planning
- **AI-powered recommendations** with conversational interfaces
- **Location-based services** with geographic queries
- **High-performance APIs** for client application consumption
- **Secure authentication** and authorization
- **Background task processing** for AI and data operations

## Decision 1: API Architecture Pattern

### Alternatives Considered

**Option 1: Pure REST API**
- Pros: Simple, cacheable, well-understood HTTP semantics
- Cons: Over-fetching for complex travel data, multiple round trips
- Travel Context: Would require many API calls for trip planning workflows

**Option 2: Pure GraphQL API** 
- Pros: Flexible queries, single endpoint, real-time subscriptions
- Cons: Caching complexity, learning curve, harder client-side caching
- Travel Context: Great for complex travel queries but harder client optimization

**Option 3: Hybrid REST + GraphQL** ✅ **CHOSEN**
- Pros: REST for simple CRUD, GraphQL for complex travel queries
- Cons: Two API paradigms to maintain
- Travel Context: REST for trips/users, GraphQL for complex travel searches

**Decision Rationale**: Travel apps have both simple CRUD operations (user profiles, basic trip data) and complex queries (nested trip data with locations, activities, group members). Hybrid approach optimizes for both use cases.

## Decision 2: Database Architecture

### Alternatives Considered

**Option 1: PostgreSQL Only**
- Pros: ACID compliance, complex queries, JSON support, PostGIS
- Cons: All data in single store, potential performance bottlenecks
- Travel Context: Good for travel data relationships but lacks caching

**Option 2: MongoDB with Redis**
- Pros: Flexible schema for travel data, built-in sharding
- Cons: No ACID transactions, complex geographic queries
- Travel Context: Good for varied travel data but weak location queries

**Option 3: PostgreSQL + Redis** ✅ **CHOSEN**
- Pros: ACID + caching, PostGIS for location queries, Redis pub/sub
- Cons: Two databases to manage
- Travel Context: Perfect for travel data relationships + fast location caching

**Decision Rationale**: Travel apps need ACID compliance for bookings, complex geographic queries for location services, and fast caching for recommendations. PostgreSQL with PostGIS handles travel data complexity while Redis provides performance.

## Decision 3: Authentication Strategy

### Alternatives Considered

**Option 1: Session-based Authentication**
- Pros: Server-side revocation, familiar pattern
- Cons: Stateful, doesn't scale horizontally, poor client experience
- Travel Context: Bad for client apps with intermittent connectivity

**Option 2: OAuth2 with External Provider Only**
- Pros: No password management, leverages existing accounts
- Cons: Vendor lock-in, requires internet for auth, limited customization
- Travel Context: Problematic for travel apps in areas with poor connectivity

**Option 3: JWT with FastAPI Security** ✅ **CHOSEN**
- Pros: Stateless, client-friendly, offline capable, FastAPI integration
- Cons: Token revocation complexity, larger payloads
- Travel Context: Excellent for travel client apps with offline requirements

**Decision Rationale**: Travel applications are used in locations with poor connectivity. JWT tokens allow offline operation and stateless scaling while FastAPI Security provides excellent developer experience.

## Decision 4: Real-time Architecture

### Alternatives Considered

**Option 1: Server-Sent Events (SSE)**
- Pros: Simple HTTP, automatic reconnection, works through proxies
- Cons: Unidirectional only, limited browser connections
- Travel Context: Insufficient for collaborative trip planning

**Option 2: Third-party Service (Pusher/Socket.io)**
- Pros: Managed infrastructure, rich features, easy scaling
- Cons: Vendor dependency, additional costs, data privacy concerns
- Travel Context: Travel data privacy concerns with external services

**Option 3: Native WebSockets with Redis Pub/Sub** ✅ **CHOSEN**
- Pros: Bidirectional, full control, Redis integration, scalable
- Cons: More complex implementation, connection management
- Travel Context: Perfect for real-time group travel collaboration

**Decision Rationale**: Group travel planning requires bidirectional real-time communication. Native WebSockets with Redis pub/sub provides full control over travel data while enabling horizontal scaling.

## Decision 5: Background Task Processing

### Alternatives Considered

**Option 1: FastAPI Background Tasks**
- Pros: Simple, no additional infrastructure, built-in
- Cons: Limited to single process, no persistence, no monitoring
- Travel Context: Insufficient for AI processing and travel data sync

**Option 2: Apache Kafka + Custom Workers**
- Pros: High throughput, durable, streaming capabilities
- Cons: Complex setup, overkill for current needs, steep learning curve
- Travel Context: Over-engineered for travel app background tasks

**Option 3: Celery with Redis** ✅ **CHOSEN**
- Pros: Python-native, Redis integration, rich monitoring, proven
- Cons: Additional complexity, requires Redis
- Travel Context: Perfect for AI processing, travel data sync, notifications

**Decision Rationale**: Travel apps need reliable background processing for AI recommendations, data synchronization, and notifications. Celery provides mature Python tooling with Redis integration.

## Decision 6: AI Integration Strategy

### Alternatives Considered

**Option 1: Local LLM Deployment**
- Pros: Full control, no external dependencies, data privacy
- Cons: High infrastructure costs, maintenance overhead, slower updates
- Travel Context: Too expensive and complex for travel recommendations

**Option 2: AI Gateway Service (LangChain Cloud)**
- Pros: Vendor abstraction, built-in chains, managed infrastructure
- Cons: Additional layer, costs, limited customization
- Travel Context: Reduces flexibility for travel-specific AI customization

**Option 3: Direct API with Abstraction Layer** ✅ **CHOSEN**
- Pros: Simple, cost-effective, full control, easy provider switching
- Cons: Vendor lock-in risk, API rate limits
- Travel Context: Direct control over travel-specific prompts and models

**Decision Rationale**: Travel applications need real-time AI responses with travel-specific context. Direct APIs provide the best performance and customization while abstraction layer enables provider switching.

## Implementation Architecture

```python
# Core Application Structure
app/
├── api/v1/          # REST API endpoints
├── graphql/         # GraphQL schema and resolvers  
├── models/          # SQLAlchemy database models
├── schemas/         # Pydantic request/response models
├── services/        # Business logic and external integrations
├── core/           # Configuration, security, database
├── workers/        # Celery background tasks
└── websocket/      # WebSocket handlers

# Key Technologies
- FastAPI: Async web framework with automatic docs
- SQLAlchemy: Database ORM with async support
- Alembic: Database migrations
- Pydantic: Data validation and serialization
- Redis: Caching, sessions, pub/sub, task queue
- Celery: Background task processing
- Strawberry: GraphQL library for Python
```

## Consequences

### Positive
- **High Performance**: Async/await throughout, Redis caching, optimized queries
- **Scalability**: Stateless JWT, Redis pub/sub, horizontal scaling ready
- **Developer Experience**: FastAPI auto-docs, type safety, comprehensive tooling
- **Flexibility**: Hybrid API approach supports various client needs
- **Reliability**: PostgreSQL ACID compliance, Celery task reliability

### Negative
- **Complexity**: Multiple technologies require operational expertise
- **Infrastructure**: PostgreSQL + Redis requires more setup than single database
- **Learning Curve**: GraphQL adds complexity for some developers

### Risks & Mitigations
- **Database Performance**: Mitigated by Redis caching and proper indexing
- **WebSocket Scaling**: Mitigated by Redis pub/sub architecture
- **AI Provider Changes**: Mitigated by service abstraction layer

## Related ADRs
- [ADR-002: Database Schema Design](002-database-schema-design.md)
- [ADR-003: API Security Implementation](003-api-security.md)
- [ADR-004: Background Task Patterns](004-background-task-patterns.md)

---
**Date**: June 2025  
**Status**: Accepted  
**Decision Makers**: Backend Team 