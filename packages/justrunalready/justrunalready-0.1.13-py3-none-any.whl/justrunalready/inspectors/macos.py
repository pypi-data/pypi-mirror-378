from __future__ import annotations

from pathlib import Path
from typing import List

from justrunalready.utils import run
from justrunalready.inspectors.base import InspectorBase


class MacOSInspector(InspectorBase):
    """macOS Mach-O binary inspector."""

    @property
    def name(self) -> str:
        return "macos"

    def list_needed(self, macho: Path) -> List[str]:
        """List shared libraries needed by a Mach-O binary."""
        r = run(["otool", "-L", str(macho)])
        if r.returncode != 0:
            return []
        deps: List[str] = []
        lines = r.stdout.splitlines()[1:]
        for line in lines:
            line = line.strip()
            if not line:
                continue
            dep = line.split(" ")[0]
            if dep == str(macho):
                continue
            deps.append(dep)
        return deps
