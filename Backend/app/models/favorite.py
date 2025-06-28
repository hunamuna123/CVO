"""
Favorite model for user favorites.
"""

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import *
from app.models.base import BaseModel


class Favorite(BaseModel):
    """
    Favorite model for user favorites.

    Represents properties that users have added to their favorites.
    """

    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "property_id", name="uq_user_property_favorite"),
    )

    # User relationship
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to User",
    )

    # Property relationship
    property_id: Mapped[str] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to Property",
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="favorites")

    property: Mapped["Property"] = relationship("Property", back_populates="favorites")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Favorite(user_id='{self.user_id}', property_id='{self.property_id}')>"
