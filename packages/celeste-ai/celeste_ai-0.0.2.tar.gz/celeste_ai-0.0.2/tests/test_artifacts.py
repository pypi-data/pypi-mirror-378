"""High-value tests for artifact classes - focusing on real-world usage patterns."""

from typing import Any

import pytest

from celeste.artifacts import Artifact, AudioArtifact, ImageArtifact, VideoArtifact
from celeste.mime_types import AudioMimeType, ImageMimeType, VideoMimeType


class TestArtifact:
    """Test base Artifact class behavior."""

    @pytest.mark.parametrize(
        "storage_combo,expected",
        [
            # Single storage types
            ({"url": "https://example.com/file"}, True),
            ({"data": b"data"}, True),
            ({"path": "/path/to/file"}, True),
            # Empty artifact
            ({}, False),
            # Multiple storage types
            ({"url": "https://example.com", "data": b"data"}, True),
            ({"url": "https://example.com", "data": b"data", "path": "/path"}, True),
            # Edge case: all None explicitly
            ({"url": None, "data": None, "path": None}, False),
            # Edge case: empty string path (common mistake)
            ({"path": ""}, False),
        ],
    )
    def test_has_content_with_storage_combinations(
        self, storage_combo: dict[str, Any], expected: bool
    ) -> None:
        """Test has_content correctly identifies content across all storage combinations."""
        artifact = Artifact(**storage_combo)
        assert artifact.has_content == expected

    def test_artifact_with_multiple_storage_types_preserves_values(self) -> None:
        """Artifact can have multiple storage types simultaneously (common in caching scenarios)."""
        artifact = Artifact(
            url="https://example.com/file.png",
            data=b"cached data",
            path="/cache/file.png",
        )
        assert artifact.has_content is True
        assert artifact.url == "https://example.com/file.png"
        assert artifact.data == b"cached data"
        assert artifact.path == "/cache/file.png"


class TestImageArtifact:
    """Test ImageArtifact specific behavior."""

    def test_image_artifact_accepts_image_mime_type(self) -> None:
        """ImageArtifact should accept valid image MIME types."""
        artifact = ImageArtifact(
            url="https://example.com/image.png", mime_type=ImageMimeType.PNG
        )
        assert artifact.mime_type == ImageMimeType.PNG

    def test_image_artifact_preserves_string_mime_type(self) -> None:
        """ImageArtifact should preserve string MIME types (for provider flexibility)."""
        custom_mime = "image/webp"  # Not in our enum but valid
        artifact = ImageArtifact(data=b"webp data", mime_type=custom_mime)
        assert artifact.mime_type == custom_mime


class TestVideoArtifact:
    """Test VideoArtifact specific behavior."""

    def test_video_artifact_accepts_video_mime_type(self) -> None:
        """VideoArtifact should accept valid video MIME types."""
        artifact = VideoArtifact(path="/videos/sample.mp4", mime_type=VideoMimeType.MP4)
        assert artifact.mime_type == VideoMimeType.MP4


class TestAudioArtifact:
    """Test AudioArtifact specific behavior."""

    @pytest.mark.parametrize("mime_type", [AudioMimeType.MP3, AudioMimeType.WAV])
    def test_audio_artifact_supports_common_formats(
        self, mime_type: AudioMimeType
    ) -> None:
        """AudioArtifact should support common audio formats."""
        artifact = AudioArtifact(
            url=f"https://example.com/audio.{mime_type.value.split('/')[-1]}",
            mime_type=mime_type,
        )
        assert artifact.mime_type == mime_type
