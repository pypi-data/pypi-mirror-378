from __future__ import annotations

from abc import ABC, abstractmethod


class WrapperBase(ABC):
    name: str = "wrapper"

    @abstractmethod
    def supports(self, platform: str) -> bool:
        """Return True if this wrapper supports the given platform string."""

    @abstractmethod
    def run(self, cfg) -> str:
        """Create the wrapped artifact and return the output path as a string."""
