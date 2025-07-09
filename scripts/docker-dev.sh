#!/bin/bash

# Docker development script for Wandr Backend API
# This script provides convenient commands for Docker development workflow

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Display help
show_help() {
    echo "Docker Development Script for Wandr Backend API"
    echo ""
    echo "Usage: ./scripts/docker-dev.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build         Build the Docker images"
    echo "  up            Start the development environment"
    echo "  down          Stop the development environment"
    echo "  restart       Restart all services"
    echo "  logs          Show logs for all services"
    echo "  logs [service] Show logs for a specific service (app, db, redis)"
    echo "  shell         Open a shell in the app container"
    echo "  test          Run tests in Docker"
    echo "  migrate       Run database migrations"
    echo "  reset-db      Reset the database (WARNING: destroys all data)"
    echo "  format        Format code with Black and Ruff"
    echo "  lint          Run linting with Ruff and mypy"
    echo "  check         Run all code quality checks (lint + format check)"
    echo "  status        Show container status"
    echo "  clean         Remove all containers and volumes"
    echo "  help          Show this help message"
}

# Build images
build_images() {
    print_info "Building Docker images..."
    docker-compose build --no-cache
    print_success "Images built successfully"
}

# Start development environment
start_dev() {
    print_info "Starting development environment..."
    docker-compose up -d
    print_info "Waiting for services to be ready..."
    sleep 5
    print_success "Development environment started"
    print_info "API available at: http://localhost:8000"
    print_info "Database available at: localhost:5432"
    print_info "Redis available at: localhost:6379"
}

# Stop development environment
stop_dev() {
    print_info "Stopping development environment..."
    docker-compose down
    print_success "Development environment stopped"
}

# Restart services
restart_dev() {
    print_info "Restarting development environment..."
    docker-compose restart
    print_success "Development environment restarted"
}

# Show logs
show_logs() {
    if [ -z "$1" ]; then
        print_info "Showing logs for all services..."
        docker-compose logs -f
    else
        print_info "Showing logs for service: $1"
        docker-compose logs -f "$1"
    fi
}

# Open shell in app container
open_shell() {
    print_info "Opening shell in app container..."
    docker-compose exec app /bin/bash
}

# Run tests
run_tests() {
    print_info "Running tests in Docker..."
    docker-compose run --rm test
}

# Run database migrations
run_migrations() {
    print_info "Running database migrations..."
    docker-compose run --rm migrate
    print_success "Migrations completed"
}

# Reset database
reset_database() {
    print_warning "This will destroy all data in the database!"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Resetting database..."
        docker-compose down
        docker volume rm wandr-backend-app_postgres_data || true
        docker-compose up -d db
        sleep 10
        run_migrations
        print_success "Database reset completed"
    else
        print_info "Database reset cancelled"
    fi
}

# Show container status
show_status() {
    print_info "Container status:"
    docker-compose ps
}

# Format code
format_code() {
    print_info "Formatting code with Ruff..."
    docker-compose exec app ruff format . || docker-compose run --rm app ruff format .
    docker-compose exec app ruff check --fix . || docker-compose run --rm app ruff check --fix .
    print_success "Code formatting completed"
}

# Run linting
run_linting() {
    print_info "Running linting with Ruff and mypy..."
    docker-compose exec app ruff check . || docker-compose run --rm app ruff check .
    docker-compose exec app mypy . || docker-compose run --rm app mypy .
    print_success "Linting completed"
}

# Run all code quality checks
run_code_quality_checks() {
    print_info "Running all code quality checks..."
    docker-compose exec app ruff format --check . || docker-compose run --rm app ruff format --check .
    docker-compose exec app ruff check . || docker-compose run --rm app ruff check .
    docker-compose exec app mypy . || docker-compose run --rm app mypy .
    print_success "All code quality checks completed"
}

# Clean up everything
clean_all() {
    print_warning "This will remove all containers, volumes, and images!"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning up..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        print_success "Cleanup completed"
    else
        print_info "Cleanup cancelled"
    fi
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Main command handling
main() {
    check_docker

    case "${1:-help}" in
        build)
            build_images
            ;;
        up)
            start_dev
            ;;
        down)
            stop_dev
            ;;
        restart)
            restart_dev
            ;;
        logs)
            show_logs "$2"
            ;;
        shell)
            open_shell
            ;;
        test)
            run_tests
            ;;
        migrate)
            run_migrations
            ;;
        reset-db)
            reset_database
            ;;
        format)
            format_code
            ;;
        lint)
            run_linting
            ;;
        check)
            run_code_quality_checks
            ;;
        status)
            show_status
            ;;
        clean)
            clean_all
            ;;
        help|*)
            show_help
            ;;
    esac
}

# Run main function
main "$@"
