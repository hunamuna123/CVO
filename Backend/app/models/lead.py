"""
Lead model for user leads/inquiries.
"""

import enum
from typing import Optional

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import *
from app.models.base import BaseModel


class LeadType(str, enum.Enum):
    """Lead type enumeration."""

    CALL_REQUEST = "CALL_REQUEST"
    VIEWING = "VIEWING"
    CONSULTATION = "CONSULTATION"


class LeadStatus(str, enum.Enum):
    """Lead status enumeration."""

    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Lead(BaseModel):
    """
    Lead model for user leads/inquiries.

    Represents inquiries from potential buyers/renters.
    """

    __tablename__ = "leads"

    # Property relationship
    property_id: Mapped[str] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to Property",
    )

    # User relationship (optional for anonymous leads)
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK to User (may be null for anonymous)",
    )

    # Contact information
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Contact name"
    )

    phone: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="Contact phone"
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(254), nullable=True, comment="Contact email"
    )

    message: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Lead message"
    )

    # Lead details
    lead_type: Mapped[LeadType] = mapped_column(
        Enum(LeadType), nullable=False, comment="Lead type"
    )

    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus),
        default=LeadStatus.NEW,
        nullable=False,
        index=True,
        comment="Lead status",
    )

    # Relationships
    property: Mapped["Property"] = relationship("Property", back_populates="leads")

    user: Mapped[Optional["User"]] = relationship("User", back_populates="leads")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Lead(property_id='{self.property_id}', name='{self.name}', type='{self.lead_type}')>"
