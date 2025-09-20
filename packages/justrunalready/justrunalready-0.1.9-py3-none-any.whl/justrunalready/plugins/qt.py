from typing import Iterable, List, Optional, Dict
from pathlib import Path

from justrunalready.utils import run
from justrunalready.plugins import PluginBase
from justrunalready.config import Config


class QtPlugin(PluginBase):
    name = "qt"

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.plugins_root: Optional[Path] = self._discover_plugins_root()

    def _discover_plugins_root(self) -> Optional[Path]:
        p = self.cfg.qt.plugins_dir
        if p:
            return p if p.exists() else None

        for exe in ("qtpaths6", "qtpaths"):
            r = run([exe, "--query", "QT_INSTALL_PLUGINS"])
            if r.returncode == 0 and r.stdout.strip():
                pp = Path(r.stdout.strip())
                if pp.exists():
                    return pp

        for exe in ("qmake6", "qmake"):
            r = run([exe, "-query", "QT_INSTALL_PLUGINS"])
            if r.returncode == 0 and r.stdout.strip():
                pp = Path(r.stdout.strip())
                if pp.exists():
                    return pp
        return None

    def _ext(self) -> str:
        import sys

        if sys.platform.startswith("linux"):
            return ".so"
        if sys.platform == "darwin":
            return ".dylib"
        return ".dll"

    def seeds(self, *, stage_root: str) -> Iterable[str]:
        include: List[str] = []

        plugin_dirs = list(self.cfg.layout.linux.plugin_dirs)
        plugin_dirs += list(self.cfg.layout.windows.plugin_dirs)
        mac_plugins_dir = self.cfg.layout.macos.plugins_dir
        if mac_plugins_dir:
            plugin_dirs.append(mac_plugins_dir)
        for d in plugin_dirs:
            include.append(f"{d}/*")

        root = (
            self.plugins_root.resolve()
            if self.plugins_root and not self.plugins_root.is_absolute()
            else self.plugins_root
        )
        if root:
            keep = self.cfg.qt.keep_plugins or {}
            ext = self._ext()
            for cat, names in keep.items():
                if not names:
                    include.append(str(root / cat / f"*{ext}"))
                else:
                    for n in names:
                        include.append(str(root / cat / f"*{n}*{ext}"))
        return include

    def prune_patterns(self) -> Iterable[str]:
        prunes: List[str] = []
        prune = self.cfg.qt.prune_plugins or {}
        if self.plugins_root:
            root = (
                self.plugins_root.resolve()
                if not self.plugins_root.is_absolute()
                else self.plugins_root
            ).as_posix()
            for cat, names in prune.items():
                for n in names:
                    prunes.append(rf"^{root}/{cat}/.*{n}.*")
        return prunes

    def _classify_plugin(self, path: Path) -> Optional[str]:
        """If path is a Qt plugin under plugins_root, return its category name."""
        if not self.plugins_root:
            return None
        try:
            rel = path.resolve().relative_to(self.plugins_root.resolve())
        except (ValueError, OSError):
            # Path is not relative to plugins_root or cannot be resolved
            return None
        parts = rel.parts
        if not parts:
            return None
        return parts[0]

    def organize_files(self, files: Dict[Path, Path]) -> Dict[Path, Path]:
        """Organize Qt plugin and QML files."""
        import sys

        # Get plugin and QML directories for the current platform
        plugin_dirs = []
        qml_dir = None
        if sys.platform.startswith("linux"):
            plugin_dirs = list(self.cfg.layout.linux.plugin_dirs or [])
            qml_dir = Path(self.cfg.layout.linux.qml_dir)
        elif sys.platform == "darwin":
            if self.cfg.layout.macos.plugins_dir:
                plugin_dirs = [self.cfg.layout.macos.plugins_dir]
            qml_dir = Path(self.cfg.layout.macos.qml_dir)
        elif sys.platform.startswith("win"):
            plugin_dirs = list(self.cfg.layout.windows.plugin_dirs or [])
            qml_dir = Path(self.cfg.layout.windows.qml_dir)

        result = {}
        qml_roots = self._qml_roots(str(self.cfg.app.staging_root))

        for src, dest in files.items():
            # Check if this file is a Qt plugin that needs categorization
            category = self._classify_plugin(src)
            if category and plugin_dirs:
                # Find the app root (first component of dest path after stripping absolute path marker)
                # For Linux: AppDir/usr/lib/file -> AppDir is the root
                dest_parts = dest.parts
                app_root_idx = 0
                for i, part in enumerate(dest_parts):
                    if part in ("AppDir", "Contents", "install"):
                        app_root_idx = i
                        break

                # Rebuild path with plugin directory structure
                if app_root_idx < len(dest_parts):
                    app_root = Path(*dest_parts[: app_root_idx + 1])
                    plugin_dir = Path(plugin_dirs[0])
                    new_dest = app_root / plugin_dir / category / src.name
                    result[src] = new_dest
                else:
                    result[src] = dest
            else:
                # Check if this is a QML file that needs special placement
                is_qml_file = False
                for qml_root in qml_roots:
                    try:
                        rel = src.relative_to(qml_root)
                        # This is a QML file - place it in the QML directory
                        if qml_dir:
                            dest_parts = dest.parts
                            app_root_idx = 0
                            for i, part in enumerate(dest_parts):
                                if part in ("AppDir", "Contents", "install"):
                                    app_root_idx = i
                                    break
                            if app_root_idx < len(dest_parts):
                                app_root = Path(*dest_parts[: app_root_idx + 1])
                                result[src] = app_root / qml_dir / rel
                            else:
                                result[src] = dest
                        else:
                            result[src] = dest
                        is_qml_file = True
                        break
                    except ValueError:
                        continue

                if not is_qml_file:
                    result[src] = dest

        return result

    def _qml_roots(self, stage_root: str) -> List[Path]:
        roots = [str(p) for p in (self.cfg.qt.qml_roots or [])]
        root_paths: List[Path] = []
        base = Path(stage_root)
        for r in roots:
            p = Path(r)
            if not p.is_absolute():
                p = base / p
            root_paths.append(p)
        return root_paths

    def asset_seeds(self, *, stage_root: str) -> Iterable[str]:
        pats: List[str] = []
        for r in self._qml_roots(stage_root):
            pats.append(str(r / "**/*"))
        return pats
