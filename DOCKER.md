# Docker Setup for Wandr Backend API

This guide covers how to run the Wandr Backend API using Docker for both development and production environments.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM available for containers

## Quick Start (Development)

1. **Start the development environment:**
   ```bash
   ./scripts/docker-dev.sh up
   ```

2. **Run database migrations:**
   ```bash
   ./scripts/docker-dev.sh migrate
   ```

3. **Access the API:**
   - API: http://localhost:8000
   - Interactive API docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## Development Commands

The `docker-dev.sh` script provides convenient commands for development:

```bash
# Build images
./scripts/docker-dev.sh build

# Start development environment
./scripts/docker-dev.sh up

# Stop development environment
./scripts/docker-dev.sh down

# View logs
./scripts/docker-dev.sh logs
./scripts/docker-dev.sh logs app    # Specific service

# Run tests
./scripts/docker-dev.sh test

# Open shell in app container
./scripts/docker-dev.sh shell

# Run database migrations
./scripts/docker-dev.sh migrate

# Reset database (WARNING: destroys data)
./scripts/docker-dev.sh reset-db

# Show container status
./scripts/docker-dev.sh status

# Clean up everything
./scripts/docker-dev.sh clean
```

## Development Services

The development environment includes:

- **app**: FastAPI application with hot reload
- **db**: PostgreSQL 15 with PostGIS extension
- **redis**: Redis for caching and background tasks
- **migrate**: One-time migration runner
- **test**: Test runner service

### Service URLs

- **API**: http://localhost:8000
- **Database**: localhost:5432
- **Redis**: localhost:6379

### Environment Variables

Development environment uses these default values:

```bash
DATABASE_URL=postgresql+asyncpg://wandr_user:wandr_password@db:5432/wandr_db
REDIS_URL=redis://redis:6379/0
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production
```

## Production Deployment

### 1. Environment Setup

Create a `.env` file with production values:

```bash
# Database
POSTGRES_PASSWORD=your_secure_password_here

# Security
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2. Start Production Services

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Run Migrations

```bash
docker-compose -f docker-compose.prod.yml run --rm migrate
```

### 4. SSL/TLS Setup

Place your SSL certificates in the `ssl/` directory:

```
ssl/
├── cert.pem
└── key.pem
```

Update the nginx configuration to use HTTPS.

## Docker Images

### Multi-stage Build

The Dockerfile uses multi-stage builds with these stages:

1. **base**: Base Python image with system dependencies
2. **dependencies**: Python dependencies installation
3. **development**: Development image with hot reload
4. **production**: Optimized production image

### Image Sizes

- Development: ~800MB (includes dev tools)
- Production: ~500MB (optimized for size)

## Volumes

### Development Volumes

- `postgres_data`: Database data persistence
- `redis_data`: Redis data persistence
- Source code is mounted for hot reload

### Production Volumes

- `postgres_data`: Database data persistence
- `redis_data`: Redis data persistence
- SSL certificates mounted read-only

## Networking

### Development Network

- Network name: `wandr-network`
- All services can communicate using service names

### Production Network

- Network name: `wandr-network-prod`
- Nginx reverse proxy handles external traffic
- Internal services communicate securely

## Health Checks

All services include health checks:

- **app**: HTTP health endpoint
- **db**: PostgreSQL readiness check
- **redis**: Redis ping command
- **nginx**: HTTP proxy health check

## Resource Limits

### Development

No resource limits set for development flexibility.

### Production

Resource limits configured for production stability:

- **app**: 1 CPU, 1GB RAM
- **db**: 1 CPU, 2GB RAM
- **redis**: 0.5 CPU, 512MB RAM

## Database Configuration

### PostgreSQL Extensions

The database is configured with these extensions:

- **PostGIS**: Geographic data support
- **uuid-ossp**: UUID generation
- **pg_trgm**: Text search optimization
- **btree_gin**: Advanced indexing
- **btree_gist**: Advanced indexing

### Migrations

Database schema is managed by Alembic:

```bash
# Run migrations
docker-compose run --rm migrate

# Generate new migration
docker-compose exec app alembic revision --autogenerate -m "description"
```

## Monitoring

### Logs

View logs for all services:

```bash
docker-compose logs -f
```

View logs for specific service:

```bash
docker-compose logs -f app
```

### Container Status

Check container health:

```bash
docker-compose ps
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Stop conflicting services
   sudo lsof -i :8000  # Find process using port
   sudo kill -9 <PID>  # Kill process
   ```

2. **Database connection failed**
   ```bash
   # Check database health
   docker-compose exec db pg_isready -U wandr_user
   
   # Restart database
   docker-compose restart db
   ```

3. **Permission denied**
   ```bash
   # Fix file permissions
   chmod +x scripts/docker-dev.sh
   
   # Fix volume permissions
   docker-compose down
   docker volume rm wandr-backend-app_postgres_data
   docker-compose up -d
   ```

### Reset Everything

If you encounter persistent issues:

```bash
# Complete reset
./scripts/docker-dev.sh clean
./scripts/docker-dev.sh build
./scripts/docker-dev.sh up
./scripts/docker-dev.sh migrate
```

### Debug Mode

Run services in debug mode:

```bash
# Run with debug output
docker-compose up --verbose

# Run specific service interactively
docker-compose run --rm app /bin/bash
```

## Security Considerations

### Development

- Uses default passwords (change for production)
- Debug mode enabled
- CORS allows localhost origins

### Production

- Requires strong passwords via environment variables
- Debug mode disabled
- Strict CORS configuration
- SSL/TLS encryption
- Security headers via Nginx
- Rate limiting enabled
- Resource limits enforced

## Performance Optimization

### Development

- Hot reload enabled for fast development
- Volume mounts for instant code changes
- Debug tools included

### Production

- Multi-worker Gunicorn/Uvicorn setup
- Nginx reverse proxy with caching
- Database connection pooling
- Redis caching layer
- Gzip compression enabled
- Resource limits prevent resource exhaustion

## Backup and Recovery

### Database Backup

```bash
# Create backup
docker-compose exec db pg_dump -U wandr_user wandr_db > backup.sql

# Restore backup
docker-compose exec -T db psql -U wandr_user wandr_db < backup.sql
```

### Volume Backup

```bash
# Backup volumes
docker run --rm -v wandr-backend-app_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Restore volumes
docker run --rm -v wandr-backend-app_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```