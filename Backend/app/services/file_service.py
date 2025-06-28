"""
File upload and processing service.
"""

import asyncio
import mimetypes
import os
import uuid
from pathlib import Path
from typing import BinaryIO, List, Optional, Tuple, Union

import aiofiles
import structlog
from fastapi import HTTPException, UploadFile, status
from PIL import Image, ImageOps

from app.core.config import get_settings

logger = structlog.get_logger(__name__)


class FileService:
    """Service for handling file uploads and processing."""

    def __init__(self):
        self.settings = get_settings()
        self.media_root = Path(self.settings.media_root)
        self.ensure_media_directories()

    def ensure_media_directories(self) -> None:
        """Ensure all media directories exist."""
        directories = [
            "properties/images",
            "properties/documents",
            "developers/logos",
            "users/avatars",
            "temp",
        ]

        for directory in directories:
            dir_path = self.media_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)

    async def upload_property_image(
        self, file: UploadFile, property_id: str, is_main: bool = False
    ) -> Tuple[str, str]:
        """
        Upload and process property image.

        Returns:
            Tuple[str, str]: (file_url, thumbnail_url)
        """
        return await self._upload_image(
            file=file,
            category="properties/images",
            entity_id=property_id,
            create_thumbnail=True,
        )

    async def upload_user_avatar(self, file: UploadFile, user_id: str) -> str:
        """Upload and process user avatar."""
        file_url, _ = await self._upload_image(
            file=file,
            category="users/avatars",
            entity_id=user_id,
            create_thumbnail=False,
            max_size=(500, 500),
        )
        return file_url

    async def upload_developer_logo(self, file: UploadFile, developer_id: str) -> str:
        """Upload and process developer logo."""
        file_url, _ = await self._upload_image(
            file=file,
            category="developers/logos",
            entity_id=developer_id,
            create_thumbnail=False,
            max_size=(400, 400),
        )
        return file_url

    async def upload_property_document(self, file: UploadFile, property_id: str) -> str:
        """Upload property document."""
        return await self._upload_document(
            file=file, category="properties/documents", entity_id=property_id
        )

    async def _upload_image(
        self,
        file: UploadFile,
        category: str,
        entity_id: str,
        create_thumbnail: bool = True,
        max_size: Optional[Tuple[int, int]] = None,
    ) -> Tuple[str, Optional[str]]:
        """
        Upload and process image file.

        Args:
            file: Uploaded file
            category: Storage category (e.g., 'properties/images')
            entity_id: Entity ID for organizing files
            create_thumbnail: Whether to create thumbnail
            max_size: Maximum size for resizing (width, height)

        Returns:
            Tuple[str, Optional[str]]: (file_url, thumbnail_url)
        """
        # Validate file
        await self._validate_image_file(file)

        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.webp"

        # Create directory structure
        entity_dir = self.media_root / category / entity_id
        entity_dir.mkdir(parents=True, exist_ok=True)

        # File paths
        file_path = entity_dir / filename
        thumbnail_path = (
            entity_dir / f"{file_id}_thumb.webp" if create_thumbnail else None
        )

        # Process and save image
        try:
            # Read uploaded file
            content = await file.read()
            await file.seek(0)  # Reset file pointer

            # Process image in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._process_image,
                content,
                str(file_path),
                str(thumbnail_path) if thumbnail_path else None,
                max_size,
            )

            # Generate URLs
            file_url = f"{self.settings.media_url}{category}/{entity_id}/{filename}"
            thumbnail_url = (
                f"{self.settings.media_url}{category}/{entity_id}/{file_id}_thumb.webp"
                if create_thumbnail
                else None
            )

            logger.info(
                "Image uploaded successfully",
                entity_id=entity_id,
                category=category,
                filename=filename,
                file_size=len(content),
            )

            return file_url, thumbnail_url

        except Exception as e:
            logger.error(
                "Failed to upload image",
                entity_id=entity_id,
                category=category,
                error=str(e),
                exc_info=True,
            )
            # Clean up partial files
            if file_path.exists():
                file_path.unlink()
            if thumbnail_path and thumbnail_path.exists():
                Path(thumbnail_path).unlink()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "IMAGE_PROCESSING_FAILED",
                        "message": "Не удалось обработать изображение",
                        "details": {"error": str(e)},
                    }
                },
            )

    async def _upload_document(
        self, file: UploadFile, category: str, entity_id: str
    ) -> str:
        """Upload document file."""
        # Validate file
        await self._validate_document_file(file)

        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix.lower()
        filename = f"{file_id}{file_extension}"

        # Create directory structure
        entity_dir = self.media_root / category / entity_id
        entity_dir.mkdir(parents=True, exist_ok=True)

        # File path
        file_path = entity_dir / filename

        try:
            # Save file
            async with aiofiles.open(file_path, "wb") as f:
                content = await file.read()
                await f.write(content)

            # Generate URL
            file_url = f"{self.settings.media_url}{category}/{entity_id}/{filename}"

            logger.info(
                "Document uploaded successfully",
                entity_id=entity_id,
                category=category,
                filename=filename,
                file_size=len(content),
            )

            return file_url

        except Exception as e:
            logger.error(
                "Failed to upload document",
                entity_id=entity_id,
                category=category,
                error=str(e),
                exc_info=True,
            )
            # Clean up partial file
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "DOCUMENT_UPLOAD_FAILED",
                        "message": "Не удалось загрузить документ",
                        "details": {"error": str(e)},
                    }
                },
            )

    def _process_image(
        self,
        content: bytes,
        file_path: str,
        thumbnail_path: Optional[str] = None,
        max_size: Optional[Tuple[int, int]] = None,
    ) -> None:
        """Process image: resize, optimize, and save as WebP."""
        with Image.open(io.BytesIO(content)) as img:
            # Convert to RGB if necessary
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(
                    img, mask=img.split()[-1] if img.mode == "RGBA" else None
                )
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Auto-orient image based on EXIF
            img = ImageOps.exif_transpose(img)

            # Resize if max_size is specified
            if max_size:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Save main image
            img.save(
                file_path, "WEBP", quality=self.settings.image_quality, optimize=True
            )

            # Create thumbnail if requested
            if thumbnail_path:
                thumb_size = (300, 300)  # Default thumbnail size
                img_thumb = img.copy()
                img_thumb.thumbnail(thumb_size, Image.Resampling.LANCZOS)
                img_thumb.save(thumbnail_path, "WEBP", quality=80, optimize=True)

    async def _validate_image_file(self, file: UploadFile) -> None:
        """Validate uploaded image file."""
        # Check file size
        if file.size and file.size > self.settings.max_upload_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail={
                    "error": {
                        "code": "FILE_TOO_LARGE",
                        "message": f"Файл слишком большой. Максимальный размер: {self.settings.max_upload_size // (1024*1024)}MB",
                        "details": {"max_size": self.settings.max_upload_size},
                    }
                },
            )

        # Check file extension
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_FILENAME",
                        "message": "Имя файла не указано",
                        "details": {},
                    }
                },
            )

        file_extension = Path(file.filename).suffix.lower().lstrip(".")
        if file_extension not in self.settings.allowed_image_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_FILE_TYPE",
                        "message": f"Недопустимый тип файла. Разрешены: {', '.join(self.settings.allowed_image_extensions)}",
                        "details": {
                            "allowed_types": self.settings.allowed_image_extensions
                        },
                    }
                },
            )

        # Check MIME type
        mime_type, _ = mimetypes.guess_type(file.filename)
        if not mime_type or not mime_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_MIME_TYPE",
                        "message": "Файл не является изображением",
                        "details": {"mime_type": mime_type},
                    }
                },
            )

    async def _validate_document_file(self, file: UploadFile) -> None:
        """Validate uploaded document file."""
        # Check file size
        if file.size and file.size > self.settings.max_upload_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail={
                    "error": {
                        "code": "FILE_TOO_LARGE",
                        "message": f"Файл слишком большой. Максимальный размер: {self.settings.max_upload_size // (1024*1024)}MB",
                        "details": {"max_size": self.settings.max_upload_size},
                    }
                },
            )

        # Check file extension
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_FILENAME",
                        "message": "Имя файла не указано",
                        "details": {},
                    }
                },
            )

        file_extension = Path(file.filename).suffix.lower().lstrip(".")
        if file_extension not in self.settings.allowed_document_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_FILE_TYPE",
                        "message": f"Недопустимый тип файла. Разрешены: {', '.join(self.settings.allowed_document_extensions)}",
                        "details": {
                            "allowed_types": self.settings.allowed_document_extensions
                        },
                    }
                },
            )

    async def delete_file(self, file_url: str) -> bool:
        """Delete file by URL."""
        try:
            # Extract file path from URL
            relative_path = file_url.replace(self.settings.media_url, "").lstrip("/")
            file_path = self.media_root / relative_path

            if file_path.exists():
                file_path.unlink()

                # Also delete thumbnail if it exists
                if "_thumb" not in file_path.stem:
                    thumb_path = (
                        file_path.parent / f"{file_path.stem}_thumb{file_path.suffix}"
                    )
                    if thumb_path.exists():
                        thumb_path.unlink()

                logger.info("File deleted successfully", file_path=str(file_path))
                return True

            return False

        except Exception as e:
            logger.error(
                "Failed to delete file", file_url=file_url, error=str(e), exc_info=True
            )
            return False

    def get_file_info(self, file_url: str) -> Optional[dict]:
        """Get file information."""
        try:
            relative_path = file_url.replace(self.settings.media_url, "").lstrip("/")
            file_path = self.media_root / relative_path

            if not file_path.exists():
                return None

            stat = file_path.stat()
            return {
                "size": stat.st_size,
                "created_at": stat.st_ctime,
                "modified_at": stat.st_mtime,
                "extension": file_path.suffix.lower(),
                "mime_type": mimetypes.guess_type(str(file_path))[0],
            }

        except Exception:
            return None


# Add missing import
import io
