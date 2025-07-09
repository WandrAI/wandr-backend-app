# Wandr Backend API - Development Context

## 🎯 Project Overview

**Wandr Backend API** is a modern FastAPI-based travel application backend providing:
- JWT-based user authentication and management
- Travel domain models (Users, Trips, Locations) with collaborative features
- RESTful APIs with automatic OpenAPI documentation
- Async database operations with SQLAlchemy 2.0
- Database migrations with Alembic

**Current Phase**: Foundation (Phase 1) ✅ Completed, moving to Core Travel APIs (Phase 2)

## 📊 Current Status & Todo List

### ✅ **Completed Tasks (10/12)**
- [x] **Core dependencies** - FastAPI, SQLAlchemy 2.0, Pydantic, Alembic, JWT libraries
- [x] **Database configuration** - Async SQLAlchemy with SQLite (dev) / PostgreSQL (prod) support
- [x] **Core models** - User, UserProfile, Trip, TripMember, TripActivity, Location
- [x] **Database migrations** - Alembic setup with initial migration applied
- [x] **JWT authentication** - Secure token-based auth with bcrypt password hashing
- [x] **User auth endpoints** - Registration, login, profile access with proper validation
- [x] **Pydantic schemas** - Type-safe request/response models with comprehensive validation
- [x] **Error handling** - Custom exception handlers with consistent HTTP responses
- [x] **Basic CRUD endpoints** - Complete trip and user management APIs with collaboration features
- [x] **Docker environment** - Complete containerized development setup with PostgreSQL and Redis

### ⏳ **Pending (2/12)**
- [ ] **Testing framework** - pytest setup with async test patterns
- [ ] **Location services** - Geographic data handling with PostGIS

## 🚀 Development Workflow

### **Quick Start Commands**

**Docker Development (Recommended):**
```bash
# Start complete development environment
./scripts/docker-dev.sh up

# Run database migrations
./scripts/docker-dev.sh migrate

# View logs
./scripts/docker-dev.sh logs

# Run tests
./scripts/docker-dev.sh test

# Open container shell
./scripts/docker-dev.sh shell

# Stop environment
./scripts/docker-dev.sh down
```

**Local Development:**
```bash
# Activate environment
source .venv/bin/activate

# Start development server (choose one)
fastapi dev app/main.py --port 8000        # FastAPI CLI (recommended)
uvicorn app.main:app --reload --port 8000  # Uvicorn (traditional)

# Database operations
alembic upgrade head                        # Apply migrations
alembic revision --autogenerate -m "msg"   # Create new migration
```

### **API Testing**
```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "username": "testuser", "password": "testpass123"}'

# Login (get JWT token)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'

# Create trip (use token from login)
curl -X POST "http://localhost:8000/api/v1/trips" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title": "European Adventure", "description": "2-week trip", "start_date": "2024-06-01", "end_date": "2024-06-14"}'

# List user trips
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" http://localhost:8000/api/v1/trips
```

### **Documentation Access**
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Architecture Docs**: `/docs/adr/` directory

## 🏗️ Architecture Context

### **Tech Stack**
- **Framework**: FastAPI with async/await patterns
- **Database**: SQLAlchemy 2.0 async + Alembic migrations
- **Authentication**: JWT tokens + bcrypt password hashing
- **Validation**: Pydantic v2 with type safety
- **Development DB**: PostgreSQL with PostGIS (Docker) / SQLite (local)
- **Production DB**: PostgreSQL with PostGIS
- **Caching**: Redis for caching and background tasks
- **Containerization**: Docker with multi-stage builds and docker-compose

### **Project Structure**
```
app/
├── __init__.py              # Package marker
├── main.py                  # FastAPI application entry point
├── core/                    # Core infrastructure
│   ├── config.py           # Environment-based settings
│   ├── database.py         # Async SQLAlchemy setup
│   ├── security.py         # JWT auth and password hashing
│   └── exceptions.py       # Custom exception handlers
├── models/                  # Database models
│   ├── user.py             # User and UserProfile models
│   ├── trip.py             # Trip, TripMember, TripActivity models
│   └── location.py         # Location model with coordinates
├── schemas/                 # Pydantic request/response models
│   ├── user.py             # User auth and profile schemas
│   └── common.py           # Shared schemas
└── api/v1/                  # API endpoints
    └── auth.py             # Authentication endpoints
```

### **Key Design Decisions**
- **Async-first**: All database operations use async/await
- **Type safety**: Pydantic models + SQLAlchemy typing throughout
- **Travel domain**: Models designed for collaborative trip planning
- **JWT stateless**: Enables offline-capable client applications
- **Environment flexibility**: SQLite for dev, PostgreSQL for production

