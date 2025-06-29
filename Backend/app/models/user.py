"""
User model for authentication and profiles.
"""

import enum
from typing import List, Optional

from sqlalchemy import Boolean, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    """User role enumeration."""

    USER = "USER"
    DEVELOPER = "DEVELOPER"
    ADMIN = "ADMIN"


class User(BaseModel):
    """
    User model for authentication and profiles.

    Represents users in the system with different roles.
    Phone number is required for registration and authentication.
    """

    __tablename__ = "users"

    # Authentication fields
    phone: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Phone number in international format (+7XXXXXXXXXX)",
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(254),
        unique=True,
        nullable=True,
        index=True,
        comment="Email address (optional)",
    )

    # Profile fields
    first_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="First name"
    )

    last_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Last name"
    )

    middle_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="Middle name (optional)"
    )

    # Role and status
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.USER, nullable=False, comment="User role"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="Is user active"
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Is phone number verified"
    )

    # Profile image
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="Avatar image URL"
    )

    # Relationships
    developer_profile: Mapped[Optional["Developer"]] = relationship(
        "Developer", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    favorites: Mapped[List["Favorite"]] = relationship(
        "Favorite", back_populates="user", cascade="all, delete-orphan"
    )

    reviews: Mapped[List["Review"]] = relationship(
        "Review", back_populates="user", cascade="all, delete-orphan"
    )

    search_history: Mapped[List["SearchHistory"]] = relationship(
        "SearchHistory", back_populates="user", cascade="all, delete-orphan"
    )

    view_history: Mapped[List["ViewHistory"]] = relationship(
        "ViewHistory", back_populates="user", cascade="all, delete-orphan"
    )

    leads: Mapped[List["Lead"]] = relationship(
        "Lead", back_populates="user", cascade="all, delete-orphan"
    )

    bookings: Mapped[List["Booking"]] = relationship(
        "Booking", back_populates="user", cascade="all, delete-orphan"
    )

    # Methods
    @property
    def full_name(self) -> str:
        """Get full name."""
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"

    @property
    def is_developer(self) -> bool:
        """Check if user is a developer."""
        return self.role == UserRole.DEVELOPER

    @property
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN

    def __repr__(self) -> str:
        """String representation."""
        return f"<User(phone={self.phone}, role={self.role.value})>"
