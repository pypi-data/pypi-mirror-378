import os
from pathlib import Path

from justrunalready.utils import run
from justrunalready.wrappers import WrapperBase


class AppImageWrapper(WrapperBase):
    name = "appimage"

    def supports(self, platform: str) -> bool:
        return platform.startswith("linux")

    def run(self, cfg) -> str:
        appdir = cfg.layout.linux.appdir
        if not appdir.exists():
            raise RuntimeError(f"AppDir not found: {appdir}")

        tool = os.environ.get("APPIMAGETOOL", "appimagetool")
        r = run(["which", tool])
        if r.returncode != 0:
            raise RuntimeError("appimagetool not found in PATH (set APPIMAGETOOL)")

        name = cfg.app.name
        out = Path(f"{name}-linux-x86_64.AppImage")
        res = run([tool, str(appdir), str(out)])
        if res.returncode != 0:
            raise RuntimeError(res.stderr or res.stdout)
        return str(out)
