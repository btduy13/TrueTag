"""Prepare the versioned application binary for the installer build.

The maintained installer templates live in ``TrueTag_Setup``.  Keeping those
files as the single source of truth prevents this helper from regenerating an
older, interactive PowerShell installer during a release build.
"""

from pathlib import Path
import shutil

from version import APP_VERSION, executable_name


def create_installer() -> bool:
    base_dir = Path(__file__).resolve().parent
    executable = base_dir / "dist" / executable_name()
    setup_dir = base_dir / "TrueTag_Setup"
    required_templates = (
        "install_plugin.ps1",
        "truetag_loader.lsp",
        "truetag_menu.mnu",
        "truetag_startup.lsp",
    )

    print(f"Preparing TrueTag v{APP_VERSION} installer payload...")
    if not executable.is_file():
        print(f"ERROR: application executable not found: {executable}")
        print("Run build_auto.bat first.")
        return False

    missing = [name for name in required_templates if not (setup_dir / name).is_file()]
    if missing:
        print(f"ERROR: missing installer templates: {', '.join(missing)}")
        return False

    setup_dir.mkdir(parents=True, exist_ok=True)
    destination = setup_dir / executable.name
    shutil.copy2(executable, destination)
    print(f"Installer payload ready: {destination}")
    return True


if __name__ == "__main__":
    raise SystemExit(0 if create_installer() else 1)
