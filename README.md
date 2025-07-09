# Wandr Backend API

Backend API services for powering AI-driven travel recommendations, social collaboration, and real-time travel assistance.

## 🎯 Project Overview

The Wandr Backend API provides the server-side infrastructure for travel applications, enabling:

- **AI-Powered Travel Assistance**: Real-time conversational AI for travel planning and recommendations
- **Hyper-Local Recommendations**: Location-based suggestions using travel APIs and machine learning
- **Social Collaboration**: Group trip planning, real-time collaboration, and expense sharing
- **User Personalization**: Profile management, preferences, and personalized travel content
- **Real-Time Features**: Live collaboration, notifications, and synchronized travel planning

## 🏗️ Architecture

### **Tech Stack**

- **Framework**: FastAPI (Python 3.12) with async/await patterns
- **Database**: SQLite (development) / PostgreSQL with PostGIS (production)
- **Authentication**: JWT with FastAPI Security utilities + bcrypt
- **Data Validation**: Pydantic v2 with type safety
- **Migrations**: Alembic for database version control
- **API Documentation**: Automatic OpenAPI/Swagger + ReDoc
- **Development**: Hot reload, async SQLAlchemy 2.0
- **Future**: GraphQL, WebSockets, Redis, Celery, AI integration

### **API Design Philosophy**

- **RESTful APIs** with clear resource endpoints
- **Async/await** patterns for optimal performance
- **Type-safe** with Pydantic models and type hints
- **Travel-domain focused** with intuitive endpoint naming
- **Client-optimized** responses with efficient data structures
- **Real-time capabilities** for collaborative features

## 🔌 Client Integration

This backend provides RESTful and GraphQL APIs for various client applications.

### **API Endpoints Overview**

```
/api/v1/ (REST API)
├── auth/              # Authentication & user management
├── users/             # User profiles & preferences
├── trips/             # Trip CRUD operations
├── recommendations/   # Travel recommendations & data
├── groups/            # Group trip management
├── ai/                # AI assistant & chat interface
├── locations/         # Location-based services
├── social/            # Social features & sharing
└── notifications/     # Push notifications & alerts

/graphql (GraphQL API)
├── Complex travel queries with nested data
├── Real-time collaboration subscriptions
├── Advanced search and filtering
└── Optimized data fetching for client applications
```

## 🚀 Development Phases

### **Phase 1 - Foundation** ✅ _Completed_

- [x] Project setup with FastAPI
- [x] Documentation structure
- [x] Cursor rules for AI assistance
- [x] Database models and migrations
- [x] Authentication system (JWT)
- [x] Basic user management APIs
- [x] Development environment setup

### **Phase 2 - Core Travel APIs** 🔄 _In Progress_

- [x] Trip management CRUD operations
- [x] User profile management
- [x] Collaborative trip planning features
- [ ] AI chat interface and conversation handling
- [ ] Travel recommendation engine
- [ ] Location-based services integration
- [ ] External travel API integrations

### **Phase 3 - Social & Collaboration**

- [ ] Group trip management APIs
- [ ] Real-time collaboration (WebSockets)
- [ ] Expense tracking and splitting
- [ ] Social sharing and discovery features
- [ ] Push notification system

### **Phase 4 - Advanced Features**

- [ ] Advanced AI personalization
- [ ] Machine learning recommendation improvements
- [ ] Travel service integrations (booking, transport)
- [ ] Offline data synchronization support
- [ ] Performance optimization and caching

## 🛠️ Getting Started

### **🐳 Docker Setup (Recommended)**

The fastest way to get started is using Docker, which provides a complete development environment.

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd wandr-backend-app
   ```

2. **Start the development environment:**

   ```bash
   ./scripts/docker-dev.sh up
   ```

3. **Run database migrations:**

   ```bash
   ./scripts/docker-dev.sh migrate
   ```

4. **🎉 You're Ready!**
   - API: http://localhost:8000
   - Interactive API docs: http://localhost:8000/docs
   - Database: localhost:5432 (PostgreSQL)
   - Redis: localhost:6379

#### **Essential Docker Commands**

```bash
# Start development environment
./scripts/docker-dev.sh up

# Stop development environment
./scripts/docker-dev.sh down

# View logs
./scripts/docker-dev.sh logs

# Run tests
./scripts/docker-dev.sh test

# Format code (Black + Ruff)
./scripts/docker-dev.sh format

# Run linting (Ruff + mypy)
./scripts/docker-dev.sh lint

