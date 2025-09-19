from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import tomllib


@dataclass
class AppConfig:
    name: str = "App"
    staging_root: Path = Path("install")
    binary: str = "bin/app"
    bundle: Optional[str] = None

    def __post_init__(self) -> None:
        if isinstance(self.staging_root, str):
            self.staging_root = Path(self.staging_root)


@dataclass
class LinuxLayout:
    appdir: Path = Path("AppDir")
    bin_dir: str = "usr/bin"
    lib_dir: str = "usr/lib"
    plugin_dirs: List[str] = field(default_factory=list)
    rpath: List[str] = field(default_factory=lambda: ["$ORIGIN", "$ORIGIN/../lib"])
    qml_dir: str = "usr/qml"

    def __post_init__(self) -> None:
        if isinstance(self.appdir, str):
            self.appdir = Path(self.appdir)


@dataclass
class MacOSLayout:
    app_bundle: Path = Path("install/Index.app")
    frameworks_dir: str = "Contents/Frameworks"
    plugins_dir: Optional[str] = None
    qml_dir: str = "Contents/Resources/qml"
    rpath: List[str] = field(default_factory=lambda: ["@executable_path/../Frameworks"])

    def __post_init__(self) -> None:
        if isinstance(self.app_bundle, str):
            self.app_bundle = Path(self.app_bundle)


@dataclass
class WindowsLayout:
    bin_dir: str = "bin"
    plugin_dirs: List[str] = field(default_factory=list)
    qml_dir: str = "bin/qml"


@dataclass
class LayoutConfig:
    linux: LinuxLayout = field(default_factory=LinuxLayout)
    macos: MacOSLayout = field(default_factory=MacOSLayout)
    windows: WindowsLayout = field(default_factory=WindowsLayout)


@dataclass
class QtConfig:
    plugins_dir: Optional[Path] = None
    keep_plugins: Dict[str, List[str]] = field(default_factory=dict)
    prune_plugins: Dict[str, List[str]] = field(default_factory=dict)
    qml_roots: List[Path] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.plugins_dir, str):
            self.plugins_dir = Path(self.plugins_dir)

        self.qml_roots = [Path(p) if isinstance(p, str) else p for p in self.qml_roots]


@dataclass
class Config:
    raw: Dict[str, Any]
    path: Path
    app: AppConfig
    layout: LayoutConfig
    qt: QtConfig
    exclude: List[str]

    def get(self, *keys: str, default: Any = None) -> Any:
        cur: Any = self.raw
        for k in keys:
            if not isinstance(cur, dict) or k not in cur:
                return default
            cur = cur[k]
        return cur


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
    exclude = list(data.get("exclude", []) or [])
    return Config(raw=data, path=path, app=app, layout=layout, qt=qt, exclude=exclude)
