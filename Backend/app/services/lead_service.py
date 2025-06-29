"""
Lead service for managing property inquiries and contacts.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException, BadRequestException
from app.models.lead import Lead
from app.models.property import Property
from app.models.user import User
from app.schemas.lead import (
    LeadCreateRequest,
    LeadListResponse,
    LeadResponse,
    LeadSearchParams,
    LeadStatusUpdateRequest,
    PropertyInfo,
    UserInfo,
)
import structlog

logger = structlog.get_logger(__name__)


class LeadService:
    """Service for managing leads and inquiries."""

    async def create_lead(
        self,
        db: AsyncSession,
        lead_data: LeadCreateRequest,
        user_id: Optional[str] = None,
    ) -> LeadResponse:
        """
        Create a new lead inquiry.
        
        Args:
            db: Database session
            lead_data: Lead data
            user_id: User UUID (optional for anonymous leads)
            
        Returns:
            Created lead
            
        Raises:
            NotFoundException: If property doesn't exist
        """
        # Verify property exists and is active
        property_query = (
            select(Property)
            .options(selectinload(Property.developer))
            .where(
                and_(
                    Property.id == UUID(lead_data.property_id),
                    Property.status == "ACTIVE"
                )
            )
        )
        property_result = await db.execute(property_query)
        property_obj = property_result.scalar_one_or_none()

        if not property_obj:
            raise NotFoundException(
                message="Объект недвижимости не найден или неактивен",
                details={"property_id": lead_data.property_id}
            )

        # Create lead
        lead = Lead(
            property_id=UUID(lead_data.property_id),
            user_id=UUID(user_id) if user_id else None,
            name=lead_data.name,
            phone=lead_data.phone,
            email=lead_data.email,
            message=lead_data.message,
            lead_type=lead_data.lead_type,
            status="NEW",
        )

        db.add(lead)
        await db.commit()
        await db.refresh(lead)

        logger.info(
            "Created lead",
            lead_id=str(lead.id),
            property_id=lead_data.property_id,
            user_id=user_id,
            lead_type=lead_data.lead_type,
        )

        # Return created lead with full details
        return await self.get_lead_by_id(db, str(lead.id), str(property_obj.developer_id))

    async def get_developer_leads(
        self,
        db: AsyncSession,
        developer_id: str,
        search_params: LeadSearchParams,
    ) -> List[LeadListResponse]:
        """
        Get leads for developer properties with filtering.
        
        Args:
            db: Database session
            developer_id: Developer UUID
            search_params: Search parameters
            
        Returns:
            List of leads for developer's properties
        """
        offset = (search_params.page - 1) * search_params.limit

        # Build base query for leads on developer's properties
        query = (
            select(Lead)
            .join(Property, Lead.property_id == Property.id)
            .options(
                selectinload(Lead.property_obj),
                selectinload(Lead.user),
            )
            .where(Property.developer_id == UUID(developer_id))
        )

        # Apply filters
        if search_params.property_id:
            query = query.where(Lead.property_id == UUID(search_params.property_id))
        
        if search_params.lead_type:
            query = query.where(Lead.lead_type == search_params.lead_type)
        
        if search_params.status:
            query = query.where(Lead.status == search_params.status)
        
        if search_params.date_from:
            try:
                date_from = datetime.strptime(search_params.date_from, "%Y-%m-%d")
                query = query.where(Lead.created_at >= date_from)
            except ValueError:
                pass  # Invalid date format, ignore filter
        
        if search_params.date_to:
            try:
                date_to = datetime.strptime(search_params.date_to, "%Y-%m-%d") + timedelta(days=1)
                query = query.where(Lead.created_at < date_to)
            except ValueError:
                pass  # Invalid date format, ignore filter

        # Apply sorting
        if search_params.sort == "created_desc":
            query = query.order_by(Lead.created_at.desc())
        elif search_params.sort == "created_asc":
            query = query.order_by(Lead.created_at.asc())
        elif search_params.sort == "status_asc":
            query = query.order_by(Lead.status.asc())
        elif search_params.sort == "priority_desc":
            # Sort by urgency (CALL_REQUEST first, then by creation date)
            query = query.order_by(
                Lead.lead_type == "CALL_REQUEST",
                Lead.created_at.desc()
            )
        else:
            query = query.order_by(Lead.created_at.desc())

        # Apply pagination
        query = query.offset(offset).limit(search_params.limit)

        result = await db.execute(query)
        leads = result.scalars().all()

        # Convert to response format
        lead_responses = []
        for lead in leads:
            property_info = PropertyInfo(
                id=str(lead.property_obj.id),
                title=lead.property_obj.title,
                property_type=lead.property_obj.property_type,
                price=float(lead.property_obj.price) if lead.property_obj.price else None,
                city=lead.property_obj.city,
                street=lead.property_obj.street,
            )

            user_info = None
            if lead.user:
                user_info = UserInfo(
                    id=str(lead.user.id),
                    first_name=lead.user.first_name,
                    last_name=lead.user.last_name,
                    email=lead.user.email,
                )

            lead_responses.append(
                LeadListResponse(
                    id=str(lead.id),
                    name=lead.name,
                    phone=lead.phone,
                    email=lead.email,
                    lead_type=lead.lead_type,
                    status=lead.status,
                    created_at=lead.created_at,
                    property=property_info,
                    user=user_info,
                )
            )

        logger.info(
            "Retrieved developer leads",
            developer_id=developer_id,
            filters=search_params.dict(),
            results_count=len(lead_responses),
        )

        return lead_responses

    async def get_lead_stats(
        self,
        db: AsyncSession,
        developer_id: str,
        period: str = "month",
    ) -> dict:
        """
        Get lead statistics for developer.
        
        Args:
            db: Database session
            developer_id: Developer UUID
            period: Statistics period (week, month, quarter, year)
            
        Returns:
            Statistics dictionary
        """
        # Calculate date range based on period
        now = datetime.utcnow()
        if period == "week":
            start_date = now - timedelta(weeks=1)
        elif period == "month":
            start_date = now - timedelta(days=30)
        elif period == "quarter":
            start_date = now - timedelta(days=90)
        elif period == "year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)  # Default to month

        # Base query for leads on developer's properties
        base_query = (
            select(Lead)
            .join(Property, Lead.property_id == Property.id)
            .where(Property.developer_id == UUID(developer_id))
        )

        # Total leads in period
        period_query = base_query.where(Lead.created_at >= start_date)
        period_result = await db.execute(select(func.count(Lead.id)).select_from(period_query.subquery()))
        total_leads = period_result.scalar() or 0

        # Leads by status in period
        status_query = (
            select(Lead.status, func.count(Lead.id))
            .select_from(period_query.subquery())
            .group_by(Lead.status)
        )
        status_result = await db.execute(status_query)
        status_data = status_result.all()

        leads_by_status = {
            "NEW": 0,
            "IN_PROGRESS": 0,
            "COMPLETED": 0,
            "CANCELLED": 0,
        }
        for status, count in status_data:
            leads_by_status[status] = count

        # Leads by type in period
        type_query = (
            select(Lead.lead_type, func.count(Lead.id))
            .select_from(period_query.subquery())
            .group_by(Lead.lead_type)
        )
        type_result = await db.execute(type_query)
        type_data = type_result.all()

        leads_by_type = {
            "CALL_REQUEST": 0,
            "VIEWING": 0,
            "CONSULTATION": 0,
        }
        for lead_type, count in type_data:
            leads_by_type[lead_type] = count

        # Conversion rate (completed / total)
        completed_leads = leads_by_status["COMPLETED"]
        conversion_rate = (completed_leads / total_leads * 100) if total_leads > 0 else 0.0

        # Daily trends (last 7 days)
        daily_trends = []
        for i in range(7):
            day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            day_query = base_query.where(
                and_(
                    Lead.created_at >= day_start,
                    Lead.created_at < day_end
                )
            )
            day_result = await db.execute(select(func.count(Lead.id)).select_from(day_query.subquery()))
            day_count = day_result.scalar() or 0
            
            daily_trends.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "leads": day_count,
            })

        stats = {
            "period": period,
            "total_leads": total_leads,
            "leads_by_status": leads_by_status,
            "leads_by_type": leads_by_type,
            "conversion_rate": round(conversion_rate, 2),
            "daily_trends": list(reversed(daily_trends)),  # Most recent first
        }

        logger.info(
            "Generated lead statistics",
            developer_id=developer_id,
            period=period,
            stats=stats,
        )

        return stats

    async def get_lead_by_id(
        self,
        db: AsyncSession,
        lead_id: str,
        developer_id: str,
    ) -> LeadResponse:
        """
        Get lead by ID (must belong to developer's property).
        
        Args:
            db: Database session
            lead_id: Lead UUID
            developer_id: Developer UUID (for access control)
            
        Returns:
            Lead details
            
        Raises:
            NotFoundException: If lead doesn't exist or doesn't belong to developer
        """
        query = (
            select(Lead)
            .join(Property, Lead.property_id == Property.id)
            .options(
                selectinload(Lead.property_obj),
                selectinload(Lead.user),
            )
            .where(
                and_(
                    Lead.id == UUID(lead_id),
                    Property.developer_id == UUID(developer_id)
                )
            )
        )

        result = await db.execute(query)
        lead = result.scalar_one_or_none()

        if not lead:
            raise NotFoundException(
                message="Заявка не найдена или недоступна",
                details={"lead_id": lead_id, "developer_id": developer_id}
            )

        # Build response
        property_info = PropertyInfo(
            id=str(lead.property_obj.id),
            title=lead.property_obj.title,
            property_type=lead.property_obj.property_type,
            price=float(lead.property_obj.price) if lead.property_obj.price else None,
            city=lead.property_obj.city,
            street=lead.property_obj.street,
        )

        user_info = None
        if lead.user:
            user_info = UserInfo(
                id=str(lead.user.id),
                first_name=lead.user.first_name,
                last_name=lead.user.last_name,
                email=lead.user.email,
            )

        return LeadResponse(
            id=str(lead.id),
            property_id=str(lead.property_id),
            user_id=str(lead.user_id) if lead.user_id else None,
            name=lead.name,
            phone=lead.phone,
            email=lead.email,
            message=lead.message,
            lead_type=lead.lead_type,
            status=lead.status,
            created_at=lead.created_at,
            updated_at=lead.updated_at,
            property=property_info,
            user=user_info,
        )

    async def update_lead_status(
        self,
        db: AsyncSession,
        lead_id: str,
        status_data: LeadStatusUpdateRequest,
        developer_id: str,
    ) -> LeadResponse:
        """
        Update lead status.
        
        Args:
            db: Database session
            lead_id: Lead UUID
            status_data: Status update data
            developer_id: Developer UUID (for access control)
            
        Returns:
            Updated lead
            
        Raises:
            NotFoundException: If lead doesn't exist or doesn't belong to developer
        """
        # Get lead (with access control)
        query = (
            select(Lead)
            .join(Property, Lead.property_id == Property.id)
            .where(
                and_(
                    Lead.id == UUID(lead_id),
                    Property.developer_id == UUID(developer_id)
                )
            )
        )

        result = await db.execute(query)
        lead = result.scalar_one_or_none()

        if not lead:
            raise NotFoundException(
                message="Заявка не найдена или недоступна",
                details={"lead_id": lead_id, "developer_id": developer_id}
            )

        # Update status
        old_status = lead.status
        lead.status = status_data.status

        # Add notes if provided (you might want to create a separate notes table)
        # For now, we'll just log the status change
        if status_data.notes:
            logger.info(
                "Lead status updated with notes",
                lead_id=lead_id,
                old_status=old_status,
                new_status=status_data.status,
                notes=status_data.notes,
                developer_id=developer_id,
            )

        await db.commit()
        await db.refresh(lead)

        logger.info(
            "Updated lead status",
            lead_id=lead_id,
            old_status=old_status,
            new_status=status_data.status,
            developer_id=developer_id,
        )

        return await self.get_lead_by_id(db, lead_id, developer_id)

    async def get_user_inquiries(
        self,
        db: AsyncSession,
        user_id: str,
        page: int = 1,
        limit: int = 20,
    ) -> List[LeadListResponse]:
        """
        Get all inquiries created by a user.
        
        Args:
            db: Database session
            user_id: User UUID
            page: Page number
            limit: Items per page
            
        Returns:
            List of user's inquiries
        """
        offset = (page - 1) * limit

        query = (
            select(Lead)
            .options(
                selectinload(Lead.property_obj),
                selectinload(Lead.user),
            )
            .where(Lead.user_id == UUID(user_id))
            .order_by(Lead.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await db.execute(query)
        leads = result.scalars().all()

        # Convert to response format
        lead_responses = []
        for lead in leads:
            property_info = PropertyInfo(
                id=str(lead.property_obj.id),
                title=lead.property_obj.title,
                property_type=lead.property_obj.property_type,
                price=float(lead.property_obj.price) if lead.property_obj.price else None,
                city=lead.property_obj.city,
                street=lead.property_obj.street,
            )

            user_info = UserInfo(
                id=str(lead.user.id),
                first_name=lead.user.first_name,
                last_name=lead.user.last_name,
                email=lead.user.email,
            )

            lead_responses.append(
                LeadListResponse(
                    id=str(lead.id),
                    name=lead.name,
                    phone=lead.phone,
                    email=lead.email,
                    lead_type=lead.lead_type,
                    status=lead.status,
                    created_at=lead.created_at,
                    property=property_info,
                    user=user_info,
                )
            )

        logger.info(
            "Retrieved user inquiries",
            user_id=user_id,
            page=page,
            limit=limit,
            count=len(lead_responses),
        )

        return lead_responses
