"""
Developer repository implementation.

This module provides developer-specific data access operations,
including verification and rating management.
"""

import abc
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.models.developer import Developer, VerificationStatus
from app.repositories.base import BaseRepository, FilterSpec, SortSpec, QueryResult


class IDeveloperRepository(abc.ABC):
    """Developer repository interface."""
    
    @abc.abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Optional[Developer]:
        """Get developer by user ID."""
        pass
    
    @abc.abstractmethod
    async def get_by_inn(self, inn: str) -> Optional[Developer]:
        """Get developer by INN."""
        pass
    
    @abc.abstractmethod
    async def get_verified_developers(self) -> List[Developer]:
        """Get all verified developers."""
        pass
    
    @abc.abstractmethod
    async def search_developers(self, query: str) -> List[Developer]:
        """Search developers by name or company."""
        pass
    
    @abc.abstractmethod
    async def update_rating(self, developer_id: UUID, new_rating: float) -> bool:
        """Update developer rating."""
        pass
    
    @abc.abstractmethod
    async def update_verification_status(
        self, 
        developer_id: UUID, 
        status: VerificationStatus
    ) -> bool:
        """Update developer verification status."""
        pass


class DeveloperRepository(BaseRepository[Developer], IDeveloperRepository):
    """Developer repository implementation."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Developer)
    
    async def get_by_user_id(self, user_id: UUID) -> Optional[Developer]:
        """Get developer by user ID."""
        return await self.get_by_field("user_id", user_id)
    
    async def get_by_inn(self, inn: str) -> Optional[Developer]:
        """Get developer by INN."""
        return await self.get_by_field("inn", inn)
    
    async def get_verified_developers(self) -> List[Developer]:
        """Get all verified developers."""
        filters = [
            FilterSpec("is_verified", "eq", True),
            FilterSpec("verification_status", "eq", VerificationStatus.APPROVED)
        ]
        
        return await self.find_many(
            filters=filters,
            sorts=[SortSpec("rating", "desc")]
        )
    
    async def search_developers(self, query: str) -> List[Developer]:
        """Search developers by name or company."""
        search_query = select(Developer).where(
            Developer.company_name.ilike(f"%{query}%") |
            Developer.legal_name.ilike(f"%{query}%")
        ).where(Developer.is_verified == True)
        
        result = await self.db.execute(search_query)
        return list(result.scalars().all())
    
    async def update_rating(self, developer_id: UUID, new_rating: float) -> bool:
        """Update developer rating."""
        updated = await self.update_by_id(developer_id, {"rating": new_rating})
        return updated is not None
    
    async def update_verification_status(
        self, 
        developer_id: UUID, 
        status: VerificationStatus
    ) -> bool:
        """Update developer verification status."""
        is_verified = status == VerificationStatus.APPROVED
        update_data = {
            "verification_status": status,
            "is_verified": is_verified
        }
        
        updated = await self.update_by_id(developer_id, update_data)
        return updated is not None
    
    async def get_developer_with_properties(self, developer_id: UUID) -> Optional[Developer]:
        """Get developer with all properties."""
        query = select(Developer).options(
            selectinload(Developer.properties),
            joinedload(Developer.user)
        ).where(Developer.id == developer_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_top_developers(self, limit: int = 10) -> List[Developer]:
        """Get top-rated developers."""
        filters = [FilterSpec("is_verified", "eq", True)]
        sorts = [SortSpec("rating", "desc")]
        
        return await self.find_many(
            filters=filters,
            sorts=sorts,
            limit=limit
        )
    
    async def get_developers_statistics(self) -> Dict[str, Any]:
        """Get developer statistics."""
        # Total developers
        total_query = select(func.count(Developer.id))
        total_result = await self.db.execute(total_query)
        total_developers = total_result.scalar()
        
        # Verified developers
        verified_query = select(func.count(Developer.id)).where(Developer.is_verified == True)
        verified_result = await self.db.execute(verified_query)
        verified_developers = verified_result.scalar()
        
        # Developers by verification status
        status_query = select(
            Developer.verification_status, 
            func.count(Developer.id)
        ).group_by(Developer.verification_status)
        status_result = await self.db.execute(status_query)
        developers_by_status = {status.value: count for status, count in status_result.all()}
        
        # Average rating
        avg_rating_query = select(func.avg(Developer.rating)).where(Developer.is_verified == True)
        avg_rating_result = await self.db.execute(avg_rating_query)
        average_rating = avg_rating_result.scalar() or 0
        
        return {
            "total_developers": total_developers,
            "verified_developers": verified_developers,
            "developers_by_status": developers_by_status,
            "average_rating": float(average_rating)
        }
    
    async def check_inn_availability(self, inn: str) -> bool:
        """Check if INN is available."""
        return not await self.exists_by_field("inn", inn)
    
    async def get_pending_verification(self) -> List[Developer]:
        """Get developers pending verification."""
        filters = [FilterSpec("verification_status", "eq", VerificationStatus.PENDING)]
        sorts = [SortSpec("created_at", "asc")]  # Oldest first
        
        return await self.find_many(filters=filters, sorts=sorts)
