"""
Review model for user reviews.
"""

from typing import Optional
from uuid import UUID as PyUUID

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import *
from app.models.base import BaseModel


class Review(BaseModel):
    """
    Review model for user reviews.

    Represents reviews that users can leave for developers and properties.
    """

    __tablename__ = "reviews"

    # User relationship
    user_id: Mapped[PyUUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to User",
    )

    # Property relationship (optional)
    property_id: Mapped[Optional[PyUUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="FK to Property (optional)",
    )

    # Developer relationship
    developer_id: Mapped[PyUUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("developers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to Developer",
    )

    # Review content
    rating: Mapped[int] = mapped_column(Integer, nullable=False, comment="Rating 1-5")

    title: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Review title"
    )

    content: Mapped[str] = mapped_column(Text, nullable=False, comment="Review content")

    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Verified by moderator"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="reviews")

    developer: Mapped["Developer"] = relationship("Developer", back_populates="reviews")

    property_obj: Mapped[Optional["Property"]] = relationship(
        "Property", back_populates="reviews"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Review(user_id='{self.user_id}', developer_id='{self.developer_id}', rating={self.rating})>"
