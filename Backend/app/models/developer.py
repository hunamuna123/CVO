"""
Developer model for real estate developers.
"""

import enum
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import Boolean, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import *
from app.models.base import BaseModel


class VerificationStatus(str, enum.Enum):
    """Developer verification status enumeration."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Developer(BaseModel):
    """
    Developer model for real estate developers/companies.

    Represents development companies that create and manage properties.
    Each developer is linked to a user account with DEVELOPER role.
    """

    __tablename__ = "developers"

    # User relationship
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="FK to User",
    )

    # Company information
    company_name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="Company name"
    )

    legal_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Legal company name"
    )

    inn: Mapped[str] = mapped_column(
        String(12),
        unique=True,
        nullable=False,
        index=True,
        comment="INN number (unique)",
    )

    ogrn: Mapped[str] = mapped_column(String(15), nullable=False, comment="OGRN number")

    legal_address: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Legal address"
    )

    # Contact information
    contact_phone: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="Contact phone number"
    )

    contact_email: Mapped[str] = mapped_column(
        String(254), nullable=False, comment="Contact email"
    )

    website: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="Company website"
    )

    # Description and branding
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Company description"
    )

    logo_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="Company logo URL"
    )

    # Rating and reviews
    rating: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.00"),
        nullable=False,
        comment="Average rating 0-5",
    )

    reviews_count: Mapped[int] = mapped_column(
        default=0, nullable=False, comment="Number of reviews"
    )

    # Verification status
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Passed verification"
    )

    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus),
        default=VerificationStatus.PENDING,
        nullable=False,
        comment="Verification status",
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="developer_profile")

    properties: Mapped[List["Property"]] = relationship(
        "Property", back_populates="developer", cascade="all, delete-orphan"
    )

    reviews: Mapped[List["Review"]] = relationship(
        "Review", back_populates="developer", cascade="all, delete-orphan"
    )

    # Methods
    def update_rating(self) -> None:
        """Update average rating based on reviews."""
        if self.reviews:
            total_rating = sum(review.rating for review in self.reviews)
            self.rating = Decimal(total_rating / len(self.reviews))
            self.reviews_count = len(self.reviews)
        else:
            self.rating = Decimal("0.00")
            self.reviews_count = 0

    @property
    def is_approved(self) -> bool:
        """Check if developer is approved."""
        return self.verification_status == VerificationStatus.APPROVED

    def __repr__(self) -> str:
        """String representation."""
        return f"<Developer(company_name='{self.company_name}', inn='{self.inn}')>"
