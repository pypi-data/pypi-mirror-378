"""Core enumerations for the Celeste AI Framework."""

from enum import Enum, Flag, auto


class Provider(str, Enum):
    """Supported AI providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    COHERE = "cohere"
    XAI = "xai"
    HUGGINGFACE = "huggingface"
    REPLICATE = "replicate"
    STABILITYAI = "stabilityai"
    LUMA = "luma"
    TOPAZLABS = "topazlabs"
    OLLAMA = "ollama"
    TRANSFORMERS = "transformers"
    LOCAL = "local"


class Capability(Flag):
    """Supported AI capabilities."""

    # Text
    TEXT_GENERATION = auto()

    # Image
    IMAGE_GENERATION = auto()


__all__ = ["Capability", "Provider"]
