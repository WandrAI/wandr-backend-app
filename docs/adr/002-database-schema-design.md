# ADR-002: Database Schema Design

## Status
**ACCEPTED** - Travel domain database architecture

## Context

Designing database schema for a travel application requiring:
- **User management** with profiles and preferences
- **Trip planning** with collaborative features and complex relationships
- **Location data** with geographic queries and recommendations
- **AI conversations** with context and history tracking
- **Real-time collaboration** with group permissions and activity tracking

## Decision 1: User and Authentication Schema

### Alternatives Considered

**Option 1: Single User Table**
- Pros: Simple, fast queries, easy to understand
- Cons: Large table, poor normalization, inflexible for travel profiles
- Travel Context: Insufficient for complex travel preferences and group roles

**Option 2: EAV (Entity-Attribute-Value) for Flexibility**
- Pros: Maximum flexibility, easy to extend
- Cons: Poor query performance, complex joins, type safety issues
- Travel Context: Too flexible, loses travel domain structure

**Option 3: Normalized User + Profile + Preferences** ✅ **CHOSEN**
- Pros: Proper normalization, travel-specific structure, good performance
- Cons: More complex schema, multiple joins
- Travel Context: Perfect for travel domain with clear user/travel separation

**Decision Rationale**: Travel applications have distinct user identity vs. travel preferences. Normalized approach provides clear separation while maintaining performance.

## Decision 2: Trip and Location Schema

### Alternatives Considered

**Option 1: Embedded JSON for Trip Data**
- Pros: Flexible schema, fewer joins, denormalized performance
- Cons: Poor queryability, JSON maintenance, relationship complexity
- Travel Context: Hard to query by location or shared trip data

**Option 2: Fully Normalized with Separate Tables**
- Pros: Perfect normalization, clear relationships, excellent queries
- Cons: Many tables, complex joins, potential performance impact
- Travel Context: Great for travel queries but potentially slow

**Option 3: Hybrid Normalized + JSON for Flexible Data** ✅ **CHOSEN**
- Pros: Core relationships normalized, flexible data in JSON, PostGIS support
- Cons: Two patterns to maintain
- Travel Context: Core travel data normalized, preferences/details in JSON

**Decision Rationale**: Travel data has both structured relationships (users, trips, locations) and flexible data (preferences, custom fields). Hybrid approach optimizes for both.

## Decision 3: Group Collaboration Schema

### Alternatives Considered

**Option 1: Simple Trip Sharing with Basic Permissions**
- Pros: Simple implementation, easy to understand
- Cons: Limited collaboration features, poor role management
- Travel Context: Insufficient for complex group travel planning

**Option 2: Complex RBAC (Role-Based Access Control)**
- Pros: Maximum flexibility, enterprise-grade permissions
- Cons: Over-engineered, complex UI, slow performance
- Travel Context: Too complex for typical travel group scenarios

**Option 3: Trip-Scoped Roles with Activity Tracking** ✅ **CHOSEN**
- Pros: Travel-specific roles, activity history, simple but flexible
- Cons: Custom role system to maintain
- Travel Context: Perfect for travel group dynamics (organizer, participant, viewer)

**Decision Rationale**: Travel groups have specific dynamics (trip organizers, participants, etc.) that standard RBAC doesn't capture well. Trip-scoped roles match travel domain needs.

## Final Schema Design

```sql
-- Core User Management
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE,
    password_hash VARCHAR,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    display_name VARCHAR,
    avatar_url VARCHAR,
    bio TEXT,
    travel_preferences JSONB, -- Flexible travel-specific data
    privacy_settings JSONB,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- Location and Geographic Data (PostGIS)
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL,
    location_type VARCHAR, -- city, country, poi, accommodation
    coordinates GEOGRAPHY(POINT) NOT NULL,
    address JSONB,
    place_data JSONB, -- External API data (Google Places, etc.)
    created_at TIMESTAMP DEFAULT now(),
    UNIQUE(name, coordinates)
);

-- Trip Management
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    status VARCHAR DEFAULT 'planning', -- planning, active, completed, cancelled
    trip_data JSONB, -- Flexible trip details, itinerary, budget
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

-- Group Collaboration
CREATE TABLE trip_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID REFERENCES trips(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR NOT NULL, -- organizer, participant, viewer
    permissions JSONB, -- Custom permissions per member
    joined_at TIMESTAMP DEFAULT now(),
    UNIQUE(trip_id, user_id)
);

CREATE TABLE trip_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID REFERENCES trips(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    activity_type VARCHAR NOT NULL, -- created, updated, joined, comment, etc.
    activity_data JSONB,
    created_at TIMESTAMP DEFAULT now()
);

-- AI and Recommendations
CREATE TABLE ai_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    trip_id UUID REFERENCES trips(id) ON DELETE SET NULL,
    conversation_data JSONB NOT NULL, -- Messages, context, preferences
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    trip_id UUID REFERENCES trips(id) ON DELETE CASCADE,
    location_id UUID REFERENCES locations(id),
    recommendation_type VARCHAR, -- restaurant, activity, accommodation
    recommendation_data JSONB,
    ai_generated BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT now()
);

-- Indexes for Performance
CREATE INDEX idx_locations_coordinates ON locations USING GIST (coordinates);
CREATE INDEX idx_trips_dates ON trips (start_date, end_date);
CREATE INDEX idx_trip_members_user ON trip_members (user_id);
CREATE INDEX idx_trip_activities_trip ON trip_activities (trip_id, created_at);
CREATE INDEX idx_ai_conversations_user ON ai_conversations (user_id, created_at);
CREATE INDEX idx_recommendations_user_trip ON recommendations (user_id, trip_id);

-- JSON Indexes for Flexible Data
CREATE INDEX idx_user_profiles_preferences ON user_profiles USING GIN (travel_preferences);
CREATE INDEX idx_trips_data ON trips USING GIN (trip_data);
CREATE INDEX idx_ai_conversations_data ON ai_conversations USING GIN (conversation_data);
```

## Consequences

### Positive
- **Travel Domain Fit**: Schema directly supports travel application workflows
- **Performance**: PostGIS for location queries, proper indexing, JSON for flexibility
- **Scalability**: UUID primary keys, proper normalization, efficient indexes
- **Flexibility**: JSON fields for evolving travel domain requirements
- **Collaboration**: Built-in support for group travel planning and permissions

### Negative
- **Complexity**: Hybrid normalized + JSON requires careful maintenance
- **PostGIS Dependency**: Requires PostGIS extension for geographic features
- **JSON Querying**: JSON fields require careful query optimization

### Risks & Mitigations
- **JSON Performance**: Mitigated by proper GIN indexes and query patterns
- **Schema Evolution**: Mitigated by Alembic migrations and JSON flexibility
- **Geographic Performance**: Mitigated by PostGIS spatial indexes

## Related ADRs
- [ADR-001: Backend Architecture Decisions](001-backend-architecture-decisions.md)
- [ADR-003: API Security Implementation](003-api-security.md)

---
**Date**: June 2025  
**Status**: Accepted  
**Decision Makers**: Backend Team 