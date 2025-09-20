"""Configuration loading using Pydantic models."""

import tomllib
from pathlib import Path

from justrunalready.models import Config


def load_config(path: Path) -> Config:
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    with open(path, "rb") as f:
        data = tomllib.load(f)

    return Config(**data)
