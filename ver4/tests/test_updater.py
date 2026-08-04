import hashlib
import tempfile
import unittest
from pathlib import Path

from updater import GitHubReleaseUpdater, UpdateError, is_newer_version


class _Response:
    def __init__(self, status_code=200, payload=None, body=b'', text=None):
        self.status_code = status_code
        self._payload = payload
        self._body = body
        self.text = text if text is not None else body.decode('utf-8', errors='replace')
        self.headers = {'Content-Length': str(len(body))}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f'HTTP {self.status_code}')

    def iter_content(self, chunk_size):
        for offset in range(0, len(self._body), chunk_size):
            yield self._body[offset:offset + chunk_size]


class _Session:
    def __init__(self, release_payload, installer=b'installer bytes', checksum=None):
        self.release_payload = release_payload
        self.installer = installer
        self.checksum = checksum or hashlib.sha256(installer).hexdigest()
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if url.endswith('/releases/latest'):
            return _Response(payload=self.release_payload)
        if url.endswith('/checksum'):
            return _Response(text=f'{self.checksum}  TrueTag_v4.1.2_Setup.exe')
        if url.endswith('/installer'):
            return _Response(body=self.installer)
        raise AssertionError(url)


def _release(tag='v4.1.2'):
    return {
        'tag_name': tag,
        'body': 'Release notes',
        'html_url': 'https://github.test/release',
        'assets': [
            {
                'name': 'TrueTag_v4.1.2_Setup.exe',
                'url': 'https://api.github.test/assets/installer',
                'size': len(b'installer bytes'),
                'digest': None,
            },
            {
                'name': 'TrueTag_v4.1.2_Setup.exe.sha256',
                'url': 'https://api.github.test/assets/checksum',
                'size': 64,
            },
        ],
    }


class VersionTests(unittest.TestCase):
    def test_semantic_version_comparison(self):
        self.assertTrue(is_newer_version('v4.1.2', '4.1.1'))
        self.assertFalse(is_newer_version('4.1.1', '4.1.1'))
        self.assertFalse(is_newer_version('4.0.9', '4.1.1'))


class GitHubReleaseUpdaterTests(unittest.TestCase):
    def test_discovers_expected_installer_asset(self):
        session = _Session(_release())
        updater = GitHubReleaseUpdater('4.1.1', session=session, token='')

        release = updater.check_for_update()

        self.assertEqual('4.1.2', release.version)
        self.assertEqual('TrueTag_v4.1.2_Setup.exe', release.asset_name)
        self.assertNotIn('Authorization', session.calls[0][1]['headers'])

    def test_private_repo_token_is_sent_to_github(self):
        session = _Session(_release())
        updater = GitHubReleaseUpdater('4.1.1', session=session, token='private-token')

        updater.check_for_update()

        self.assertEqual('Bearer private-token', session.calls[0][1]['headers']['Authorization'])

    def test_current_version_does_not_offer_update(self):
        updater = GitHubReleaseUpdater('4.1.2', session=_Session(_release()), token='')
        self.assertIsNone(updater.check_for_update())

    def test_download_verifies_checksum(self):
        session = _Session(_release())
        with tempfile.TemporaryDirectory() as directory:
            updater = GitHubReleaseUpdater(
                '4.1.1', session=session, token='', download_dir=Path(directory)
            )
            release = updater.check_for_update()

            path = updater.download_update(release)

            self.assertEqual(b'installer bytes', path.read_bytes())

    def test_download_rejects_bad_checksum(self):
        session = _Session(_release(), checksum='0' * 64)
        with tempfile.TemporaryDirectory() as directory:
            updater = GitHubReleaseUpdater(
                '4.1.1', session=session, token='', download_dir=Path(directory)
            )
            release = updater.check_for_update()

            with self.assertRaises(UpdateError):
                updater.download_update(release)


if __name__ == '__main__':
    unittest.main()
