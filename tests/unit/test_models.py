"""
Unit tests for database models.

Tests cover:
- Model validation and constraints
- Relationships between models
- Model methods and properties
- Data integrity
"""

from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.location import Location
from app.models.trip import Trip, TripActivity, TripMember
from app.models.user import User, UserProfile


@pytest.mark.unit
class TestUserModel:
    """Test User model functionality."""

    async def test_create_user_success(self, db_session: AsyncSession):
        """Test creating a valid user."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword123",
            is_active=True,
        )

        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.created_at is not None
        assert user.updated_at is not None

    async def test_user_email_unique_constraint(self, db_session: AsyncSession):
        """Test that user emails must be unique."""
        # Create first user
        user1 = User(
            email="duplicate@example.com", username="user1", hashed_password="hash1"
        )
        db_session.add(user1)
        await db_session.commit()

        # Try to create second user with same email
        user2 = User(
            email="duplicate@example.com",  # Duplicate email
            username="user2",
            hashed_password="hash2",
        )
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_user_username_unique_constraint(self, db_session: AsyncSession):
        """Test that usernames must be unique."""
        # Create first user
        user1 = User(
            email="user1@example.com", username="duplicateuser", hashed_password="hash1"
        )
        db_session.add(user1)
        await db_session.commit()

        # Try to create second user with same username
        user2 = User(
            email="user2@example.com",
            username="duplicateuser",  # Duplicate username
            hashed_password="hash2",
        )
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_user_defaults(self, db_session: AsyncSession):
        """Test user model default values."""
        user = User(
            email="defaults@example.com",
            username="defaultuser",
            hashed_password="hashedpassword",
        )

        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Test default values
        assert user.is_active is True  # Default should be True
        assert user.created_at is not None
        assert user.updated_at is not None


@pytest.mark.unit
class TestUserProfileModel:
    """Test UserProfile model functionality."""

    async def test_create_user_profile_success(self, db_session: AsyncSession):
        """Test creating a valid user profile."""
        # Create user first
        user = User(
            email="profile@example.com",
            username="profileuser",
            hashed_password="hashedpassword",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create profile
        profile = UserProfile(
            user_id=user.id,
            first_name="John",
            last_name="Doe",
            bio="Test user bio",
            timezone="UTC",
        )

        db_session.add(profile)
        await db_session.commit()
        await db_session.refresh(profile)

        assert profile.id is not None
        assert profile.user_id == user.id
        assert profile.first_name == "John"
        assert profile.last_name == "Doe"
        assert profile.bio == "Test user bio"
        assert profile.timezone == "UTC"

    async def test_user_profile_relationship(self, db_session: AsyncSession):
        """Test relationship between User and UserProfile."""
        # Create user with profile
        user = User(
            email="relationship@example.com",
            username="relationshipuser",
            hashed_password="hashedpassword",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        profile = UserProfile(user_id=user.id, first_name="Jane", last_name="Smith")
        db_session.add(profile)
        await db_session.commit()
        await db_session.refresh(profile)

        # Test relationships
        await db_session.refresh(user, ["profile"])
        assert user.profile is not None
        assert user.profile.first_name == "Jane"
        assert user.profile.last_name == "Smith"

        await db_session.refresh(profile, ["user"])
        assert profile.user is not None
        assert profile.user.username == "relationshipuser"

    async def test_user_profile_foreign_key_constraint(self, db_session: AsyncSession):
        """Test foreign key constraint on user_id."""
        # Try to create profile with non-existent user_id
        profile = UserProfile(
            user_id=99999,
            first_name="Invalid",
            last_name="User",  # Non-existent user
        )
        db_session.add(profile)

        with pytest.raises(IntegrityError):
            await db_session.commit()


@pytest.mark.unit
class TestTripModel:
    """Test Trip model functionality."""

    async def test_create_trip_success(self, db_session: AsyncSession):
        """Test creating a valid trip."""
        # Create user first
        user = User(
            email="trip@example.com",
            username="tripuser",
            hashed_password="hashedpassword",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create trip
        trip = Trip(
            title="European Adventure",
            description="2-week trip through Europe",
            owner_id=user.id,
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 15),
            destination="Europe",
        )

        db_session.add(trip)
        await db_session.commit()
        await db_session.refresh(trip)

        assert trip.id is not None
        assert trip.title == "European Adventure"
        assert trip.description == "2-week trip through Europe"
        assert trip.owner_id == user.id
        assert trip.start_date == date(2024, 7, 1)
        assert trip.end_date == date(2024, 7, 15)
        assert trip.destination == "Europe"
        assert trip.created_at is not None
        assert trip.updated_at is not None

    async def test_trip_owner_relationship(self, db_session: AsyncSession):
        """Test relationship between Trip and User (owner)."""
        # Create user and trip
        user = User(
            email="owner@example.com",
            username="owneruser",
            hashed_password="hashedpassword",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        trip = Trip(
            title="Owner Test Trip",
            description="Testing owner relationship",
            owner_id=user.id,
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 15),
        )
        db_session.add(trip)
        await db_session.commit()
        await db_session.refresh(trip)

        # Test relationships
        await db_session.refresh(trip, ["owner"])
        assert trip.owner is not None
        assert trip.owner.username == "owneruser"

        await db_session.refresh(user, ["owned_trips"])
        assert len(user.owned_trips) == 1
        assert user.owned_trips[0].title == "Owner Test Trip"

    async def test_trip_foreign_key_constraint(self, db_session: AsyncSession):
        """Test foreign key constraint on owner_id."""
        # Try to create trip with non-existent owner_id
        trip = Trip(
            title="Invalid Trip",
            description="Trip with invalid owner",
            owner_id=99999,  # Non-existent user
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 15),
        )
        db_session.add(trip)

        with pytest.raises(IntegrityError):
            await db_session.commit()


@pytest.mark.unit
class TestTripMemberModel:
    """Test TripMember model functionality."""

    async def test_create_trip_member_success(self, db_session: AsyncSession):
        """Test creating a valid trip member."""
        # Create users and trip
        owner = User(
            email="owner@example.com", username="owner", hashed_password="hash"
        )
        member = User(
            email="member@example.com", username="member", hashed_password="hash"
        )
        db_session.add_all([owner, member])
        await db_session.commit()
        await db_session.refresh(owner)
        await db_session.refresh(member)

        trip = Trip(
            title="Member Test Trip",
            description="Testing members",
            owner_id=owner.id,
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 15),
        )
        db_session.add(trip)
        await db_session.commit()
        await db_session.refresh(trip)

        # Create trip member
        trip_member = TripMember(trip_id=trip.id, user_id=member.id, role="member")
        db_session.add(trip_member)
        await db_session.commit()
        await db_session.refresh(trip_member)

        assert trip_member.id is not None
        assert trip_member.trip_id == trip.id
        assert trip_member.user_id == member.id
        assert trip_member.role == "member"
        assert trip_member.joined_at is not None

    async def test_trip_member_relationships(self, db_session: AsyncSession):
        """Test relationships in TripMember model."""
        # Create test data
        owner = User(
            email="owner@example.com", username="owner", hashed_password="hash"
        )
        member = User(
            email="member@example.com", username="member", hashed_password="hash"
        )
        db_session.add_all([owner, member])
        await db_session.commit()
        await db_session.refresh(owner)
        await db_session.refresh(member)

        trip = Trip(
            title="Relationship Test Trip",
            owner_id=owner.id,
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 15),
        )
        db_session.add(trip)
        await db_session.commit()
        await db_session.refresh(trip)

        trip_member = TripMember(trip_id=trip.id, user_id=member.id, role="member")
        db_session.add(trip_member)
        await db_session.commit()
        await db_session.refresh(trip_member)

        # Test relationships
        await db_session.refresh(trip_member, ["trip", "user"])
        assert trip_member.trip.title == "Relationship Test Trip"
        assert trip_member.user.username == "member"

        await db_session.refresh(trip, ["members"])
        assert len(trip.members) == 1
        assert trip.members[0].user_id == member.id


@pytest.mark.unit
class TestTripActivityModel:
    """Test TripActivity model functionality."""

    async def test_create_trip_activity_success(self, db_session: AsyncSession):
        """Test creating a valid trip activity."""
        # Create user and trip
        user = User(
            email="activity@example.com",
            username="activityuser",
            hashed_password="hash",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        trip = Trip(
            title="Activity Test Trip",
            owner_id=user.id,
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 15),
        )
        db_session.add(trip)
        await db_session.commit()
        await db_session.refresh(trip)

        # Create activity
        activity = TripActivity(
            trip_id=trip.id,
            title="Visit Museum",
            description="Visit the local history museum",
            scheduled_date=date(2024, 7, 5),
            location="Downtown Museum",
        )
        db_session.add(activity)
        await db_session.commit()
        await db_session.refresh(activity)

        assert activity.id is not None
        assert activity.trip_id == trip.id
        assert activity.title == "Visit Museum"
        assert activity.description == "Visit the local history museum"
        assert activity.scheduled_date == date(2024, 7, 5)
        assert activity.location == "Downtown Museum"
        assert activity.created_at is not None

    async def test_trip_activity_relationship(self, db_session: AsyncSession):
        """Test relationship between TripActivity and Trip."""
        # Create test data
        user = User(email="rel@example.com", username="reluser", hashed_password="hash")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        trip = Trip(
            title="Activity Relationship Trip",
            owner_id=user.id,
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 15),
        )
        db_session.add(trip)
        await db_session.commit()
        await db_session.refresh(trip)

        activity = TripActivity(
            trip_id=trip.id,
            title="Test Activity",
            description="Testing relationships",
            scheduled_date=date(2024, 7, 5),
        )
        db_session.add(activity)
        await db_session.commit()
        await db_session.refresh(activity)

        # Test relationships
        await db_session.refresh(activity, ["trip"])
        assert activity.trip.title == "Activity Relationship Trip"

        await db_session.refresh(trip, ["activities"])
        assert len(trip.activities) == 1
        assert trip.activities[0].title == "Test Activity"


@pytest.mark.unit
class TestLocationModel:
    """Test Location model functionality."""

    async def test_create_location_success(self, db_session: AsyncSession):
        """Test creating a valid location."""
        location = Location(
            name="Paris, France",
            description="Capital city of France",
            latitude=48.8566,
            longitude=2.3522,
            country="France",
            city="Paris",
        )

        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)

        assert location.id is not None
        assert location.name == "Paris, France"
        assert location.description == "Capital city of France"
        assert location.latitude == 48.8566
        assert location.longitude == 2.3522
        assert location.country == "France"
        assert location.city == "Paris"
        assert location.created_at is not None

    async def test_location_coordinates_validation(self, db_session: AsyncSession):
        """Test that latitude and longitude are properly stored."""
        # Test with various coordinate values
        locations = [
            {"name": "North Pole", "latitude": 90.0, "longitude": 0.0},
            {"name": "South Pole", "latitude": -90.0, "longitude": 0.0},
            {"name": "Date Line", "latitude": 0.0, "longitude": 180.0},
            {"name": "Anti-Meridian", "latitude": 0.0, "longitude": -180.0},
        ]

        for loc_data in locations:
            location = Location(
                name=loc_data["name"],
                latitude=loc_data["latitude"],
                longitude=loc_data["longitude"],
            )
            db_session.add(location)

        await db_session.commit()

        # Verify all locations were created successfully
        from sqlalchemy import select

        result = await db_session.execute(select(Location))
        saved_locations = result.scalars().all()
        assert len(saved_locations) == 4
