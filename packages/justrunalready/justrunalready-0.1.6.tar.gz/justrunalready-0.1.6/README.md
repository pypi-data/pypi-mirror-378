<div align="center">
  <img src="logo.png" alt="JRA Logo" width="200"/>
</div>

# JustRunAlready — Cross‑Platform App Bundler

Minimal, predictable bundler that stages your built app into a runnable bundle
across Linux, macOS, and Windows. It discovers dependencies, copies what you
ship, patches load paths (RPATH/@rpath/PE), and places assets consistently.
One CLI and one config on every platform.

## Features
- Single CLI and TOML config for Linux/macOS/Windows
- Dependency closure for ELF/Mach‑O/PE (patchelf/install_name_tool aware)
- Canonical layouts (AppDir on Linux, .app on macOS, flat on Windows)

## Examples

Basic example:
```toml
[app]
name = "MyApp"
staging_root = "install"

[layout.linux]
appdir = "AppDir"
binary = "bin/myapp"
bin_dir = "usr/bin"
lib_dir = "usr/lib"
rpath = ["$ORIGIN", "$ORIGIN/../lib"]

[layout.macos]
app_bundle = "install/MyApp.app"
frameworks_dir = "Contents/Frameworks"
rpath = ["@executable_path/../Frameworks"]

[layout.windows]
binary = "bin/myapp.exe"
bin_dir = "bin"

# Platform-specific include patterns
[include.linux]
patterns = ["lib/*.so"]

[include.macos]
patterns = ["lib/*.dylib"]

[include.windows]
patterns = ["bin/*.dll"]
```

Qt Example (plugins + QML)
```toml
[app]
name = "Index"
staging_root = "install"

[layout.linux]
appdir = "AppDir"
binary = "bin/index"
bin_dir = "usr/bin"
lib_dir = "usr/lib"
plugin_dirs = ["usr/bin/plugins/index"]
qml_dir = "usr/qml"
rpath = ["$ORIGIN", "$ORIGIN/../lib", "$ORIGIN/plugins/index"]

[layout.macos]
app_bundle = "install/Index.app"
frameworks_dir = "Contents/Frameworks"
plugins_dir = "Contents/PlugIns/index"
qml_dir = "Contents/Resources/qml"
rpath = ["@executable_path/../Frameworks"]

[layout.windows]
binary = "bin/index.exe"
bin_dir = "bin"
plugin_dirs = ["bin/plugins/index"]
qml_dir = "bin/qml"

[qt]
plugins_dir = "/opt/Qt/6.7.3/gcc_64/plugins"

[qt.keep_plugins]
platforms = ["xcb", "cocoa", "windows"]
sqldrivers = ["sqlite"]

[qt.prune_plugins]
sqldrivers = ["odbc", "psql", "mimer"]

[include.linux]
patterns = ["bin/plugins/index/*"]

[include.windows]
patterns = ["bin/plugins/index/*"]
```

## CLI

Bundle up your built project:

```
jra bundle --config jra.toml [--platform auto|linux|macos|windows] [--dry-run] [--verbose]
```

(Optionally) verify nothing is missing:
```
jra verify --config jra.toml [--platform linux|macos|windows]
```

## Configuration

### Platform-Specific Binary

Each platform specifies its own binary location:

```toml
[layout.linux]
binary = "bin/myapp"        # Linux executable

[layout.windows]
binary = "bin/myapp.exe"    # Windows executable with .exe

# macOS uses app_bundle instead
[layout.macos]
app_bundle = "install/MyApp.app"
```

### Include Patterns with Exclusions

Use platform-specific include patterns to control which files are bundled. Patterns starting with `!` exclude previously matched files:

```toml
[include.linux]
patterns = [
    "lib/*.so",           # Include all .so files
    "!lib/*_debug.so",    # But exclude debug libraries
    "!lib/*_test.so"      # And test libraries
]
```

### Copy Mappings

Copy non-library files to specific locations in the bundle:

```toml
[copy.linux]
files = [
    # Simple pattern - copies to bundle root
    "myapp.desktop",
    "myapp.png",

    # Mapped pattern - copies to specific destination
    { pattern = "share/icons/*.png", dest = "usr/share/icons" },
    { pattern = "docs/*", dest = "usr/share/doc" }
]
```

This is particularly useful for Linux AppImage bundles that require `.desktop` files in the AppDir root.
