"""Release metadata shared by the application and build tooling."""

APP_VERSION = "4.1.2"
GITHUB_REPOSITORY = "btduy13/TrueTag"


def executable_name(version=APP_VERSION):
    return f"TRUETAG-v{version}.exe"


def installer_name(version=APP_VERSION):
    return f"TrueTag_v{version}_Setup.exe"
