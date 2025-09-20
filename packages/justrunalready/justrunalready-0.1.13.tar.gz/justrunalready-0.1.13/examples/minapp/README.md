MinApp — JustRunAlready example
================================

This is a tiny cross‑platform C project to demonstrate bundling with `jra`.

Build
- cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
- cmake --build build
- cmake --install build --prefix install

Bundle
- Linux: jra bundle --config jra.toml --platform linux
- macOS: jra bundle --config jra.toml --platform macos
- Windows: jra bundle --config jra.toml --platform windows

Tips
- Use --dry-run to preview without writing files.
- Use --verbose to print copy/patch operations.
- Use `jra doctor` to check required tools on your platform.

Verify
- jra verify --config jra.toml --platform linux
- jra verify --config jra.toml --platform macos
- jra verify --config jra.toml --platform windows

Outputs
- Linux: AppDir/usr/bin/minapp and libraries under AppDir/usr/lib
- macOS: install/MinApp.app with frameworks under Contents/Frameworks
- Windows: install/bin/minapp.exe and DLLs next to it
