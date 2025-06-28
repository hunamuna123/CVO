"""
User repository implementation.

This module provides user-specific data access operations,
extending the base repository with user-related functionality.
"""

import abc
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, UserRole
from app.repositories.base import BaseRepository, FilterSpec, SortSpec, QueryResult


class IUserRepository(abc.ABC):
    """User repository interface."""
    
    @abc.abstractmethod
    async def get_by_phone(self, phone: str) -> Optional[User]:
        """Get user by phone number."""
        pass
    
    @abc.abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        pass
    
    @abc.abstractmethod
    async def get_verified_users(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """Get all verified users."""
        pass
    
    @abc.abstractmethod
    async def get_users_by_role(self, role: UserRole) -> List[User]:
        """Get users by specific role."""
        pass
    
    @abc.abstractmethod
    async def search_users(
        self, 
        query: str, 
        filters: Optional[List[FilterSpec]] = None
    ) -> List[User]:
        """Search users by name or phone."""
        pass
    
    @abc.abstractmethod
    async def activate_user(self, user_id: UUID) -> bool:
        """Activate user account."""
        pass
    
    @abc.abstractmethod
    async def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate user account."""
        pass
    
    @abc.abstractmethod
    async def verify_user(self, user_id: UUID) -> bool:
        """Mark user as verified."""
        pass
    
    @abc.abstractmethod
    async def update_user_role(self, user_id: UUID, role: UserRole) -> Optional[User]:
        """Update user role."""
        pass


class UserRepository(BaseRepository[User], IUserRepository):
    """User repository implementation."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)
    
    async def get_by_phone(self, phone: str) -> Optional[User]:
        """Get user by phone number."""
        return await self.get_by_field("phone", phone)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return await self.get_by_field("email", email)
    
    async def get_verified_users(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """Get all verified users."""
        filters = [FilterSpec("is_verified", "eq", True)]
        return await self.find_many(
            filters=filters,
            sorts=[SortSpec("created_at", "desc")],
            limit=limit
        )
    
    async def get_users_by_role(self, role: UserRole) -> List[User]:
        """Get users by specific role."""
        return await self.get_many_by_field("role", role)
    
    async def search_users(
        self, 
        query: str, 
        filters: Optional[List[FilterSpec]] = None
    ) -> List[User]:
        """Search users by name or phone."""
        search_query = select(User).where(
            User.first_name.ilike(f"%{query}%") |
            User.last_name.ilike(f"%{query}%") |
            User.phone.ilike(f"%{query}%")
        )
        
        # Apply additional filters if provided
        if filters:
            for filter_spec in filters:
                search_query = filter_spec.apply(search_query, User)
        
        # Only return active users in search
        search_query = search_query.where(User.is_active == True)
        
        result = await self.db.execute(search_query)
        return list(result.scalars().all())
    
    async def activate_user(self, user_id: UUID) -> bool:
        """Activate user account."""
        updated = await self.update_by_id(user_id, {"is_active": True})
        return updated is not None
    
    async def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate user account."""
        updated = await self.update_by_id(user_id, {"is_active": False})
        return updated is not None
    
    async def verify_user(self, user_id: UUID) -> bool:
        """Mark user as verified."""
        updated = await self.update_by_id(user_id, {"is_verified": True})
        return updated is not None
    
    async def update_user_role(self, user_id: UUID, role: UserRole) -> Optional[User]:
        """Update user role."""
        return await self.update_by_id(user_id, {"role": role})
    
    async def get_user_with_profile(self, user_id: UUID) -> Optional[User]:
        """Get user with related profile data."""
        query = select(User).options(
            selectinload(User.developer_profile),
            selectinload(User.favorites),
        ).where(User.id == user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_statistics(self) -> dict:
        """Get user statistics."""
        from sqlalchemy import func
        
        # Total users
        total_query = select(func.count(User.id))
        total_result = await self.db.execute(total_query)
        total_users = total_result.scalar()
        
        # Verified users
        verified_query = select(func.count(User.id)).where(User.is_verified == True)
        verified_result = await self.db.execute(verified_query)
        verified_users = verified_result.scalar()
        
        # Active users
        active_query = select(func.count(User.id)).where(User.is_active == True)
        active_result = await self.db.execute(active_query)
        active_users = active_result.scalar()
        
        # Users by role
        role_query = select(User.role, func.count(User.id)).group_by(User.role)
        role_result = await self.db.execute(role_query)
        users_by_role = {role.value: count for role, count in role_result.all()}
        
        return {
            "total_users": total_users,
            "verified_users": verified_users,
            "active_users": active_users,
            "users_by_role": users_by_role
        }
    
    async def get_recently_registered(
        self, 
        days: int = 7, 
        limit: int = 50
    ) -> List[User]:
        """Get recently registered users."""
        from datetime import datetime, timedelta
        
        since_date = datetime.utcnow() - timedelta(days=days)
        filters = [
            FilterSpec("created_at", "gte", since_date),
            FilterSpec("is_active", "eq", True)
        ]
        
        return await self.find_many(
            filters=filters,
            sorts=[SortSpec("created_at", "desc")],
            limit=limit
        )
    
    async def find_users_with_incomplete_profiles(self) -> List[User]:
        """Find users with incomplete profiles."""
        query = select(User).where(
            (User.email.is_(None)) |
            (User.avatar_url.is_(None))
        ).where(User.is_active == True)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def check_phone_availability(self, phone: str) -> bool:
        """Check if phone number is available."""
        return not await self.exists_by_field("phone", phone)
    
    async def check_email_availability(self, email: str) -> bool:
        """Check if email is available."""
        return not await self.exists_by_field("email", email)
