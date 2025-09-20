"""Base class for binary inspectors."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List


class InspectorBase(ABC):
    """Base class for platform-specific binary inspectors."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the inspector name (e.g., 'linux', 'windows', 'macos')."""
        pass

    @abstractmethod
    def list_needed(self, binary: Path) -> List[str]:
        """List the dependencies needed by the given binary.

        Args:
            binary: Path to the binary file to inspect

        Returns:
            List of dependency names or paths
        """
        pass

    def supports_file(self, file: Path) -> bool:
        """Check if this inspector can handle the given file.

        Default implementation returns True. Subclasses can override
        to provide more specific checks.

        Args:
            file: Path to the file to check

        Returns:
            True if this inspector can handle the file
        """
        return True
