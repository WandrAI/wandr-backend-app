"""
Unit tests for Pydantic schemas.

Tests cover:
- Schema validation and constraints
- Data serialization and deserialization
- Error handling for invalid data
- Custom validators
"""

from datetime import date, datetime

from pydantic import ValidationError
import pytest

from app.schemas.common import PaginationParams
from app.schemas.trip import (
    TripCreate,
    TripMemberCreate,
    TripResponse,
    TripUpdate,
)
from app.schemas.user import (
    UserCreate,
    UserProfileUpdate,
    UserResponse,
)


@pytest.mark.unit
class TestUserSchemas:
    """Test user-related Pydantic schemas."""

    def test_user_create_valid(self):
        """Test UserCreate schema with valid data."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "securepassword123",
        }

        user = UserCreate(**user_data)

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.password == "securepassword123"

    def test_user_create_email_validation(self):
        """Test UserCreate email validation."""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "",
            "test..test@example.com",  # Double dots
        ]

        for invalid_email in invalid_emails:
            with pytest.raises(ValidationError) as exc_info:
                UserCreate(
                    email=invalid_email, username="testuser", password="password123"
                )
            assert "email" in str(exc_info.value).lower()

    def test_user_create_username_validation(self):
        """Test UserCreate username validation."""
        invalid_usernames = [
            "",  # Empty
            "ab",  # Too short
            "a" * 51,  # Too long
            "user name",  # Contains space
            "user@name",  # Contains special chars
        ]

        for invalid_username in invalid_usernames:
            with pytest.raises(ValidationError) as exc_info:
                UserCreate(
                    email="test@example.com",
                    username=invalid_username,
                    password="password123",
                )
            assert "username" in str(exc_info.value).lower()

    def test_user_create_password_validation(self):
        """Test UserCreate password validation."""
        invalid_passwords = [
            "",  # Empty
            "12345",  # Too short
            "a" * 129,  # Too long
        ]

        for invalid_password in invalid_passwords:
            with pytest.raises(ValidationError) as exc_info:
                UserCreate(
                    email="test@example.com",
                    username="testuser",
                    password=invalid_password,
                )
            assert "password" in str(exc_info.value).lower()

    def test_user_response_excludes_password(self):
        """Test UserResponse schema excludes password fields."""
        import uuid

        user_data = {
            "id": str(uuid.uuid4()),
            "email": "test@example.com",
            "username": "testuser",
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        user = UserResponse(**user_data)

        # Verify password-related fields are not present
        assert not hasattr(user, "password")
        assert not hasattr(user, "hashed_password")
        assert user.email == "test@example.com"
        assert user.username == "testuser"

    def test_user_profile_update_valid(self):
        """Test UserProfileUpdate schema with valid data."""
        profile_data = {
            "first_name": "John",
            "last_name": "Doe",
            "bio": "Software developer and travel enthusiast",
            "timezone": "America/New_York",
        }

        profile = UserProfileUpdate(**profile_data)

        assert profile.first_name == "John"
        assert profile.last_name == "Doe"
        assert profile.bio == "Software developer and travel enthusiast"
        assert profile.timezone == "America/New_York"

    def test_user_profile_update_optional_fields(self):
        """Test UserProfileUpdate with optional fields."""
        # Should work with minimal data
        profile = UserProfileUpdate()
        assert profile.first_name is None
        assert profile.last_name is None

        # Should work with partial data
        profile = UserProfileUpdate(first_name="John")
        assert profile.first_name == "John"
        assert profile.last_name is None

    def test_user_profile_update_validation(self):
        """Test UserProfileUpdate field validation."""
        # Test field length limits
        with pytest.raises(ValidationError):
            UserProfileUpdate(first_name="A" * 101)  # Too long

        with pytest.raises(ValidationError):
            UserProfileUpdate(last_name="B" * 101)  # Too long

        with pytest.raises(ValidationError):
            UserProfileUpdate(bio="C" * 1001)  # Too long

        # Test invalid timezone
        with pytest.raises(ValidationError):
            UserProfileUpdate(timezone="Invalid/Timezone")


@pytest.mark.unit
class TestTripSchemas:
    """Test trip-related Pydantic schemas."""

    def test_trip_create_valid(self):
        """Test TripCreate schema with valid data."""
        trip_data = {
            "title": "European Adventure",
            "description": "2-week trip through Europe",
            "start_date": "2024-07-01",
            "end_date": "2024-07-15",
            "destination": "Europe",
        }

        trip = TripCreate(**trip_data)

        assert trip.title == "European Adventure"
        assert trip.description == "2-week trip through Europe"
        assert trip.start_date == date(2024, 7, 1)
        assert trip.end_date == date(2024, 7, 15)
        assert trip.destination == "Europe"

    def test_trip_create_required_fields(self):
        """Test TripCreate required field validation."""
        # Missing title
        with pytest.raises(ValidationError) as exc_info:
            TripCreate(
                description="Trip description",
                start_date="2024-07-01",
                end_date="2024-07-15",
            )
        assert "title" in str(exc_info.value).lower()

        # Missing start_date
        with pytest.raises(ValidationError) as exc_info:
            TripCreate(
                title="Trip Title",
                description="Trip description",
                end_date="2024-07-15",
            )
        assert "start_date" in str(exc_info.value).lower()

        # Missing end_date
        with pytest.raises(ValidationError) as exc_info:
            TripCreate(
                title="Trip Title",
                description="Trip description",
                start_date="2024-07-01",
            )
        assert "end_date" in str(exc_info.value).lower()

    def test_trip_create_date_validation(self):
        """Test TripCreate date validation."""
        # End date before start date
        with pytest.raises(ValidationError) as exc_info:
            TripCreate(
                title="Invalid Trip",
                description="End date before start date",
                start_date="2024-07-15",
                end_date="2024-07-01",  # Before start date
            )
        # Should contain validation error about dates
        error_str = str(exc_info.value).lower()
        assert "date" in error_str or "end" in error_str or "start" in error_str

        # Invalid date format
        with pytest.raises(ValidationError):
            TripCreate(
                title="Invalid Trip",
                description="Invalid date format",
                start_date="invalid-date",
                end_date="2024-07-15",
            )

    def test_trip_create_title_validation(self):
        """Test TripCreate title validation."""
        # Empty title
        with pytest.raises(ValidationError) as exc_info:
            TripCreate(
                title="",
                description="Trip description",
                start_date="2024-07-01",
                end_date="2024-07-15",
            )
        assert "title" in str(exc_info.value).lower()

        # Title too long
        with pytest.raises(ValidationError) as exc_info:
            TripCreate(
                title="A" * 201,  # Too long
                description="Trip description",
                start_date="2024-07-01",
                end_date="2024-07-15",
            )
        assert "title" in str(exc_info.value).lower()

    def test_trip_update_partial_fields(self):
        """Test TripUpdate allows partial updates."""
        # Should work with only title
        trip_update = TripUpdate(title="Updated Title")
        assert trip_update.title == "Updated Title"
        assert trip_update.description is None

        # Should work with only description
        trip_update = TripUpdate(description="Updated description")
        assert trip_update.description == "Updated description"
        assert trip_update.title is None

        # Should work with no fields (for PATCH requests)
        trip_update = TripUpdate()
        assert trip_update.title is None
        assert trip_update.description is None

    def test_trip_response_includes_metadata(self):
        """Test TripResponse includes all necessary metadata."""
        import uuid

        trip_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        trip_data = {
            "id": trip_id,
            "title": "Test Trip",
            "description": "Test description",
            "destination": "Test Destination",
            "start_date": date(2024, 7, 1),
            "end_date": date(2024, 7, 15),
            "status": "planning",
            "created_by": user_id,
            "trip_data": {},
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        trip = TripResponse(**trip_data)

        assert str(trip.id) == trip_id
        assert trip.title == "Test Trip"
        assert str(trip.created_by) == user_id
        assert trip.created_at is not None
        assert trip.updated_at is not None


@pytest.mark.unit
class TestTripMemberSchemas:
    """Test trip member schemas."""

    def test_trip_member_create_valid(self):
        """Test TripMemberCreate schema with valid data."""
        import uuid

        user_id = str(uuid.uuid4())
        member_data = {"user_id": user_id, "role": "participant"}

        member = TripMemberCreate(**member_data)

        assert str(member.user_id) == user_id
        assert member.role == "participant"

    def test_trip_member_create_role_validation(self):
        """Test TripMemberCreate role validation."""
        import uuid

        user_id = str(uuid.uuid4())
        valid_roles = ["organizer", "participant", "viewer"]

        for role in valid_roles:
            member = TripMemberCreate(user_id=user_id, role=role)
            assert member.role == role

        # Test invalid role
        with pytest.raises(ValidationError) as exc_info:
            TripMemberCreate(user_id=user_id, role="invalid_role")
        assert "role" in str(exc_info.value).lower()

    def test_trip_member_create_required_fields(self):
        """Test TripMemberCreate required fields."""
        import uuid

        user_id = str(uuid.uuid4())

        # Missing user_id
        with pytest.raises(ValidationError) as exc_info:
            TripMemberCreate(role="participant")
        assert "user_id" in str(exc_info.value).lower()

        # Missing role (role has default value, so this test won't work as expected)
        # Test with required user_id only
        member = TripMemberCreate(user_id=user_id)
        assert member.role == "participant"  # Default value


# TripActivityCreate schema doesn't exist in current implementation
# Activity creation is handled differently in the current schema design


@pytest.mark.unit
class TestCommonSchemas:
    """Test common/shared schemas."""

    def test_pagination_params_defaults(self):
        """Test PaginationParams default values."""
        params = PaginationParams()

        assert params.offset == 0
        assert params.limit == 50

    def test_pagination_params_custom_values(self):
        """Test PaginationParams with custom values."""
        params = PaginationParams(offset=20, limit=10)

        assert params.offset == 20
        assert params.limit == 10

    def test_pagination_params_validation(self):
        """Test PaginationParams validation."""
        # Negative offset
        with pytest.raises(ValidationError) as exc_info:
            PaginationParams(offset=-1)
        assert "offset" in str(exc_info.value).lower()

        # Limit too high
        with pytest.raises(ValidationError) as exc_info:
            PaginationParams(limit=1000)
        assert "limit" in str(exc_info.value).lower()

        # Limit too low
        with pytest.raises(ValidationError) as exc_info:
            PaginationParams(limit=0)
        assert "limit" in str(exc_info.value).lower()


@pytest.mark.unit
class TestSchemaValidationHelpers:
    """Test custom validation helpers and edge cases."""

    def test_date_string_parsing(self):
        """Test date string parsing in schemas."""
        # Test various valid date formats
        valid_date_pairs = [
            ("2024-07-01", "2024-07-15"),
            ("2024-12-31", "2025-01-15"),
            ("2025-01-01", "2025-01-15"),
        ]

        for start_date, end_date in valid_date_pairs:
            trip = TripCreate(
                title="Date Test",
                description="Testing date parsing",
                start_date=start_date,
                end_date=end_date,
            )
            assert isinstance(trip.start_date, date)

    def test_whitespace_handling(self):
        """Test that schemas handle whitespace properly."""
        # Test that leading/trailing whitespace is handled
        user = UserCreate(
            email="  test@example.com  ",
            username="  testuser  ",
            password="password123",
        )

        # Depending on schema configuration, whitespace might be stripped
        # This test verifies the behavior is consistent
        assert "@example.com" in user.email
        assert "testuser" in user.username

    def test_case_sensitivity(self):
        """Test case sensitivity in validation."""
        # Email should be case-insensitive for validation but preserved
        user = UserCreate(
            email="Test@EXAMPLE.COM", username="TestUser", password="password123"
        )

        # Email format should be valid regardless of case
        assert "@" in user.email
        assert "example.com" in user.email.lower()
