"""MIME type enumerations for the Celeste AI framework."""

from enum import Enum


class MimeType(str, Enum):
    """Base class for all MIME types."""

    pass


class ImageMimeType(MimeType):
    """Standard MIME types for images."""

    PNG = "image/png"
    JPEG = "image/jpeg"
    # WEBP = "image/webp"


class VideoMimeType(MimeType):
    """Standard MIME types for videos."""

    MP4 = "video/mp4"
    # AVI = "video/x-msvideo"
    # MOV = "video/quicktime"


class AudioMimeType(MimeType):
    """Standard MIME types for audio."""

    MP3 = "audio/mpeg"
    WAV = "audio/wav"
    # OGG = "audio/ogg"
    # WEBM = "audio/webm"
    # AAC = "audio/aac"
    # FLAC = "audio/flac"
    # M4A = "audio/mp4"
    # WMA = "audio/x-ms-wma"


__all__ = [
    "AudioMimeType",
    "ImageMimeType",
    "MimeType",
    "VideoMimeType",
]
