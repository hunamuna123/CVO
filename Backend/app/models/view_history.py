"""
ViewHistory model for property view tracking.
"""

from typing import Optional
from uuid import UUID as PyUUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import *
from app.models.base import BaseModel


class ViewHistory(BaseModel):
    """
    ViewHistory model for property view tracking.

    Tracks when users view specific properties.
    """

    __tablename__ = "view_history"

    # User relationship (optional for anonymous users)
    user_id: Mapped[Optional[PyUUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="FK to User (may be null for anonymous)",
    )

    # Property relationship
    property_id: Mapped[PyUUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to Property",
    )

    # Session and tracking info
    session_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="Session ID"
    )

    ip_address: Mapped[str] = mapped_column(
        String(45), nullable=False, comment="IP address"  # IPv6 max length
    )

    user_agent: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="User agent string"
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="view_history")

    property_obj: Mapped["Property"] = relationship(
        "Property", back_populates="view_history"
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<ViewHistory(property_id='{self.property_id}', ip='{self.ip_address}')>"
        )