## 🎯 Next Steps (Immediate Priorities)

### **1. Set Up Testing Framework** (Next Priority)
**Task**: Implement pytest with async support
**Requirements**:
- Test configuration with test database
- Authentication endpoint tests
- Database model tests
- Integration tests for API endpoints

**Docker Testing**: Use `./scripts/docker-dev.sh test` to run tests in containerized environment

### **2. Location Services** (Future)
**Task**: Implement geographic data handling
**Requirements**:
- Location search and filtering
- Distance calculations
- PostGIS integration (already available in Docker environment)

## 🧪 Testing Current Implementation

### **Verify Authentication Flow**

**Using Docker:**
1. **Start environment**: `./scripts/docker-dev.sh up`
2. **Run migrations**: `./scripts/docker-dev.sh migrate`
3. **Register user**: Use curl command above or Swagger UI at `/docs`
4. **Login**: Get JWT token from login response
5. **Access profile**: Use token in Authorization header: `Bearer <token>`

**Using Local Development:**
1. **Start server**: `fastapi dev app/main.py --port 8000`
2. **Register user**: Use curl command above or Swagger UI at `/docs`
3. **Login**: Get JWT token from login response
4. **Access profile**: Use token in Authorization header: `Bearer <token>`

### **Database Verification**

**Docker Environment:**
- **Check database**: Connect to PostgreSQL at `localhost:5432`
- **Verify tables**: Use `./scripts/docker-dev.sh shell` then `psql` commands
- **Test migrations**: `./scripts/docker-dev.sh migrate` should run without errors

**Local Environment:**
- **Check database**: SQLite file `wandr.db` should exist
- **Verify tables**: User, user_profiles, trips, trip_members, etc.
- **Test migrations**: `alembic upgrade head` should run without errors

## 🔧 Common Development Tasks

### **Database Reset (Development)**

**Docker Environment:**
```bash
# Quick reset (removes all data)
./scripts/docker-dev.sh reset-db

# Manual reset
./scripts/docker-dev.sh down
docker volume rm wandr-backend-app_postgres_data
./scripts/docker-dev.sh up
./scripts/docker-dev.sh migrate
```

**Local Environment:**
```bash
# Quick reset (removes all data)
rm wandr.db
alembic upgrade head

# Reset with fresh migration
rm wandr.db && rm -rf alembic/versions/*.py
alembic revision --autogenerate -m "Fresh schema"
alembic upgrade head

# Schema reset (keep migration history)
alembic downgrade base
alembic upgrade head
```

### **Adding New API Endpoints**
1. Create Pydantic schemas in `app/schemas/`
2. Add business logic to `app/services/` (create if needed)
3. Create API router in `app/api/v1/`
4. Include router in `app/main.py`
5. Test with `/docs` interface

### **Database Schema Changes**
1. Modify models in `app/models/`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review generated migration file
4. Apply migration: `alembic upgrade head`

### **Adding Dependencies**
1. Add to `requirements.txt`
2. Install: `pip install -r requirements.txt`
3. Update if needed for compatibility

## 🚨 Known Issues & Solutions

### **bcrypt Version Warning**
- **Issue**: `(trapped) error reading bcrypt version` during password hashing
- **Impact**: Cosmetic only - password hashing works correctly
- **Solution**: Ignore for development, will be fixed in future dependency update

### **FastAPI CLI vs Uvicorn**
- **FastAPI CLI**: `fastapi dev app/main.py --port 8000` (pretty output, file path)
- **Uvicorn**: `uvicorn app.main:app --reload --port 8000` (traditional, module path)
- **Both work**: Use whichever you prefer

## 🎖️ Development Best Practices

### **Code Quality**
- **Type hints**: Use throughout for better IDE support and validation
- **Async patterns**: Prefer async/await for all I/O operations
- **Error handling**: Use custom exceptions with proper HTTP status codes
- **Documentation**: Update docstrings and API descriptions

### **Database**
- **Migrations**: Always create migrations for schema changes
- **Relationships**: Use SQLAlchemy relationships for data integrity
- **Validation**: Leverage Pydantic for comprehensive input validation

### **Security**
- **JWT tokens**: Include user ID in token payload, validate on each request
- **Password hashing**: Never store plain text passwords
- **Input validation**: Validate all inputs with Pydantic schemas

---

**Last Updated**: July 2025 | **Status**: Phase 1 Complete, Phase 2 In Progress