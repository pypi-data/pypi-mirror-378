from pathlib import Path

from justrunalready.models import Config
from justrunalready.utils import run
from justrunalready.wrappers import WrapperBase


class DmgWrapper(WrapperBase):
    name = "dmg"

    def supports(self, platform: str) -> bool:
        return platform in ("darwin", "mac", "macos")

    def run(self, cfg: Config) -> str:
        app_path = cfg.layout.macos.app_bundle
        if not app_path.exists():
            raise RuntimeError(f"App bundle not found: {app_path}")
        name = cfg.app.name or app_path.stem
        out = Path(f"{name}-macos.dmg")
        res = run(
            [
                "hdiutil",
                "create",
                "-volname",
                name,
                "-srcfolder",
                str(app_path),
                "-ov",
                "-format",
                "UDZO",
                str(out),
            ]
        )
        if res.returncode != 0:
            raise RuntimeError(res.stderr or res.stdout)
        return str(out)
