import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

from license_generator import LicenseGenerator
from licensing_manager import LicensingManager
from license_manager_ui import _default_data_dir
import license_server_api


class _Response:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class _ActivationSession:
    def __init__(self):
        self.urls = []

    def post(self, url, **kwargs):
        self.urls.append(url)
        if url.endswith('/api/activate'):
            return _Response(200, {'success': True, 'message': 'activated'})
        return _Response(200, {
            'valid': True,
            'message': 'validated',
            'license_info': {
                'expiry_date': (datetime.now() + timedelta(days=30)).isoformat(),
                'features': ['basic_scripts'],
            },
        })


class _OfflineSession:
    def post(self, *args, **kwargs):
        raise OSError('server unavailable')


class LicenseGeneratorRegressionTests(unittest.TestCase):
    def test_bound_machine_remains_valid_at_activation_limit(self):
        with tempfile.TemporaryDirectory() as data_dir:
            generator = LicenseGenerator(data_dir)
            created, _, license_data = generator.create_license(
                'basic', {'name': 'QA'}, custom_duration=30
            )
            self.assertTrue(created)
            license_key = license_data['license_key']
            self.assertTrue(generator.activate_license(license_key, 'QA-MACHINE')[0])

            valid, message, _ = generator.validate_license(license_key, 'QA-MACHINE')

            self.assertTrue(valid, message)

    def test_integrity_is_checked_before_bound_machine_is_trusted(self):
        with tempfile.TemporaryDirectory() as data_dir:
            generator = LicenseGenerator(data_dir)
            _, _, license_data = generator.create_license('basic', custom_duration=30)
            license_key = license_data['license_key']
            self.assertTrue(generator.activate_license(license_key, 'QA-MACHINE')[0])
            generator.license_db['licenses'][license_key]['checksum'] = 'tampered'

            valid, message, _ = generator.validate_license(license_key, 'QA-MACHINE')

            self.assertFalse(valid)
            self.assertEqual('License integrity check failed', message)

    def test_revoke_and_unrevoke_lifecycle(self):
        with tempfile.TemporaryDirectory() as data_dir:
            generator = LicenseGenerator(data_dir)
            _, _, license_data = generator.create_license('professional', custom_duration=30)
            license_key = license_data['license_key']
            self.assertTrue(generator.revoke_license(license_key, 'QA', 'tester')[0])
            self.assertFalse(generator.validate_license(license_key, 'QA-MACHINE')[0])
            self.assertTrue(generator.unrevoke_license(license_key, 'tester', 'QA restore')[0])
            self.assertTrue(generator.validate_license(license_key, 'QA-MACHINE')[0])

    def test_expired_license_cannot_be_unrevoked(self):
        with tempfile.TemporaryDirectory() as data_dir:
            generator = LicenseGenerator(data_dir)
            _, _, license_data = generator.create_license('basic', custom_duration=30)
            license_key = license_data['license_key']
            generator.license_db['licenses'][license_key]['expiry_date'] = (
                datetime.now() - timedelta(days=1)
            ).isoformat()
            generator.license_db['licenses'][license_key]['checksum'] = (
                generator._calculate_license_checksum(generator.license_db['licenses'][license_key])
            )
            self.assertTrue(generator.revoke_license(license_key, 'expired QA', 'tester')[0])
            restored, message = generator.unrevoke_license(license_key, 'tester', 'QA restore')
            self.assertFalse(restored)
            self.assertEqual('Cannot unrevoke expired license', message)


