# API Design Guide

## Overview

This document establishes API design principles and conventions for the Wandr backend application, ensuring consistency, maintainability, and excellent developer experience.

## RESTful API Principles

### Resource Naming

- Use **nouns** for resource endpoints, not verbs
- Use **plural** forms for collections: `/destinations`, `/trips`, `/users`
- Use **lowercase** with hyphens for multi-word resources: `/travel-plans`

```
✅ Good:
GET /api/v1/destinations
POST /api/v1/trips
GET /api/v1/user-preferences

❌ Avoid:
GET /api/v1/getDestinations
POST /api/v1/createTrip
GET /api/v1/userPreferences
```

### HTTP Methods

Follow standard HTTP semantics:

- **GET**: Retrieve data (read-only, safe)
- **POST**: Create new resources or complex operations
- **PUT**: Update entire resource (idempotent)
- **PATCH**: Partial resource updates
- **DELETE**: Remove resources (idempotent)

### Status Codes

Use appropriate HTTP status codes:

- **200 OK**: Successful GET, PUT, PATCH
- **201 Created**: Successful POST with resource creation
- **204 No Content**: Successful DELETE or PUT without response body
- **400 Bad Request**: Client error, validation failures
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation errors with details
- **500 Internal Server Error**: Server errors

## Travel API Conventions

### Destination Resources

```python
# Collection endpoints
GET /api/v1/destinations              # List destinations with pagination
POST /api/v1/destinations             # Create new destination (admin)

# Individual resource endpoints
GET /api/v1/destinations/{id}         # Get destination details
PUT /api/v1/destinations/{id}         # Update destination (admin)
DELETE /api/v1/destinations/{id}      # Delete destination (admin)

# Nested resources
GET /api/v1/destinations/{id}/reviews # Get reviews for destination
POST /api/v1/destinations/{id}/reviews # Add review to destination
```

### Trip Resources

```python
# User trip management
GET /api/v1/trips                     # User's trips
POST /api/v1/trips                    # Create new trip
GET /api/v1/trips/{id}               # Get trip details
PUT /api/v1/trips/{id}               # Update trip
DELETE /api/v1/trips/{id}            # Delete trip

# Trip activities
GET /api/v1/trips/{id}/activities    # Get trip activities
POST /api/v1/trips/{id}/activities   # Add activity to trip
```

## Request/Response Patterns

### Request Format

```json
{
  "data": {
    "type": "destination",
    "attributes": {
      "name": "Paris",
      "country": "France",
      "coordinates": {
        "latitude": 48.8566,
        "longitude": 2.3522
      }
    }
  }
}
```

### Response Format

```json
{
  "data": {
    "id": "123",
    "type": "destination",
    "attributes": {
      "name": "Paris",
      "country": "France",
      "rating": 4.8,
      "created_at": "2024-01-15T10:30:00Z"
    },
    "relationships": {
      "reviews": {
        "links": {
          "related": "/api/v1/destinations/123/reviews"
        }
      }
    }
  },
  "meta": {
    "version": "1.0",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Error Response Format

```json
{
  "errors": [
    {
      "code": "VALIDATION_ERROR",
      "title": "Validation Failed",
      "detail": "Destination name is required",
      "source": {
        "pointer": "/data/attributes/name"
      }
    }
  ],
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Pagination

### Cursor-Based Pagination (Recommended)

```
GET /api/v1/destinations?cursor=eyJpZCI6MTIzfQ&limit=20
```

Response includes pagination metadata:

```json
{
  "data": [...],
  "meta": {
    "pagination": {
      "has_next": true,
      "has_previous": false,
      "next_cursor": "eyJpZCI6MTQzfQ",
      "count": 20
    }
  }
}
```

### Offset Pagination (For simple cases)

```
GET /api/v1/destinations?offset=20&limit=20
```

## Filtering and Searching

### Query Parameters

```
GET /api/v1/destinations?country=france&rating_min=4.0&sort=-rating
GET /api/v1/destinations?search=paris&type=restaurant
```

### Advanced Filtering

```
GET /api/v1/destinations?filter[country]=france&filter[rating][gte]=4.0
```

## Versioning

### URL Versioning (Current)

```
/api/v1/destinations
/api/v2/destinations
```

### Header Versioning (Future consideration)

```
Accept: application/vnd.wandr.v1+json
```

## Authentication & Authorization

### JWT Bearer Tokens

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### API Keys (For third-party integration)

```
X-API-Key: wandr_live_sk_1234567890abcdef
```

## Rate Limiting

### Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

### Rate Limit Response

```json
{
  "errors": [
    {
      "code": "RATE_LIMIT_EXCEEDED",
      "title": "Rate Limit Exceeded",
      "detail": "Too many requests. Try again in 60 seconds."
    }
  ]
}
```

## Travel-Specific Considerations

### Location Data

- Use decimal degrees for coordinates (latitude, longitude)
- Include address components (street, city, country, postal_code)
- Support multiple coordinate reference systems if needed

### Currency and Pricing

- Always include currency code (ISO 4217)
- Use decimal type for prices to avoid floating-point issues
- Support price ranges for activities/accommodations

### Internationalization

- Accept `Accept-Language` header for localized content
- Return localized destination names and descriptions
- Support multiple currency display formats

### Time Zones

- Store all times in UTC
- Include timezone information for location-specific times
- Support user timezone preferences

## Performance Guidelines

### Caching

- Use ETags for conditional requests
- Implement cache headers for static/semi-static data
- Cache expensive queries (destination searches, recommendations)

### Response Optimization

- Use field selection: `?fields=name,country,rating`
- Implement resource embedding: `?include=reviews,photos`
- Compress responses with gzip

## Documentation Requirements

### FastAPI Integration

- Use Pydantic models for automatic schema generation
- Provide comprehensive docstrings for all endpoints
- Include example requests/responses in OpenAPI spec
- Tag endpoints by resource type for better organization

### API Documentation Standards

- Document all possible error responses
- Include rate limiting information
- Provide authentication examples
- Document pagination patterns clearly

## Related Documents

- [FastAPI Patterns](./fastapi-patterns.md)
- [Backend Architecture](../adr/001-backend-architecture-decisions.md)
- [API Security](../adr/003-api-security-implementation.md)

---

**Last Updated**: June 2025
