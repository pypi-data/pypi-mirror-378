from __future__ import annotations

from typing import Any


def print_dependency_graph(cfg: Any) -> int:
    seeds = cfg.get("include", default=[]) or []
    print("Seeds:")
    for s in seeds:
        print(f" - {s}")
    return 0
