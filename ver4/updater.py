"""GitHub Releases updater for public and private TrueTag repositories."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import requests

from version import APP_VERSION, GITHUB_REPOSITORY, installer_name


class UpdateError(RuntimeError):
    """Raised when release metadata or an update artifact is invalid."""


@dataclass(frozen=True)
class ReleaseInfo:
    version: str
    tag_name: str
    notes: str
    html_url: str
    asset_name: str
    asset_api_url: str
    asset_size: int
    checksum_api_url: Optional[str]
    asset_digest: Optional[str]


def _version_tuple(value: str):
    numbers = [int(part) for part in re.findall(r"\d+", value)]
    return tuple((numbers + [0, 0, 0])[:3])


def is_newer_version(candidate: str, current: str) -> bool:
    return _version_tuple(candidate) > _version_tuple(current)


class GitHubReleaseUpdater:
    def __init__(
        self,
        current_version: str = APP_VERSION,
        repository: str = GITHUB_REPOSITORY,
        session=None,
        token: Optional[str] = None,
        download_dir: Optional[Path] = None,
    ):
        self.current_version = current_version
        self.repository = os.getenv("TRUETAG_GITHUB_REPO", repository)
        self.session = session or requests.Session()
        self.token = token if token is not None else self._discover_token()
        self.download_dir = Path(download_dir) if download_dir else self._default_download_dir()

    @staticmethod
    def _default_download_dir() -> Path:
        base = os.getenv("LOCALAPPDATA") or tempfile.gettempdir()
        return Path(base) / "TrueTag" / "updates"

    @staticmethod
    def _discover_token() -> Optional[str]:
        for name in ("TRUETAG_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
            token = os.getenv(name, "").strip()
            if token:
                return token

        gh = shutil.which("gh")
        if not gh:
            return None
        try:
            startupinfo = None
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(
                [gh, "auth", "token"],
                capture_output=True,
                text=True,
                timeout=5,
                startupinfo=startupinfo,
            )
            token = result.stdout.strip()
            return token if result.returncode == 0 and token else None
        except Exception:
            return None

    def _headers(self, binary=False):
        headers = {
            "Accept": "application/octet-stream" if binary else "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": f"TrueTag/{self.current_version}",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def check_for_update(self) -> Optional[ReleaseInfo]:
        url = f"https://api.github.com/repos/{self.repository}/releases/latest"
        try:
            response = self.session.get(url, headers=self._headers(), timeout=10)
        except Exception as exc:
            raise UpdateError(f"Cannot contact GitHub Releases: {exc}") from exc

        if response.status_code in (401, 403, 404):
            hint = " Set TRUETAG_GITHUB_TOKEN or authenticate with gh for a private repository."
            raise UpdateError(f"GitHub release is not accessible (HTTP {response.status_code}).{hint}")
        try:
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            raise UpdateError(f"Invalid GitHub release response: {exc}") from exc

        tag_name = payload.get("tag_name", "")
        version = tag_name.lstrip("vV")
        if not version or not is_newer_version(version, self.current_version):
            return None

        assets = payload.get("assets", [])
        expected_name = installer_name(version)
        asset = next((item for item in assets if item.get("name") == expected_name), None)
        if asset is None:
            asset = next((item for item in assets if item.get("name", "").endswith("_Setup.exe")), None)
        if asset is None:
            raise UpdateError(f"Release {tag_name} does not contain a TrueTag installer asset")

        checksum_name = f"{asset['name']}.sha256"
        checksum_asset = next((item for item in assets if item.get("name") == checksum_name), None)
        return ReleaseInfo(
            version=version,
            tag_name=tag_name,
            notes=payload.get("body", ""),
            html_url=payload.get("html_url", ""),
            asset_name=asset["name"],
            asset_api_url=asset["url"],
            asset_size=int(asset.get("size", 0)),
            checksum_api_url=checksum_asset.get("url") if checksum_asset else None,
            asset_digest=asset.get("digest"),
        )

    def _expected_sha256(self, release: ReleaseInfo) -> str:
        if release.checksum_api_url:
            response = self.session.get(
                release.checksum_api_url,
                headers=self._headers(binary=True),
                timeout=15,
                allow_redirects=True,
            )
            response.raise_for_status()
            checksum = response.text.strip().split()[0].lower()
            if re.fullmatch(r"[0-9a-f]{64}", checksum):
                return checksum

        digest = (release.asset_digest or "").lower()
        if digest.startswith("sha256:") and re.fullmatch(r"[0-9a-f]{64}", digest[7:]):
            return digest[7:]
        raise UpdateError("Release installer has no valid SHA-256 checksum")

    def download_update(
        self,
        release: ReleaseInfo,
        progress: Optional[Callable[[int, int], None]] = None,
    ) -> Path:
        self.download_dir.mkdir(parents=True, exist_ok=True)
        destination = self.download_dir / release.asset_name
        partial = destination.with_suffix(destination.suffix + ".part")
        expected_sha256 = self._expected_sha256(release)

        try:
            response = self.session.get(
                release.asset_api_url,
                headers=self._headers(binary=True),
                timeout=60,
                stream=True,
                allow_redirects=True,
            )
            response.raise_for_status()
            total = int(response.headers.get("Content-Length") or release.asset_size or 0)
            downloaded = 0
            digest = hashlib.sha256()
            with partial.open("wb") as output:
                for chunk in response.iter_content(chunk_size=1024 * 256):
                    if not chunk:
                        continue
                    output.write(chunk)
                    digest.update(chunk)
                    downloaded += len(chunk)
                    if progress:
                        progress(downloaded, total)

            if digest.hexdigest().lower() != expected_sha256:
                raise UpdateError("Downloaded installer failed SHA-256 verification")
            partial.replace(destination)
            return destination
        except Exception:
            partial.unlink(missing_ok=True)
            raise

    @staticmethod
    def launch_installer(path: Path):
        creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        subprocess.Popen([str(path)], close_fds=True, creationflags=creationflags)
