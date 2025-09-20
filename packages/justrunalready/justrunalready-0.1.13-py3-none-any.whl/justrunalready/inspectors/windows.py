from __future__ import annotations

from pathlib import Path
from typing import List

from justrunalready.inspectors.base import InspectorBase


class WindowsInspector(InspectorBase):
    """Windows PE binary inspector."""

    @property
    def name(self) -> str:
        return "windows"

    def list_needed(self, pe: Path) -> List[str]:
        """List DLLs needed by a Windows PE binary."""
        try:
            import pefile

            pef = pefile.PE(str(pe))
            names: List[str] = []
            if hasattr(pef, "DIRECTORY_ENTRY_IMPORT"):
                for entry in pef.DIRECTORY_ENTRY_IMPORT:
                    if entry.dll:
                        names.append(entry.dll.decode("ascii", errors="ignore"))
            return names
        except ImportError:
            pass

        import subprocess

        try:
            r = subprocess.run(
                ["dumpbin", "/dependents", str(pe)], capture_output=True, text=True
            )
            if r.returncode == 0:
                out: List[str] = []
                for line in r.stdout.splitlines():
                    line = line.strip()
                    if line.upper().endswith(".DLL"):
                        out.append(line)
                return out
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

        raise RuntimeError(
            f"Unable to inspect Windows PE file {pe}: neither pefile nor dumpbin available"
        )

    def supports_file(self, file: Path) -> bool:
        """Check if this is a PE file we can inspect."""
        return file.suffix.lower() in (".exe", ".dll", ".pyd", ".sys")
