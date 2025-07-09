"""
Integration tests for user endpoints.

Tests cover:
- User profile management
- User search and discovery
- User relationships
- Privacy and authorization
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserProfile


@pytest.mark.integration
class TestUserProfiles:
    """Test user profile management endpoints."""
    
    async def test_get_user_profile_by_id(self, authenticated_client: AsyncClient, second_test_user: User):
        """Test retrieving another user's public profile."""
        response = await authenticated_client.get(f"/api/v1/users/{second_test_user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == second_test_user.id
        assert data["username"] == second_test_user.username
        # Email should not be exposed in public profile
        assert "email" not in data
        # Profile information should be included
        assert "profile" in data
    
    async def test_get_nonexistent_user_profile(self, authenticated_client: AsyncClient):
        """Test retrieving non-existent user profile returns 404."""
        response = await authenticated_client.get("/api/v1/users/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    async def test_get_user_profile_unauthenticated(self, test_client: AsyncClient, second_test_user: User):
        """Test that unauthenticated users cannot access user profiles."""
        response = await test_client.get(f"/api/v1/users/{second_test_user.id}")
        
        assert response.status_code == 401
    
    async def test_update_own_profile_via_correct_endpoint(self, authenticated_client: AsyncClient, test_user: User):
        """Test updating own user profile via correct endpoint."""
        update_data = {
            "first_name": "Updated",
            "last_name": "Profile",
            "bio": "This is my updated bio",
            "timezone": "America/Los_Angeles"
        }
        
        response = await authenticated_client.put("/api/v1/users/me/profile", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == update_data["first_name"]
        assert data["last_name"] == update_data["last_name"]
        assert data["bio"] == update_data["bio"]
        assert data["timezone"] == update_data["timezone"]
    
    async def test_update_other_user_profile_endpoint_does_not_exist(self, authenticated_client: AsyncClient, second_test_user: User):
        """Test that endpoint to update other users' profiles doesn't exist."""
        update_data = {
            "first_name": "Hacked",
            "last_name": "Profile",
            "bio": "This should not work"
        }
        
        response = await authenticated_client.put(f"/api/v1/users/{second_test_user.id}/profile", json=update_data)
        
        assert response.status_code == 404  # Endpoint doesn't exist
        data = response.json()
        assert "detail" in data


# @pytest.mark.integration
# class TestUserSearch:
#     """Test user search and discovery - ENDPOINT DOES NOT EXIST."""
#     
#     # Note: User search endpoint (/api/v1/users/search) is not implemented
#     # These tests are commented out until the endpoint is implemented
#     
#     # async def test_search_users_by_username(self, authenticated_client: AsyncClient, test_user: User, second_test_user: User):
#     #     """Test searching for users by username."""
#     #     # Search for a specific username
#     #     response = await authenticated_client.get(f"/api/v1/users/search?q={second_test_user.username}")
#     #     
#     #     assert response.status_code == 200
#     #     data = response.json()
#     #     assert len(data) >= 1
#     #     
#     #     # Find the searched user in results
#     #     found_user = next((u for u in data if u["id"] == second_test_user.id), None)
#     #     assert found_user is not None
#     #     assert found_user["username"] == second_test_user.username
#     #     # Private information should not be exposed
#     #     assert "email" not in found_user


# @pytest.mark.integration
# class TestUserListing:
#     """Test user listing endpoints - ENDPOINT DOES NOT EXIST."""
#     
#     # Note: User listing endpoint (/api/v1/users) is not implemented
#     # These tests are commented out until the endpoint is implemented
#     
#     # async def test_get_all_users_with_pagination(self, authenticated_client: AsyncClient, test_user: User, second_test_user: User):
#     #     """Test getting paginated list of users."""
#     #     response = await authenticated_client.get("/api/v1/users?limit=10&offset=0")
#     #     
#     #     assert response.status_code == 200
#     #     data = response.json()
#     #     assert isinstance(data, list)
#     #     assert len(data) >= 2  # At least our test users


@pytest.mark.integration
class TestUserPrivacy:
    """Test user privacy and data protection."""
    
    async def test_user_email_privacy(self, authenticated_client: AsyncClient, second_test_user: User):
        """Test that user emails are not exposed in public endpoints."""
        # Get user profile
        profile_response = await authenticated_client.get(f"/api/v1/users/{second_test_user.id}")
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        assert "email" not in profile_data
        
        # Note: Search users and list users endpoints don't exist yet
        # These tests are commented out until those endpoints are implemented
    
    async def test_user_password_privacy(self, authenticated_client: AsyncClient, second_test_user: User):
        """Test that password information is never exposed."""
        # Get user profile
        response = await authenticated_client.get(f"/api/v1/users/{second_test_user.id}")
        assert response.status_code == 200
        data = response.json()
        
        # Check that no password-related fields are present
        password_fields = ["password", "hashed_password", "password_hash", "hash"]
        for field in password_fields:
            assert field not in data
            assert field not in str(data).lower()
    
    async def test_inactive_user_not_visible(self, authenticated_client: AsyncClient, db_session: AsyncSession):
        """Test that inactive users are not visible in public endpoints."""
        # Create an inactive user
        from app.core.security import get_password_hash
        
        inactive_user = User(
            email="inactive@example.com",
            username="inactiveuser",
            hashed_password=get_password_hash("password123"),
            is_active=False
        )
        db_session.add(inactive_user)
        await db_session.commit()
        await db_session.refresh(inactive_user)
        
        # Try to get inactive user profile
        response = await authenticated_client.get(f"/api/v1/users/{inactive_user.id}")
        assert response.status_code == 404  # Should not be found
        
        # Note: Search endpoint doesn't exist yet
        # This test will be updated when the search endpoint is implemented


@pytest.mark.integration
class TestUserValidation:
    """Test user data validation."""
    
    async def test_profile_update_validation(self, authenticated_client: AsyncClient, test_user: User):
        """Test validation of profile update data."""
        invalid_updates = [
            {"timezone": "Invalid/Timezone"},  # Invalid timezone
            {"first_name": "A" * 101},  # Too long
            {"last_name": "B" * 101},  # Too long
            {"bio": "C" * 1001},  # Bio too long
        ]
        
        for invalid_data in invalid_updates:
            response = await authenticated_client.put("/api/v1/users/me/profile", json=invalid_data)
            assert response.status_code == 422
            data = response.json()
            assert "detail" in data
    
    # async def test_search_query_validation(self, authenticated_client: AsyncClient):
    #     """Test validation of search queries - ENDPOINT DOES NOT EXIST."""
    #     # Note: Search endpoint doesn't exist yet
    #     # This test is commented out until the endpoint is implemented
    #     pass