class ClientActivationRegressionTests(unittest.TestCase):
    def _client(self, session, enabled=True):
        client = LicensingManager.__new__(LicensingManager)
        client.config = {
            'enable_server_validation': enabled,
            'license_server': 'http://qa-server:5000',
            'server_timeout': 1,
            'version': '4.1.1',
            'features': {'basic_scripts': True},
        }
        client._get_machine_id = lambda: 'QA-MACHINE'
        client._session = session
        return client

    def test_activation_is_recorded_before_validation(self):
        session = _ActivationSession()
        result = self._client(session)._validate_license_with_server(
            'TRUETAG-AAAA-BBBB-CCCC-DDDD-EEEE'
        )

        self.assertTrue(result['valid'])
        self.assertEqual(
            ['http://qa-server:5000/api/activate', 'http://qa-server:5000/api/validate'],
            session.urls,
        )

    def test_unverified_key_is_rejected_when_server_is_offline(self):
        result = self._client(_OfflineSession())._validate_license_with_server(
            'TRUETAG-FAKE-FAKE-FAKE-FAKE-FAKE'
        )

        self.assertFalse(result['valid'])
        self.assertIn('requires an online validation', result['message'])

    def test_unverified_key_is_rejected_when_server_validation_is_disabled(self):
        result = self._client(_ActivationSession(), enabled=False)._validate_license_with_server(
            'TRUETAG-FAKE-FAKE-FAKE-FAKE-FAKE'
        )

        self.assertFalse(result['valid'])


class ExpiryRegressionTests(unittest.TestCase):
    def _manager(self, data_dir, days_ago):
        manager = LicensingManager.__new__(LicensingManager)
        manager.data_dir = data_dir
        manager.license_file = os.path.join(data_dir, 'license.json')
        manager.config = {
            'version': '4.1.1',
            'grace_period_days': 7,
            'features': {'basic_scripts': True, 'csv_import': True},
            'enable_server_validation': False,
        }
        manager._get_machine_id = lambda: 'QA-MACHINE'
        manager._load_trial_from_registry = lambda: None
        manager._check_license_revoked_status = lambda key: (False, '')
        manager.license_data = {
            'status': 'licensed',
            'license_key': 'TRUETAG-TEST-TEST-TEST-TEST-TEST',
            'activation_date': '',
            'expiry_date': (datetime.now() - timedelta(days=days_ago)).isoformat(),
            'machine_id': 'QA-MACHINE',
            'features': {'basic_scripts': True, 'csv_import': True},
            'trial_used': True,
            'last_check': '',
            'checksum': '',
        }
        manager.license_data['checksum'] = manager._calculate_checksum(manager.license_data)
        Path(manager.license_file).write_text(
            json.dumps(manager.license_data), encoding='utf-8'
        )
        return manager

    def test_license_remains_valid_during_grace_period(self):
        with tempfile.TemporaryDirectory() as data_dir:
            manager = self._manager(data_dir, days_ago=2)
            valid, message = manager.is_license_valid()
            self.assertTrue(valid)
            self.assertIn('grace period', message)

    def test_all_features_are_blocked_after_grace_period(self):
        with tempfile.TemporaryDirectory() as data_dir:
            manager = self._manager(data_dir, days_ago=8)
            self.assertFalse(manager.is_license_valid()[0])
            self.assertFalse(manager.is_feature_enabled('basic_scripts'))
            self.assertFalse(manager.is_feature_enabled('csv_import'))


class FrozenBuildRegressionTests(unittest.TestCase):
    def test_license_manager_uses_executable_directory_when_frozen(self):
        fake_executable = os.path.join('C:\\Program Files', 'TrueTag', 'LicenseManager.exe')
        with mock.patch.object(sys, 'frozen', True, create=True), mock.patch.object(
            sys, 'executable', fake_executable
        ):
            self.assertEqual(os.path.dirname(fake_executable), _default_data_dir())


class LicenseServerApiIntegrationTests(unittest.TestCase):
    def test_activate_then_validate_same_machine(self):
        with tempfile.TemporaryDirectory() as data_dir:
            generator = LicenseGenerator(data_dir)
            _, _, license_data = generator.create_license('basic', custom_duration=30)
            previous_generator = license_server_api.generator
            license_server_api.generator = generator
            try:
                client = license_server_api.app.test_client()
                activation = client.post('/api/activate', json={
                    'license_key': license_data['license_key'],
                    'machine_id': 'QA-MACHINE',
                    'customer_name': 'QA',
                })
                validation = client.post('/api/validate', json={
                    'license_key': license_data['license_key'],
                    'machine_id': 'QA-MACHINE',
                    'version': '4.1.1',
                })
            finally:
                license_server_api.generator = previous_generator

            self.assertEqual(200, activation.status_code, activation.get_json())
            self.assertEqual(200, validation.status_code, validation.get_json())
            self.assertTrue(validation.get_json()['valid'])


if __name__ == '__main__':
    unittest.main()
