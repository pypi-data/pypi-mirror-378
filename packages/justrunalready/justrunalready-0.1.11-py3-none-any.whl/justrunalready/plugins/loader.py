from __future__ import annotations

from importlib.metadata import entry_points
from typing import List

from justrunalready.plugins import PluginBase


def load_plugins(cfg) -> List[PluginBase]:
    plugins: List[PluginBase] = []
    eps = entry_points(group="justrunalready.plugins")
    for ep in eps:
        try:
            cls = ep.load()
            plugins.append(cls(cfg))
        except Exception as e:
            # Log plugin load failure but continue with other plugins
            print(f"Warning: Failed to load plugin {ep.name}: {e}")
            continue
    return plugins
