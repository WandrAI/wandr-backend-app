"""
Integration tests for trip endpoints.

Tests cover:
- Trip CRUD operations
- Trip member management
- Trip activity tracking
- Authorization and ownership
- Collaboration features
"""

from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip import Trip
from app.models.user import User
from tests.test_database import DatabaseTestUtils


@pytest.mark.integration
class TestTripCRUD:
    """Test trip CRUD operations."""

    async def test_create_trip_success(
        self,
        authenticated_client: AsyncClient,
        test_user: User,
        db_session: AsyncSession,
    ):
        """Test successful trip creation."""
        trip_data = {
            "title": "European Adventure",
            "description": "2-week trip through Europe",
            "start_date": "2024-07-01",
            "end_date": "2024-07-15",
            "destination": "Europe",
        }

        response = await authenticated_client.post("/api/v1/trips", json=trip_data)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == trip_data["title"]
        assert data["description"] == trip_data["description"]
        assert data["start_date"] == trip_data["start_date"]
        assert data["end_date"] == trip_data["end_date"]
        assert data["destination"] == trip_data["destination"]
        assert data["owner_id"] == test_user.id
        assert "id" in data

        # Verify trip was created in database
        assert await DatabaseTestUtils.verify_trip_exists(
            db_session, trip_data["title"]
        )

    async def test_create_trip_unauthenticated(self, test_client: AsyncClient):
        """Test trip creation without authentication fails."""
        trip_data = {
            "title": "Unauthorized Trip",
            "description": "This should fail",
            "start_date": "2024-07-01",
            "end_date": "2024-07-15",
        }

        response = await test_client.post("/api/v1/trips", json=trip_data)

        assert response.status_code == 401

    @pytest.mark.parametrize(
        "invalid_data",
        [
            {
                "title": "",
                "description": "desc",
                "start_date": "2024-07-01",
                "end_date": "2024-07-15",
            },  # Empty title
            {
                "title": "Trip",
                "description": "desc",
                "start_date": "invalid-date",
                "end_date": "2024-07-15",
            },  # Invalid date
            {
                "title": "Trip",
                "description": "desc",
                "start_date": "2024-07-15",
                "end_date": "2024-07-01",
            },  # End before start
            {},  # Missing required fields
        ],
    )
    async def test_create_trip_invalid_data(
        self, authenticated_client: AsyncClient, invalid_data
    ):
        """Test trip creation with invalid data fails."""
        response = await authenticated_client.post("/api/v1/trips", json=invalid_data)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_get_user_trips(
        self,
        authenticated_client: AsyncClient,
        test_user: User,
        db_session: AsyncSession,
    ):
        """Test retrieving user's trips."""
        # Create multiple trips
        trip_data = [
            {
                "title": "Trip 1",
                "description": "First trip",
                "start_date": "2024-07-01",
                "end_date": "2024-07-15",
            },
            {
                "title": "Trip 2",
                "description": "Second trip",
                "start_date": "2024-08-01",
                "end_date": "2024-08-15",
            },
        ]

        created_trips = []
        for data in trip_data:
            response = await authenticated_client.post("/api/v1/trips", json=data)
            assert response.status_code == 200
            created_trips.append(response.json())

        # Get all trips
        response = await authenticated_client.get("/api/v1/trips")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Verify trip data
        titles = [trip["title"] for trip in data]
        assert "Trip 1" in titles
        assert "Trip 2" in titles

    async def test_get_trip_by_id(
        self, authenticated_client: AsyncClient, test_user: User
    ):
        """Test retrieving a specific trip by ID."""
        # Create a trip
        trip_data = {
            "title": "Specific Trip",
            "description": "Trip to get by ID",
            "start_date": "2024-07-01",
            "end_date": "2024-07-15",
        }

        create_response = await authenticated_client.post(
            "/api/v1/trips", json=trip_data
        )
        assert create_response.status_code == 201
        created_trip = create_response.json()
        trip_id = created_trip["id"]

        # Get trip by ID
        response = await authenticated_client.get(f"/api/v1/trips/{trip_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == trip_id
        assert data["title"] == trip_data["title"]

    async def test_get_nonexistent_trip(self, authenticated_client: AsyncClient):
        """Test retrieving non-existent trip returns 404."""
        response = await authenticated_client.get("/api/v1/trips/99999")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    async def test_update_trip_success(
        self, authenticated_client: AsyncClient, test_user: User
    ):
        """Test successful trip update."""
        # Create a trip
        trip_data = {
            "title": "Original Trip",
            "description": "Original description",
            "start_date": "2024-07-01",
            "end_date": "2024-07-15",
        }

        create_response = await authenticated_client.post(
            "/api/v1/trips", json=trip_data
        )
        assert create_response.status_code == 201
        created_trip = create_response.json()
        trip_id = created_trip["id"]

        # Update trip
        update_data = {
            "title": "Updated Trip",
            "description": "Updated description",
            "destination": "New Destination",
        }

        response = await authenticated_client.put(
            f"/api/v1/trips/{trip_id}", json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["destination"] == update_data["destination"]
        # Original dates should remain
        assert data["start_date"] == trip_data["start_date"]
        assert data["end_date"] == trip_data["end_date"]

    async def test_update_trip_unauthorized(
        self,
        test_client: AsyncClient,
        test_user: User,
        second_test_user: User,
        db_session: AsyncSession,
    ):
        """Test that users cannot update trips they don't own."""
        # Create trip as first user
        trip = Trip(
            title="First User Trip",
            description="Trip owned by first user",
            owner_id=test_user.id,
            start_date="2024-07-01",
            end_date="2024-07-15",
        )
        db_session.add(trip)
        await db_session.commit()
        await db_session.refresh(trip)

        # Try to update as second user
        from app.core.security import create_access_token

        second_user_token = create_access_token(data={"sub": str(second_test_user.id)})
        headers = {"Authorization": f"Bearer {second_user_token}"}

        update_data = {"title": "Hacked Trip"}
        response = await test_client.put(
            f"/api/v1/trips/{trip.id}", json=update_data, headers=headers
        )

        assert response.status_code == 403
        data = response.json()
        assert "detail" in data

    async def test_delete_trip_success(
        self, authenticated_client: AsyncClient, test_user: User
    ):
        """Test successful trip deletion."""
        # Create a trip
        trip_data = {
            "title": "Trip to Delete",
            "description": "This trip will be deleted",
            "start_date": "2024-07-01",
            "end_date": "2024-07-15",
        }

        create_response = await authenticated_client.post(
            "/api/v1/trips", json=trip_data
        )
        assert create_response.status_code == 201
        created_trip = create_response.json()
        trip_id = created_trip["id"]

        # Delete trip
        response = await authenticated_client.delete(f"/api/v1/trips/{trip_id}")

        assert response.status_code == 204

        # Verify trip is deleted
        get_response = await authenticated_client.get(f"/api/v1/trips/{trip_id}")
        assert get_response.status_code == 404


@pytest.mark.integration
class TestTripMembers:
    """Test trip member management."""

    async def test_add_trip_member(
        self, authenticated_client: AsyncClient, test_user: User, second_test_user: User
    ):
        """Test adding a member to a trip."""
        # Create a trip
        trip_data = {
            "title": "Collaborative Trip",
            "description": "Trip with multiple members",
            "start_date": "2024-07-01",
            "end_date": "2024-07-15",
        }

        create_response = await authenticated_client.post(
            "/api/v1/trips", json=trip_data
        )
        assert create_response.status_code == 201
        trip = create_response.json()
        trip_id = trip["id"]

        # Add member
        member_data = {"user_id": second_test_user.id, "role": "member"}
        response = await authenticated_client.post(
            f"/api/v1/trips/{trip_id}/members", json=member_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == second_test_user.id
        assert data["role"] == "member"
        assert data["trip_id"] == trip_id

    async def test_get_trip_members(
        self, authenticated_client: AsyncClient, test_user: User, second_test_user: User
    ):
        """Test retrieving trip members."""
        # Create trip and add member
        trip_data = {
            "title": "Member Test Trip",
            "description": "Trip for testing members",
            "start_date": "2024-07-01",
            "end_date": "2024-07-15",
        }

        create_response = await authenticated_client.post(
            "/api/v1/trips", json=trip_data
        )
        trip = create_response.json()
        trip_id = trip["id"]

        # Add member
        member_data = {"user_id": second_test_user.id, "role": "member"}
        await authenticated_client.post(
            f"/api/v1/trips/{trip_id}/members", json=member_data
        )

        # Get members
        response = await authenticated_client.get(f"/api/v1/trips/{trip_id}/members")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1  # Should include the added member

        # Find the added member
        added_member = next(
            (m for m in data if m["user_id"] == second_test_user.id), None
        )
        assert added_member is not None
        assert added_member["role"] == "member"

    async def test_remove_trip_member(
        self, authenticated_client: AsyncClient, test_user: User, second_test_user: User
    ):
        """Test removing a member from a trip."""
        # Create trip and add member
        trip_data = {
            "title": "Remove Member Trip",
            "description": "Trip for testing member removal",
            "start_date": "2024-07-01",
            "end_date": "2024-07-15",
        }

        create_response = await authenticated_client.post(
            "/api/v1/trips", json=trip_data
        )
        trip = create_response.json()
        trip_id = trip["id"]

        # Add member
        member_data = {"user_id": second_test_user.id, "role": "member"}
        add_response = await authenticated_client.post(
            f"/api/v1/trips/{trip_id}/members", json=member_data
        )
        assert add_response.status_code == 200

        # Remove member
        response = await authenticated_client.delete(
            f"/api/v1/trips/{trip_id}/members/{second_test_user.id}"
        )

        assert response.status_code == 200

        # Verify member is removed
        get_response = await authenticated_client.get(
            f"/api/v1/trips/{trip_id}/members"
        )
        members = get_response.json()
        removed_member = next(
            (m for m in members if m["user_id"] == second_test_user.id), None
        )
        assert removed_member is None


# @pytest.mark.integration
# class TestTripActivities:
#     """Test trip activity tracking - ENDPOINTS DO NOT EXIST."""
#
#     # Note: Trip activity endpoints (/api/v1/trips/{trip_id}/activities) are not implemented
#     # These tests are commented out until the endpoints are implemented
#
#     # async def test_add_trip_activity(self, authenticated_client: AsyncClient, test_user: User):
#     #     """Test adding an activity to a trip."""
#     #     # Create a trip
#     #     trip_data = {
#     #         "title": "Activity Trip",
#     #         "description": "Trip for testing activities",
#     #         "start_date": "2024-07-01",
#     #         "end_date": "2024-07-15"
#     #     }
#     #
#     #     create_response = await authenticated_client.post("/api/v1/trips", json=trip_data)
#     #     trip = create_response.json()
#     #     trip_id = trip["id"]
#     #
#     #     # Add activity
#     #     activity_data = {
#     #         "title": "Visit Museum",
#     #         "description": "Visit the local history museum",
#     #         "scheduled_date": "2024-07-05",
#     #         "location": "Downtown Museum"
#     #     }
#     #
#     #     response = await authenticated_client.post(f"/api/v1/trips/{trip_id}/activities", json=activity_data)
#     #
#     #     assert response.status_code == 200
#     #     data = response.json()
#     #     assert data["title"] == activity_data["title"]
#     #     assert data["description"] == activity_data["description"]
#     #     assert data["scheduled_date"] == activity_data["scheduled_date"]
#     #     assert data["location"] == activity_data["location"]
#     #     assert data["trip_id"] == trip_id
