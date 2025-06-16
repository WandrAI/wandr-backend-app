# Wandr Backend API

Backend services for powering AI-driven travel recommendations, social collaboration, and real-time travel assistance.

## 🎯 Project Overview

The Wandr Backend API provides the server-side infrastructure for the Wandr mobile app, enabling:

- **AI-Powered Travel Assistance**: Real-time conversational AI for travel planning and recommendations
- **Hyper-Local Recommendations**: Location-based suggestions using travel APIs and machine learning
- **Social Collaboration**: Group trip planning, real-time collaboration, and expense sharing
- **User Personalization**: Profile management, preferences, and personalized travel content
- **Real-Time Features**: Live collaboration, notifications, and synchronized travel planning

## 🏗️ Architecture

### **Tech Stack**
- **Framework**: FastAPI (Python 3.11+) with async/await patterns
- **API Design**: RESTful APIs + GraphQL for complex travel queries
- **Database**: PostgreSQL with PostGIS + Redis for caching/sessions
- **Authentication**: JWT with FastAPI Security utilities
- **Real-Time**: WebSockets with Redis pub/sub for collaboration
- **AI Integration**: Direct OpenAI/Anthropic APIs with service abstraction
- **Task Queue**: Celery with Redis for background processing
- **Documentation**: Automatic OpenAPI/Swagger + comprehensive ADRs

### **API Design Philosophy**
- **RESTful APIs** with clear resource endpoints
- **Async/await** patterns for optimal performance
- **Type-safe** with Pydantic models and type hints
- **Travel-domain focused** with intuitive endpoint naming
- **Mobile-optimized** responses with efficient data structures
- **Real-time capabilities** for collaborative features

## 📱 Mobile App Integration

This backend serves the [Wandr Mobile App](../mobile-app) built with React Native + Tamagui.

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
└── Mobile-optimized data fetching
```

## 🚀 Development Phases

### **Phase 1 - Foundation** ⚡ *Current*
- [x] Project setup with FastAPI
- [x] Documentation structure
- [x] Cursor rules for AI assistance
- [ ] Database models and migrations
- [ ] Authentication system
- [ ] Basic user management APIs
- [ ] Development environment setup

### **Phase 2 - Core Travel APIs** 
- [ ] AI chat interface and conversation handling
- [ ] Travel recommendation engine
- [ ] Location-based services integration
- [ ] User preferences and personalization
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

### **Prerequisites**
- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Git

### **Installation** *(Coming Soon)*
```bash
# Clone the repository
git clone <repository-url>
cd wandr-backend-app

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### **API Documentation**
Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 Documentation

Comprehensive documentation following the mobile app's proven patterns:

- **Architecture Decision Records**: `/docs/adr/` - Backend architectural decisions
- **API Specifications**: `/docs/api/` - Detailed endpoint documentation  
- **Development Guide**: `/docs/development/` - Setup and development patterns
- **Deployment Guide**: `/docs/deployment/` - Production deployment instructions

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
- **CORS Configuration** for mobile app integration
- **Environment-based Secrets** management

## 🌍 Travel-Specific Considerations

- **Location Privacy**: Secure handling of user location data
- **Multi-Currency**: Support for international travel
- **Multi-Language**: API responses ready for localization
- **Offline Sync**: APIs designed for offline mobile app usage
- **Real-Time Collaboration**: WebSocket support for group planning
- **Travel Data Integration**: Structured for external travel APIs

---

**Built with ❤️ for travelers worldwide**  
*Making travel planning seamless, social, and smart.* 