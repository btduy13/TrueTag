"""Interactive smoke test for a built TrueTag installer artifact."""

from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

from pywinauto import Desktop

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from version import APP_VERSION, executable_name  # noqa: E402


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: smoke_release_installer.py <installer.exe>")

    installer = Path(sys.argv[1]).resolve()
    test_root = Path(tempfile.mkdtemp(prefix="truetag-installer-smoke-"))
    environment = os.environ.copy()
    environment["APPDATA"] = str(test_root)
    process = subprocess.Popen([str(installer)], env=environment)

    try:
        window = Desktop(backend="win32").window(title=f"TrueTag v{APP_VERSION} Installer")
        window.wait("visible enabled", timeout=30)
        # ttk child captions are not exposed by Tk's Win32 accessibility
        # bridge, so click the centered button using client coordinates.
        window.click_input(coords=(208, 222))

        success = Desktop(backend="win32").window(title="Success")
        success.wait("visible enabled", timeout=45)
        success.child_window(title="OK").click_input()
        process.wait(timeout=15)

        install_dir = test_root / "TrueTag"
        required = (
            executable_name(),
            "truetag_loader.lsp",
            "truetag_startup.lsp",
            "truetag_menu.mnu",
        )
        missing = [name for name in required if not (install_dir / name).is_file()]
        if missing:
            print(f"INSTALLER_SMOKE=FAIL missing={','.join(missing)}")
            return 1
        print("INSTALLER_SMOKE=PASS")
        return 0
    finally:
        if process.poll() is None:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                capture_output=True,
                check=False,
            )
        shutil.rmtree(test_root, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
