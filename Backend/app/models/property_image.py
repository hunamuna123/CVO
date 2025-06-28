"""
PropertyImage model for property images.
"""

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import *
from app.models.base import BaseModel


class PropertyImage(BaseModel):
    """
    PropertyImage model for property images.

    Represents images associated with properties.
    """

    __tablename__ = "property_images"

    # Property relationship
    property_id: Mapped[str] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to Property",
    )

    # Image information
    url: Mapped[str] = mapped_column(String(500), nullable=False, comment="Image URL")

    title: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="Image description"
    )

    is_main: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Is main image"
    )

    order: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="Display order"
    )

    # Relationships
    property: Mapped["Property"] = relationship("Property", back_populates="images")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<PropertyImage(property_id='{self.property_id}', is_main={self.is_main})>"
        )
