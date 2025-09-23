"""Unified artifact types for the Celeste AI framework."""

from typing import Any, Optional, Union

from pydantic import BaseModel, Field

from celeste.mime_types import AudioMimeType, ImageMimeType, VideoMimeType


class Artifact(BaseModel):
    """Base class for all media artifacts.

    Artifacts can be represented in three ways:
    - url: Remote HTTP/HTTPS URL (may expire, e.g., DALL-E URLs last 1 hour)
    - data: In-memory bytes (for immediate use without download)
    - path: Local filesystem path (for local providers or saved files)

    Providers typically populate only one of these fields.
    """

    url: Optional[str] = None
    data: Optional[bytes] = None
    path: Optional[str] = None
    mime_type: Optional[str] = None  # Standard MIME type for the artifact
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def has_content(self) -> bool:
        """Check if artifact has any content."""
        return bool(self.url or self.data or self.path)


class ImageArtifact(Artifact):
    """Image artifact from generation/edit operations."""

    mime_type: Optional[Union[ImageMimeType, str]] = None


class VideoArtifact(Artifact):
    """Video artifact from generation operations."""

    mime_type: Optional[Union[VideoMimeType, str]] = None


class AudioArtifact(Artifact):
    """Audio artifact from TTS/transcription operations."""

    mime_type: Optional[Union[AudioMimeType, str]] = None


__all__ = [
    "Artifact",
    "AudioArtifact",
    "ImageArtifact",
    "VideoArtifact",
]
