"""
PropertyDocument model for property documents.
"""

import enum
from uuid import UUID as PyUUID

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import *
from app.models.base import BaseModel


class DocumentType(str, enum.Enum):
    """Document type enumeration."""

    PLAN = "PLAN"
    CERTIFICATE = "CERTIFICATE"
    CONTRACT = "CONTRACT"
    OTHER = "OTHER"


class PropertyDocument(BaseModel):
    """
    PropertyDocument model for property documents.

    Represents documents associated with properties.
    """

    __tablename__ = "property_documents"

    # Property relationship
    property_id: Mapped[PyUUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK to Property",
    )

    # Document information
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType), nullable=False, comment="Document type"
    )

    title: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Document title"
    )

    file_url: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="File URL"
    )

    file_size: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="File size in bytes"
    )

    mime_type: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="MIME type"
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="Is document verified"
    )

    # Relationships
    property_obj: Mapped["Property"] = relationship("Property", back_populates="documents")

    def __repr__(self) -> str:
        """String representation."""
        return f"<PropertyDocument(property_id='{self.property_id}', type='{self.document_type}')>"
