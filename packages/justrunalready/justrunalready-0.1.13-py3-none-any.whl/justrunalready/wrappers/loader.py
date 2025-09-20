from __future__ import annotations

from importlib.metadata import entry_points
from typing import Dict

from justrunalready.wrappers import WrapperBase


def load_wrappers() -> Dict[str, WrapperBase]:
    out: Dict[str, WrapperBase] = {}
    for ep in entry_points(group="justrunalready.wrappers"):
        try:
            cls = ep.load()
            inst = cls()
            out[getattr(inst, "name", ep.name)] = inst
        except Exception as e:
            print(f"Warning: Failed to load wrapper {ep.name}: {e}")
            continue
    return out
