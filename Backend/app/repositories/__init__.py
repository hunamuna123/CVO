"""
Repository pattern implementation for data access layer.

This module provides abstract repositories and their implementations,
ensuring clean separation between business logic and data access.
"""

from .base import IRepository, BaseRepository
from .user_repository import IUserRepository, UserRepository
from .property_repository import IPropertyRepository, PropertyRepository
from .developer_repository import IDeveloperRepository, DeveloperRepository

__all__ = [
    "IRepository",
    "BaseRepository", 
    "IUserRepository",
    "UserRepository",
    "IPropertyRepository",
    "PropertyRepository",
    "IDeveloperRepository",
    "DeveloperRepository",
]
