from __future__ import annotations

import re
from pathlib import Path
from typing import List

from justrunalready.utils import run


def list_needed(elf: Path) -> List[str]:
    if run(["which", "readelf"]).returncode == 0:
        r = run(["readelf", "-d", str(elf)])
        if r.returncode == 0:
            deps: List[str] = []
            for line in r.stdout.splitlines():
                m = re.search(r"\(NEEDED\).*Shared library: \[(.*?)\]", line)
                if m:
                    deps.append(m.group(1))
            return deps

    r = run(["ldd", str(elf)])
    deps: List[str] = []
    if r.returncode == 0:
        for line in r.stdout.splitlines():
            m = re.match(r"\s*(\S+)\s*=>\s*(\S+)", line)
            if m:
                path = m.group(2)
                if path != "not" and path != "" and path != "(0x00000000)":
                    deps.append(path)
                else:
                    deps.append(m.group(1))
    return deps
