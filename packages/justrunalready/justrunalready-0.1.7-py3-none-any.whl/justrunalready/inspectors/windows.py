from __future__ import annotations

from pathlib import Path
from typing import List


def list_needed(pe: Path) -> List[str]:
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
        # pefile not available, fall back to dumpbin
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
        # dumpbin not available or failed
        pass

    # Neither pefile nor dumpbin available - can't inspect Windows binaries
    raise RuntimeError(f"Unable to inspect Windows PE file {pe}: neither pefile nor dumpbin available")
