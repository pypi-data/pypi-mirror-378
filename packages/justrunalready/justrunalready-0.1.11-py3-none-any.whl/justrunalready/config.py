from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import tomllib


@dataclass
class AppConfig:
    """Application-level configuration."""

    #: Name of the application used in bundle metadata.
    name: str = "App"
    #: Root directory where the built application is staged before bundling (e.g., CMake install prefix).
    staging_root: Path = Path("install")
    #: Optional bundle identifier (e.g., com.company.app) used for platform-specific packaging.
    bundle: Optional[str] = None

    def __post_init__(self) -> None:
        if isinstance(self.staging_root, str):
            self.staging_root = Path(self.staging_root)


@dataclass
class LinuxLayout:
    """Linux platform-specific bundle layout configuration."""

    #: Output directory for the Linux AppImage bundle structure.
    appdir: Path = Path("AppDir")
    #: Path to the main executable relative to staging_root (e.g., 'bin/myapp').
    binary: str = "bin/app"
    #: Directory for executables within the AppDir bundle (relative to appdir).
    bin_dir: str = "usr/bin"
    #: Directory for shared libraries within the AppDir bundle (relative to appdir).
    lib_dir: str = "usr/lib"
    #: Directories that should preserve their structure for plugins (relative to appdir).
    plugin_dirs: List[str] = field(default_factory=list)
    #: Runtime library search paths to set on executables and libraries.
    rpath: List[str] = field(default_factory=lambda: ["$ORIGIN", "$ORIGIN/../lib"])
    #: Directory for QML modules within the AppDir bundle (relative to appdir).
    qml_dir: str = "usr/qml"

    def __post_init__(self) -> None:
        if isinstance(self.appdir, str):
            self.appdir = Path(self.appdir)


@dataclass
class MacOSLayout:
    """macOS platform-specific bundle layout configuration."""

    #: Path to the .app bundle directory, including the app name and .app extension.
    app_bundle: Path = Path("install/Index.app")
    #: Directory for frameworks and dylibs within the .app bundle (relative to app_bundle).
    frameworks_dir: str = "Contents/Frameworks"
    #: Directory for plugins within the .app bundle (relative to app_bundle), if different from default.
    plugins_dir: Optional[str] = None
    #: Directory for QML modules within the .app bundle (relative to app_bundle).
    qml_dir: str = "Contents/Resources/qml"
    #: Runtime library search paths to set on executables and libraries.
    rpath: List[str] = field(default_factory=lambda: ["@executable_path/../Frameworks"])

    def __post_init__(self) -> None:
        if isinstance(self.app_bundle, str):
            self.app_bundle = Path(self.app_bundle)


@dataclass
class WindowsLayout:
    """Windows platform-specific bundle layout configuration."""

    #: Path to the main executable relative to staging_root (e.g., 'bin/myapp.exe').
    binary: str = "bin/app.exe"
    #: Directory for executables and DLLs in the final bundle (relative to staging_root).
    bin_dir: str = "bin"
    #: Directories that should preserve their structure for plugins (relative to staging_root).
    plugin_dirs: List[str] = field(default_factory=list)
    #: Directory for QML modules in the final bundle (relative to staging_root).
    qml_dir: str = "bin/qml"


@dataclass
class LayoutConfig:
    """Container for platform-specific layout configurations."""

    #: Linux-specific bundle layout settings.
    linux: LinuxLayout = field(default_factory=LinuxLayout)
    #: macOS-specific bundle layout settings.
    macos: MacOSLayout = field(default_factory=MacOSLayout)
    #: Windows-specific bundle layout settings.
    windows: WindowsLayout = field(default_factory=WindowsLayout)


@dataclass
class QtConfig:
    """Qt-specific configuration for bundling Qt applications."""

    #: Path to Qt plugins directory in the staging area (auto-detected if not specified).
    plugins_dir: Optional[Path] = None
    #: Qt plugins to explicitly keep, organized by category (e.g., {'platforms': ['qcocoa']}).
    keep_plugins: Dict[str, List[str]] = field(default_factory=dict)
    #: Qt plugins to explicitly exclude, organized by category (e.g., {'sqldrivers': ['qsqlite']}).
    prune_plugins: Dict[str, List[str]] = field(default_factory=dict)
    #: Root directories to scan for QML imports to determine required QML modules.
    qml_roots: List[Path] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.plugins_dir, str):
            self.plugins_dir = Path(self.plugins_dir)

        self.qml_roots = [Path(p) if isinstance(p, str) else p for p in self.qml_roots]


@dataclass
class Config:
    """Main configuration object containing all bundling settings."""

    #: Raw configuration data as loaded from the TOML file.
    raw: Dict[str, Any]
    #: Path to the configuration file.
    path: Path
    #: Application-level configuration settings.
    app: AppConfig
    #: Platform-specific layout configurations.
    layout: LayoutConfig
    #: Qt-specific bundling configuration.
    qt: QtConfig
    #: List of library name patterns to exclude from bundling (e.g., 'libGL*', 'libc.so*').
    exclude: List[str]

    def get(self, *keys: str, default: Any = None) -> Any:
        cur: Any = self.raw
        for k in keys:
            if not isinstance(cur, dict) or k not in cur:
                return default
            cur = cur[k]
        return cur

    def get_platform_includes(self, platform: str) -> List[str]:
        """Get include patterns for a specific platform.

        Returns patterns from [include.<platform>] section, or empty list if not defined.
        """
        # Get platform-specific includes from [include.<platform>] section
        include_section = self.raw.get("include", {})
        if isinstance(include_section, dict):
            platform_patterns = include_section.get(platform, {}).get("patterns", [])
            return list(platform_patterns)
        return []

    def get_platform_copies(self, platform: str) -> List[Dict[str, str] | str]:
        """Get copy specifications for a specific platform.

        Returns copy specs from [copy.<platform>] section.
        Each spec can be:
        - A string pattern (copies to bundle root)
        - A dict with 'pattern' and 'dest' keys

        Example config:
        [copy.linux]
        files = [
            "myapp.desktop",  # Copy to AppDir root
            { pattern = "share/icons/*.png", dest = "/" },
            { pattern = "docs/*", dest = "usr/share/doc" }
        ]
        """
        copy_section = self.raw.get("copy", {})
        if isinstance(copy_section, dict):
            platform_copies = copy_section.get(platform, {}).get("files", [])
            return list(platform_copies)
        return []


def _parse_app(d: Dict[str, Any]) -> AppConfig:
    return AppConfig(**d)


def _parse_layout(d: Dict[str, Any]) -> LayoutConfig:
    lin = d.get("linux", {})
    mac = d.get("macos", {})
    win = d.get("windows", {})
    return LayoutConfig(
        linux=LinuxLayout(**lin), macos=MacOSLayout(**mac), windows=WindowsLayout(**win)
    )


def _parse_qt(d: Dict[str, Any]) -> QtConfig:
    return QtConfig(**d)


def load_config(path: Path) -> Config:
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    data: Dict[str, Any]
    data = tomllib.loads(path.read_text("utf-8"))
    app = _parse_app(data.get("app", {}))
    layout = _parse_layout(data.get("layout", {}))
    qt = _parse_qt(data.get("qt", {}))

    # Parse exclude patterns
    exclude = list(data.get("exclude", []) or [])

    return Config(raw=data, path=path, app=app, layout=layout, qt=qt, exclude=exclude)
