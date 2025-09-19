from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class Dso:
    path: Path
    deps: List[str] = field(default_factory=list)


@dataclass
class Graph:
    nodes: Dict[Path, Dso] = field(default_factory=dict)

    def add(self, d: Dso) -> None:
        self.nodes[d.path] = d

    def __contains__(self, p: Path) -> bool:
        return p in self.nodes

    def paths(self) -> List[Path]:
        return list(self.nodes.keys())
