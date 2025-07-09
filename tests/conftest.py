"""
Test configuration and fixtures for the Wandr Backend API.

This module provides:
- Database fixtures for test isolation
- Authentication helpers for protected endpoints
- Test client configuration
- Common test utilities
"""

import os

from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.main import app
from app.models.user import User, UserProfile

# Test database URL - use in-memory SQLite for speed
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine with specific configuration for SQLite
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,
    },
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Event loop is handled by pytest-asyncio automatically


@pytest_asyncio.fixture
async def db_session():
    """
    Create a fresh database session for each test.

    This fixture:
    1. Creates all tables in the test database
    2. Provides a clean session for the test
    3. Rolls back all changes after the test
    4. Drops all tables for cleanup
    """
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

    # Drop all tables for cleanup
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_client(db_session: AsyncSession):
    """
    Create a test client with database dependency override.
    """

    # Override the database dependency
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client

    # Clean up dependency override
    app.dependency_overrides.clear()


@pytest.fixture
def sync_test_client():
    """
    Create a synchronous test client for simple endpoint testing.
    """
    return TestClient(app)


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """
    Create a test user in the database.

    Returns:
        User: The created test user
    """
    from app.core.security import get_password_hash

    # Create user
    hashed_password = get_password_hash("testpassword123")
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash=hashed_password,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create user profile
    profile = UserProfile(
        user_id=user.id,
        display_name="Test User",
        bio="Test user bio",
    )
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(profile)

    return user


@pytest_asyncio.fixture
async def test_user_token(test_user: User):
    """
    Create a JWT token for the test user.

    Args:
        test_user: The test user fixture

    Returns:
        str: JWT access token for the test user
    """
    return create_access_token(data={"sub": str(test_user.id)})


@pytest_asyncio.fixture
async def authenticated_client(test_client: AsyncClient, test_user_token: str):
    """
    Create an authenticated test client with Authorization header.

    Args:
        test_client: The test client fixture
        test_user_token: JWT token for the test user

    Returns:
        AsyncClient: Test client with authentication headers set
    """
    test_client.headers.update({"Authorization": f"Bearer {test_user_token}"})
    return test_client


@pytest_asyncio.fixture
async def second_test_user(db_session: AsyncSession):
    """
    Create a second test user for testing user interactions.

    Returns:
        User: The created second test user
    """
    from app.core.security import get_password_hash

    # Create second user
    hashed_password = get_password_hash("secondpassword123")
    user = User(
        email="second@example.com",
        username="seconduser",
        password_hash=hashed_password,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create user profile
    profile = UserProfile(
        user_id=user.id,
        display_name="Second User",
        bio="Second test user bio",
    )
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(profile)

    return user


# Test data factories
class TestDataFactory:
    """Factory class for creating test data."""

    @staticmethod
    def user_registration_data():
        """Valid user registration data."""
        return {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword123",
        }

    @staticmethod
    def user_login_data():
        """Valid user login data."""
        return {"email": "test@example.com", "password": "testpassword123"}

    @staticmethod
    def invalid_user_data():
        """Invalid user registration data for testing validation."""
        return {
            "email": "invalid-email",
            "username": "",
            "password": "123",  # Too short
        }

    @staticmethod
    def trip_data():
        """Valid trip creation data."""
        return {
            "title": "Test Trip",
            "description": "A test trip for testing purposes",
            "start_date": "2024-07-01",
            "end_date": "2024-07-15",
            "destination": "Test Destination",
        }

    @staticmethod
    def trip_update_data():
        """Valid trip update data."""
        return {
            "title": "Updated Test Trip",
            "description": "An updated test trip",
            "destination": "Updated Destination",
        }


@pytest.fixture
def test_data():
    """Provide access to test data factory."""
    return TestDataFactory


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Add custom markers
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "auth: mark test as authentication related")
    config.addinivalue_line("markers", "slow: mark test as slow running")


# Skip tests that require external services in CI
def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle CI environment."""
    if os.getenv("CI"):
        skip_slow = pytest.mark.skip(reason="Skipping slow tests in CI")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
