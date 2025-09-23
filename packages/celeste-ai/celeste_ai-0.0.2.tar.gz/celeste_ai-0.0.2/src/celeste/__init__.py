"""Celeste AI Framework"""

__version__ = "0.0.1"
__author__ = "agent-kai"

from celeste.core import Capability, Provider


def create_client(
    capability: Capability,
    provider: Provider,
    model: str,  # TODO: Use real Model type
) -> None:
    """
    Placeholder for the universal client factory.

    The full implementation will provide a unified interface for all AI capabilities.
    """
    raise NotImplementedError(
        "Celeste AI is in development. "
        "This is a placeholder package to reserve the name. "
        "Follow updates at: https://github.com/celeste-kai/celeste-ai"
    )


# Placeholder exports
__all__ = ["create_client"]
