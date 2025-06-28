"""
SearchHistory model for search history tracking.
"""

from typing import Any, Dict, Optional

from sqlalchemy import JSON, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import *
from app.models.base import BaseModel


class SearchHistory(BaseModel):
    """
    SearchHistory model for search history tracking.

    Tracks search queries and filters used by users.
    """

    __tablename__ = "search_history"

    # User relationship (optional for anonymous users)
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="FK to User (may be null for anonymous)",
    )

    # Session tracking
    session_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Session ID for anonymous users",
    )

    # Search details
    search_query: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Search query text"
    )

    filters: Mapped[Dict[str, Any]] = mapped_column(
        JSON, nullable=False, comment="Applied filters as JSON"
    )

    results_count: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Number of search results"
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="search_history"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<SearchHistory(session_id='{self.session_id}', results_count={self.results_count})>"
