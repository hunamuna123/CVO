"""
Property model for real estate objects.
"""

import enum
from datetime import date
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Date,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import *
from app.models.base import BaseModel


class PropertyType(str, enum.Enum):
    """Property type enumeration."""

    APARTMENT = "APARTMENT"
    HOUSE = "HOUSE"
    COMMERCIAL = "COMMERCIAL"


class DealType(str, enum.Enum):
    """Deal type enumeration."""

    SALE = "SALE"
    RENT = "RENT"


class PropertyStatus(str, enum.Enum):
    """Property status enumeration."""

    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    SOLD = "SOLD"
    RENTED = "RENTED"
    ARCHIVED = "ARCHIVED"


class RenovationType(str, enum.Enum):
    """Renovation type enumeration."""

    NONE = "NONE"
    COSMETIC = "COSMETIC"
    EURO = "EURO"
    DESIGNER = "DESIGNER"


class Property(BaseModel):
    """
    Property model for real estate objects.

    Represents properties (apartments, houses, commercial)
    that can be sold or rented.
    """

    __tablename__ = "properties"

    # Developer relationship
    developer_id: Mapped[str] = mapped_column(
        ForeignKey("developers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to Developer",
    )

    # Basic information
    title: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="Property title"
    )

    description: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Property description"
    )

    property_type: Mapped[PropertyType] = mapped_column(
        Enum(PropertyType), nullable=False, index=True, comment="Property type"
    )

    deal_type: Mapped[DealType] = mapped_column(
        Enum(DealType), nullable=False, index=True, comment="Deal type"
    )

    # Price information
    price: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, index=True, comment="Price in rubles"
    )

    price_per_sqm: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="Price per square meter"
    )

    currency: Mapped[str] = mapped_column(
        String(3), default="RUB", nullable=False, comment="Currency code"
    )

    # Address information
    region: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, comment="Region"
    )

    city: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, comment="City"
    )

    district: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="District"
    )

    street: Mapped[str] = mapped_column(String(255), nullable=False, comment="Street")

    house_number: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="House number"
    )

    apartment_number: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="Apartment number"
    )

    postal_code: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True, comment="Postal code"
    )

    # Coordinates
    latitude: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Latitude"
    )

    longitude: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Longitude"
    )

    # Characteristics
    total_area: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Total area in square meters"
    )

    living_area: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Living area in square meters"
    )

    kitchen_area: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Kitchen area in square meters"
    )

    rooms_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, index=True, comment="Number of rooms"
    )

    bedrooms_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Number of bedrooms"
    )

    bathrooms_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Number of bathrooms"
    )

    floor: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Floor number"
    )

    total_floors: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Total floors in building"
    )

    building_year: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Building construction year"
    )

    ceiling_height: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Ceiling height in meters"
    )

    # Features
    has_balcony: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Has balcony"
    )

    has_loggia: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Has loggia"
    )

    has_elevator: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Has elevator"
    )

    has_parking: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True, comment="Has parking"
    )

    has_furniture: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Has furniture"
    )

    renovation_type: Mapped[Optional[RenovationType]] = mapped_column(
        Enum(RenovationType), nullable=True, comment="Renovation type"
    )

    # Status and metrics
    status: Mapped[PropertyStatus] = mapped_column(
        Enum(PropertyStatus),
        default=PropertyStatus.DRAFT,
        nullable=False,
        index=True,
        comment="Property status",
    )

    is_featured: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True, comment="Featured property"
    )

    views_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="Number of views"
    )

    favorites_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="Number of favorites"
    )

    # Availability
    available_from: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="Available from date"
    )

    # Relationships
    developer: Mapped["Developer"] = relationship(
        "Developer", back_populates="properties"
    )

    images: Mapped[List["PropertyImage"]] = relationship(
        "PropertyImage",
        back_populates="property",
        cascade="all, delete-orphan",
        order_by="PropertyImage.order",
    )

    documents: Mapped[List["PropertyDocument"]] = relationship(
        "PropertyDocument", back_populates="property", cascade="all, delete-orphan"
    )

    favorites: Mapped[List["Favorite"]] = relationship(
        "Favorite", back_populates="property", cascade="all, delete-orphan"
    )

    view_history: Mapped[List["ViewHistory"]] = relationship(
        "ViewHistory", back_populates="property", cascade="all, delete-orphan"
    )

    leads: Mapped[List["Lead"]] = relationship(
        "Lead", back_populates="property", cascade="all, delete-orphan"
    )

    reviews: Mapped[List["Review"]] = relationship(
        "Review", back_populates="property", cascade="all, delete-orphan"
    )

    # Methods
    @property
    def full_address(self) -> str:
        """Get full address string."""
        parts = [self.region, self.city]
        if self.district:
            parts.append(self.district)
        parts.extend([self.street, self.house_number])
        if self.apartment_number:
            parts.append(f"кв. {self.apartment_number}")
        return ", ".join(parts)

    @property
    def main_image(self) -> Optional["PropertyImage"]:
        """Get main image."""
        for image in self.images:
            if image.is_main:
                return image
        return self.images[0] if self.images else None

    def increment_views(self) -> None:
        """Increment views counter."""
        self.views_count += 1

    def update_favorites_count(self) -> None:
        """Update favorites counter."""
        self.favorites_count = len(self.favorites)

    def calculate_price_per_sqm(self) -> None:
        """Calculate price per square meter."""
        if self.total_area and self.total_area > 0:
            self.price_per_sqm = self.price / Decimal(str(self.total_area))

    @property
    def is_available(self) -> bool:
        """Check if property is available for deals."""
        return self.status in [PropertyStatus.ACTIVE]

    def __repr__(self) -> str:
        """String representation."""
        return f"<Property(title='{self.title}', type='{self.property_type}', price={self.price})>"