# Check code quality
./scripts/docker-dev.sh check

# Open shell in container
./scripts/docker-dev.sh shell

# Reset database (destroys data)
./scripts/docker-dev.sh reset-db

# See all available commands
./scripts/docker-dev.sh help
```

### **💻 Local Development Setup**

### **Prerequisites**

**Option 1: Docker (Recommended)**

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM available for containers

**Option 2: Local Development**

- Python 3.11+ (recommended: 3.12)
- Git

_Note: Docker provides a complete environment with PostgreSQL and Redis. For local development, the project uses SQLite (no additional database setup required)._

### **Quick Start**

1. **Clone and setup the project:**

   ```bash
   # Clone the repository
   git clone <repository-url>
   cd wandr-backend-app

   # Setup virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment (optional for development):**

   ```bash
   # Copy environment template (optional - defaults work for development)
   cp .env.example .env
   # Edit .env if you want to customize settings
   ```

4. **Run database migrations:**

   ```bash
   alembic upgrade head
   ```

5. **Install code quality tools:**

   ```bash
   # Install pre-commit hooks for automatic code formatting
   pre-commit install
   ```

6. **Start the development server:**

   **Option 1: FastAPI CLI (recommended):**

   ```bash
   fastapi dev app/main.py --port 8000
   ```

   **Option 2: Uvicorn:**

   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

#### **Local Code Quality Commands**

```bash
# Format code
black .
ruff check --fix .

# Check code quality
ruff check .
mypy .

# Run pre-commit hooks manually
pre-commit run --all-files
```

### **🎉 You're Ready!**

The API server will start at **http://localhost:8000**

### **API Documentation**

Once running, visit:

- **Interactive API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### **Try the API**

**Register a new user:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpassword123"
  }'
```

**Login and get a token:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

**Create a trip:**

```bash
curl -X POST "http://localhost:8000/api/v1/trips" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "European Adventure",
    "description": "2-week trip across Europe",
    "start_date": "2024-06-01",
    "end_date": "2024-06-14"
  }'
```

**List your trips:**

```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/api/v1/trips
```

### **Development Features**

- ✅ **Hot Reload**: Code changes automatically restart the server
- ✅ **Auto Documentation**: Interactive API docs at `/docs`
- ✅ **JWT Authentication**: Secure user registration and login
- ✅ **Trip Management**: Complete CRUD operations with collaboration
- ✅ **User Profiles**: Profile management and public user info
- ✅ **Permission System**: Role-based trip access (organizer/participant/viewer)
- ✅ **Docker Environment**: Complete containerized development setup
- ✅ **PostgreSQL Database**: Production-ready database with PostGIS
- ✅ **Redis Caching**: Fast caching and background task support
- ✅ **Type Safety**: Full Pydantic validation
- ✅ **Error Handling**: Comprehensive HTTP error responses

## 📚 Documentation

Comprehensive documentation following the mobile app's proven patterns:

- **Architecture Decision Records**: `/docs/adr/` - Backend architectural decisions
- **API Specifications**: `/docs/api/` - Detailed endpoint documentation
- **Development Guide**: `/docs/development/` - Setup and development patterns
- **Docker Setup**: `DOCKER.md` - Complete Docker development and deployment guide
- **Deployment Guide**: `/docs/deployment/` - Production deployment instructions
- **Development Context**: `CLAUDE.md` - AI assistant context and quick reference

## 🧪 Testing Strategy

- **Unit Tests**: Individual function and service testing
- **Integration Tests**: API endpoint and database testing
- **Load Testing**: Performance testing for travel peak loads
- **AI Testing**: Conversation flow and recommendation accuracy testing

## 🔒 Security

- **JWT Authentication** with secure token handling
- **Rate Limiting** to prevent abuse
- **Input Validation** with Pydantic models
- **SQL Injection Protection** via SQLAlchemy ORM
- **CORS Configuration** for client application integration
- **Environment-based Secrets** management

## 🌍 Travel-Specific Considerations

- **Location Privacy**: Secure handling of user location data
- **Multi-Currency**: Support for international travel
- **Multi-Language**: API responses ready for localization
- **Offline Sync**: APIs designed for offline-capable client applications
- **Real-Time Collaboration**: WebSocket support for group planning
- **Travel Data Integration**: Structured for external travel APIs

---

**Built with ❤️ for travelers worldwide**
_Making travel planning seamless, social, and smart._
