"""Pydantic models for configuration validation."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AppConfig(BaseModel):
    """Application configuration."""

    name: str = Field(description="Application name")
    staging_root: Path = Field(description="Root directory for staging files")

    @field_validator("staging_root", mode="before")
    @classmethod
    def resolve_staging_root(cls, v: Union[str, Path]) -> Path:
        """Resolve staging root to absolute path."""
        return Path(v).resolve()


class LinuxLayoutConfig(BaseModel):
    """Linux platform layout configuration."""

    appdir: Path = Field(default=Path("AppDir"), description="AppDir root directory")
    bin_dir: Path = Field(default=Path("usr/bin"), description="Binary directory")
    lib_dir: Path = Field(default=Path("usr/lib"), description="Library directory")
    binary: Path = Field(description="Main binary name")
    rpath: Optional[List[str]] = Field(
        default=None, description="Runtime library search paths"
    )


class WindowsLayoutConfig(BaseModel):
    """Windows platform layout configuration."""

    bin_dir: Path = Field(default=Path("."), description="Binary directory")
    lib_dir: Path = Field(default=Path("."), description="Library directory")
    binary: Path = Field(description="Main binary name with .exe extension")


class MacOSLayoutConfig(BaseModel):
    """macOS platform layout configuration."""

    app_bundle: Path = Field(description="App bundle directory (e.g., MyApp.app)")
    bin_dir: Path = Field(
        default=Path("Contents/MacOS"), description="Binary directory within app bundle"
    )
    lib_dir: Path = Field(
        default=Path("Contents/Frameworks"), description="Framework/library directory"
    )
    binary: Optional[Path] = Field(
        default=None, description="Main binary name (auto-detected if not specified)"
    )
    rpath: Optional[List[str]] = Field(
        default=None, description="Runtime library search paths"
    )


class LayoutConfig(BaseModel):
    """Platform layouts configuration."""

    linux: Optional[LinuxLayoutConfig] = None
    windows: Optional[WindowsLayoutConfig] = None
    macos: Optional[MacOSLayoutConfig] = None


class IncludeConfig(BaseModel):
    """Include patterns configuration."""

    model_config = ConfigDict(extra="allow")


class CopyConfig(BaseModel):
    """Copy configuration."""

    model_config = ConfigDict(extra="allow")


class Config(BaseModel):
    """Main configuration model."""

    model_config = ConfigDict(populate_by_name=True)

    app: AppConfig
    layout: LayoutConfig
    exclude: List[str] = Field(
        default_factory=list, description="Global exclusion patterns"
    )
    include: Optional[IncludeConfig] = None
    copy_config: Optional[CopyConfig] = Field(default=None, alias="copy")
    plugins: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Plugin configurations"
    )

    def get_platform_excludes(self, platform: str) -> List[str]:
        """Get exclude patterns for a platform.

        For now, just returns the global exclude list.
        Could be extended to support platform-specific excludes.
        """
        return self.exclude

    def get_platform_includes(self, platform: str) -> List[str]:
        """Get include patterns for a platform.

        Returns patterns from [include.<platform>].patterns
        """
        if not self.include:
            return []

        platform_data = getattr(self.include, platform, None)
        if platform_data and isinstance(platform_data, dict):
            return platform_data.get("patterns", [])
        return []

    def get_platform_copies(self, platform: str) -> List[Union[str, Dict[str, Any]]]:
        """Get copy rules for a platform.

        Returns copy specs from [copy.<platform>].files
        """
        if not self.copy_config:
            return []

        platform_data = getattr(self.copy_config, platform, None)
        if platform_data and isinstance(platform_data, dict):
            return platform_data.get("files", [])
        return []
