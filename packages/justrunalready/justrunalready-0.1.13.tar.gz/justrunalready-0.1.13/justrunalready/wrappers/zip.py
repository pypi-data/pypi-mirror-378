import shutil
from pathlib import Path

from justrunalready.models import Config
from justrunalready.wrappers import WrapperBase


class ZipWrapper(WrapperBase):
    name = "zip"

    def supports(self, platform: str) -> bool:
        return True

    def run(self, cfg: Config) -> str:
        staging = cfg.app.staging_root
        bin_dir = Path(cfg.layout.windows.bin_dir)
        src = staging / bin_dir
        if not src.exists():
            appdir = cfg.layout.linux.appdir
            if appdir.exists():
                src = appdir
            else:
                app_path = cfg.layout.macos.app_bundle
                if app_path.exists():
                    src = app_path
                else:
                    raise RuntimeError("Nothing to zip: missing bin/appdir/app bundle")
        base = cfg.app.name or "Bundle"
        out = shutil.make_archive(base, "zip", root_dir=str(src))
        return out
