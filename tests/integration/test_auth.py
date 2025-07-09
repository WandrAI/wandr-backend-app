"""
Integration tests for authentication endpoints.

Tests cover:
- User registration with validation
- User login and JWT token generation
- Protected endpoint access
- Profile retrieval and updates
- Error handling and edge cases
"""

from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from tests.test_database import DatabaseTestUtils


@pytest.mark.integration
@pytest.mark.auth
class TestUserRegistration:
    """Test user registration endpoint."""

    async def test_register_user_success(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test successful user registration."""
        registration_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
        }

        response = await test_client.post(
            "/api/v1/auth/register", json=registration_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == registration_data["email"]
        assert data["username"] == registration_data["username"]
        assert "id" in data
        assert "password_hash" not in data  # Password should not be returned
        assert "hashed_password" not in data  # Password should not be returned

        # Verify user was created in database
        assert await DatabaseTestUtils.verify_user_exists(
            db_session, registration_data["email"]
        )

    async def test_register_user_duplicate_email(
        self, test_client: AsyncClient, test_user: User
    ):
        """Test registration with duplicate email fails."""
        registration_data = {
            "email": test_user.email,  # Duplicate email
            "username": "differentuser",
            "password": "password123",
        }

        response = await test_client.post(
            "/api/v1/auth/register", json=registration_data
        )

        assert response.status_code == 400
        data = response.json()
        assert "email" in data["detail"].lower()

    async def test_register_user_duplicate_username(
        self, test_client: AsyncClient, test_user: User
    ):
        """Test registration with duplicate username fails."""
        registration_data = {
            "email": "different@example.com",
            "username": test_user.username,  # Duplicate username
            "password": "password123",
        }

        response = await test_client.post(
            "/api/v1/auth/register", json=registration_data
        )

        assert response.status_code == 400
        data = response.json()
        assert "username" in data["detail"].lower()

    @pytest.mark.parametrize(
        "invalid_data",
        [
            {"email": "invalid-email", "username": "user", "password": "password123"},
            {"email": "test@example.com", "username": "", "password": "password123"},
            {
                "email": "test@example.com",
                "username": "user",
                "password": "123",
            },  # Too short
            {"email": "", "username": "user", "password": "password123"},
            {},  # Missing fields
        ],
    )
    async def test_register_user_invalid_data(
        self, test_client: AsyncClient, invalid_data
    ):
        """Test registration with invalid data fails with validation errors."""
        response = await test_client.post("/api/v1/auth/register", json=invalid_data)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


@pytest.mark.integration
@pytest.mark.auth
class TestUserLogin:
    """Test user login endpoint."""

    async def test_login_success(self, test_client: AsyncClient, test_user: User):
        """Test successful login returns JWT token."""
        login_data = {
            "email": test_user.email,
            "password": "testpassword123",  # Password from test_user fixture
        }

        response = await test_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        # Note: Login response doesn't include user info, only token

    async def test_login_wrong_password(
        self, test_client: AsyncClient, test_user: User
    ):
        """Test login with wrong password fails."""
        login_data = {"email": test_user.email, "password": "wrongpassword"}

        response = await test_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_login_nonexistent_user(self, test_client: AsyncClient):
        """Test login with non-existent email fails."""
        login_data = {"email": "nonexistent@example.com", "password": "password123"}

        response = await test_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_login_inactive_user(
        self, test_client: AsyncClient, db_session: AsyncSession
    ):
        """Test login with inactive user fails."""
        # Create inactive user
        from app.core.security import get_password_hash

        inactive_user = User(
            email="inactive@example.com",
            username="inactiveuser",
            hashed_password=get_password_hash("password123"),
            is_active=False,  # Inactive user
        )
        db_session.add(inactive_user)
        await db_session.commit()

        login_data = {"email": inactive_user.email, "password": "password123"}

        response = await test_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 400
        data = response.json()
        assert "inactive" in data["detail"].lower()


@pytest.mark.integration
@pytest.mark.auth
class TestUserProfile:
    """Test user profile endpoints."""

    async def test_get_profile_authenticated(
        self, authenticated_client: AsyncClient, test_user: User
    ):
        """Test getting user profile with valid token."""
        response = await authenticated_client.get("/api/v1/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert data["id"] == test_user.id
        assert data["is_active"] == test_user.is_active
        # Profile data should be included
        assert "profile" in data

    async def test_get_profile_unauthenticated(self, test_client: AsyncClient):
        """Test getting profile without authentication fails."""
        response = await test_client.get("/api/v1/auth/me")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_get_profile_invalid_token(self, test_client: AsyncClient):
        """Test getting profile with invalid token fails."""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = await test_client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    # Note: Profile update endpoint doesn't exist in auth routes
    # Profile updates are handled via /api/v1/users/me/profile
    async def test_update_profile_endpoint_does_not_exist(
        self, authenticated_client: AsyncClient, test_user: User
    ):
        """Test that profile update endpoint doesn't exist in auth routes."""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "bio": "Updated bio text",
            "timezone": "America/New_York",
        }

        response = await authenticated_client.put(
            "/api/v1/auth/profile", json=update_data
        )

        assert response.status_code == 404  # Endpoint doesn't exist


@pytest.mark.integration
@pytest.mark.auth
class TestTokenValidation:
    """Test JWT token validation and security."""

    async def test_token_contains_user_id(self, test_user_token: str, test_user: User):
        """Test that JWT token contains the correct user ID."""
        from app.core.security import decode_access_token

        payload = decode_access_token(test_user_token)
        assert payload is not None
        assert payload["sub"] == str(test_user.id)

    async def test_expired_token_rejected(self, test_client: AsyncClient):
        """Test that expired tokens are rejected."""
        # Create a token with very short expiration
        from datetime import timedelta

        from app.core.security import create_access_token

        expired_token = create_access_token(
            data={"sub": "1"},
            expires_delta=timedelta(seconds=-1),  # Already expired
        )

        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await test_client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_malformed_token_rejected(self, test_client: AsyncClient):
        """Test that malformed tokens are rejected."""
        malformed_tokens = [
            "Bearer",  # Missing token
            "Bearer malformed.token.here",  # Invalid format
            "InvalidScheme valid_token_here",  # Wrong auth scheme
            "",  # Empty header
        ]

        for token in malformed_tokens:
            headers = {"Authorization": token} if token else {}
            response = await test_client.get("/api/v1/auth/me", headers=headers)
            assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.auth
class TestPasswordSecurity:
    """Test password security features."""

    async def test_password_is_hashed(self, db_session: AsyncSession):
        """Test that passwords are properly hashed in database."""
        from app.core.security import get_password_hash

        password = "testpassword123"
        hashed = get_password_hash(password)

        # Hash should not equal original password
        assert hashed != password

        # Hash should be consistent
        assert get_password_hash(password) != hashed  # bcrypt uses random salt

        # Verify password function should work
        from app.core.security import verify_password

        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)

    async def test_password_not_returned_in_responses(self, test_client: AsyncClient):
        """Test that password fields are never returned in API responses."""
        # Registration response
        registration_data = {
            "email": "security@example.com",
            "username": "securitytest",
            "password": "securepassword123",
        }

        response = await test_client.post(
            "/api/v1/auth/register", json=registration_data
        )
        assert response.status_code == 200
        data = response.json()

        # Check that no password-related fields are in response
        password_fields = ["password", "hashed_password", "password_hash", "hash"]
        for field in password_fields:
            assert field not in data
            assert field not in str(data).lower()
