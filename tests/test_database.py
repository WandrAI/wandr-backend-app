"""
Database testing utilities for Wandr Backend API.

This module provides utilities for:
- Database session management in tests
- Data setup and teardown helpers
- Database state verification
"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserProfile
from app.models.trip import Trip, TripMember, TripActivity
from app.models.location import Location


class DatabaseTestUtils:
    """Utility class for database testing operations."""
    
    @staticmethod
    async def count_records(db: AsyncSession, model_class) -> int:
        """Count records in a table."""
        result = await db.execute(text(f"SELECT COUNT(*) FROM {model_class.__tablename__}"))
        return result.scalar_one()
    
    @staticmethod
    async def clear_all_tables(db: AsyncSession):
        """Clear all data from all tables."""
        # Delete in order to respect foreign key constraints
        await db.execute(text("DELETE FROM trip_activities"))
        await db.execute(text("DELETE FROM trip_members"))
        await db.execute(text("DELETE FROM trips"))
        await db.execute(text("DELETE FROM locations"))
        await db.execute(text("DELETE FROM user_profiles"))
        await db.execute(text("DELETE FROM users"))
        await db.commit()
    
    @staticmethod
    async def verify_user_exists(db: AsyncSession, email: str) -> bool:
        """Verify that a user exists with the given email."""
        result = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email})
        return result.scalar_one_or_none() is not None
    
    @staticmethod
    async def verify_trip_exists(db: AsyncSession, title: str) -> bool:
        """Verify that a trip exists with the given title."""
        result = await db.execute(text("SELECT id FROM trips WHERE title = :title"), {"title": title})
        return result.scalar_one_or_none() is not None
    
    @staticmethod
    async def get_user_trip_count(db: AsyncSession, user_id: int) -> int:
        """Get the number of trips for a user."""
        result = await db.execute(
            text("SELECT COUNT(*) FROM trips WHERE owner_id = :user_id"), 
            {"user_id": user_id}
        )
        return result.scalar_one()
    
    @staticmethod
    async def verify_foreign_key_constraints(db: AsyncSession):
        """Verify that foreign key constraints are working."""
        # Try to insert a trip with a non-existent owner_id
        try:
            await db.execute(
                text("INSERT INTO trips (title, owner_id) VALUES ('Test', 99999)")
            )
            await db.commit()
            return False  # Should have failed
        except Exception:
            await db.rollback()
            return True  # Constraints are working


@pytest.mark.unit
class TestDatabaseConfiguration:
    """Test database configuration and utilities."""
    
    @pytest.mark.asyncio
    async def test_database_session_creates_tables(self, db_session: AsyncSession):
        """Test that database session creates all required tables."""
        # Verify that we can query each table (tables exist)
        user_count = await DatabaseTestUtils.count_records(db_session, User)
        trip_count = await DatabaseTestUtils.count_records(db_session, Trip)
        location_count = await DatabaseTestUtils.count_records(db_session, Location)
        
        assert user_count == 0
        assert trip_count == 0
        assert location_count == 0
    
    @pytest.mark.asyncio
    async def test_database_isolation_between_tests(self, db_session: AsyncSession):
        """Test that tests are isolated from each other."""
        # Add a user
        user = User(
            email="isolation@test.com",
            username="isolationtest",
            password_hash="hashedpassword"
        )
        db_session.add(user)
        await db_session.commit()
        
        # Verify user exists
        user_count = await DatabaseTestUtils.count_records(db_session, User)
        assert user_count == 1
        
        # The fixture should clean up after this test
    
    @pytest.mark.asyncio
    async def test_foreign_key_constraints(self, db_session: AsyncSession):
        """Test that foreign key constraints are enforced."""
        constraints_working = await DatabaseTestUtils.verify_foreign_key_constraints(db_session)
        assert constraints_working
    
    @pytest.mark.asyncio
    async def test_database_utils_clear_tables(self, db_session: AsyncSession):
        """Test the clear_all_tables utility function."""
        # Add some test data
        user = User(email="test@clear.com", username="cleartest", password_hash="hash")
        db_session.add(user)
        await db_session.commit()
        
        # Verify data exists
        user_count = await DatabaseTestUtils.count_records(db_session, User)
        assert user_count == 1
        
        # Clear all data
        await DatabaseTestUtils.clear_all_tables(db_session)
        
        # Verify data is gone
        user_count = await DatabaseTestUtils.count_records(db_session, User)
        assert user_count == 0