"""
Review model for user reviews.
"""

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
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
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to User",
    )

    # Developer relationship
    developer_id: Mapped[str] = mapped_column(
        ForeignKey("developers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to Developer",
    )

    # Property relationship (optional)
    property_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="FK to Property (optional)",
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

    property: Mapped[Optional["Property"]] = relationship(
        "Property", back_populates="reviews"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Review(user_id='{self.user_id}', developer_id='{self.developer_id}', rating={self.rating})>"
