import unittest
import requests
import os

from assertpy import assert_that
from mock import mock

from framepy import _configuration


class ConfigurationTest(unittest.TestCase):
    def test_loading_properties_from_file(self):
        # given
        file_path = self._find_config_absolute_path()

        # when
        properties = _configuration._load_properties(file_path)

        # then
        assert_that(properties).is_equal_to({'a': 'b', 'c': 'd'})

    def test_loading_properties_from_non_existing_file(self):
        # given
        file_path = 'non_existing_file.ini'

        # when then
        with self.assertRaises(IOError):
            _configuration._load_properties(file_path)

    def test_loading_remote_configuration_without_remote_config_url(self):
        # given
        properties = {
            'app_name': 'app',
        }

        # when
        updated_properties = _configuration._update_with_remote_configuration(properties)

        # then
        assert_that(updated_properties).is_equal_to(properties)

    def test_loading_remote_configuration_without_app_name(self):
        # given
        properties = {
            'remote_config_url': 'http://localhost'
        }

        # when
        updated_properties = _configuration._update_with_remote_configuration(properties)

        # then
        assert_that(updated_properties).is_equal_to(properties)

    @mock.patch('requests.get')
    def test_loading_remote_configuration(self, requests_get):
        # given
        properties = {
            'app_name': 'app',
            'remote_config_url': 'http://localhost'
        }
        requests_get.return_value = self._fake_ok_response_from_service({
            'propertySources': [
                {
                    'source': {
                        'x': 'y'
                    }
                }
            ]
        })

        # when
        updated_properties = _configuration._update_with_remote_configuration(properties)

        # then
        requests_get.assert_called_once_with('http://localhost/app/default')
        assert_that(updated_properties).is_equal_to(
            {
                'x': 'y',
                'app_name': 'app',
                'remote_config_url': 'http://localhost'
            }
        )

    @mock.patch('requests.get')
    def test_loading_remote_configuration_error_response_from_service(self, requests_get):
        # given
        properties = {
            'app_name': 'app',
            'remote_config_url': 'http://localhost'
        }
        requests_get.return_value = self._fake_error_response_from_service()

        # when
        updated_properties = _configuration._update_with_remote_configuration(properties)

        # then
        requests_get.assert_called_once_with('http://localhost/app/default')
        assert_that(updated_properties).is_equal_to(properties)

    @mock.patch('requests.get')
    def test_loading_remote_configuration_error_connecting_to_service(self, requests_get):
        # given
        properties = {
            'app_name': 'app',
            'remote_config_url': 'http://localhost'
        }
        requests_get.side_effect = requests.exceptions.ConnectionError()

        # when
        updated_properties = _configuration._update_with_remote_configuration(properties)

        # then
        requests_get.assert_called_once_with('http://localhost/app/default')
        assert_that(updated_properties).is_equal_to(properties)

    def _fake_ok_response_from_service(self, properties_to_set):
        resp = requests.Response()
        resp.status_code = 200
        resp.json = lambda: properties_to_set
        return resp

    def _fake_error_response_from_service(self):
        resp = requests.Response()
        resp.status_code = 404
        return resp

    def _find_config_absolute_path(self):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config/config.ini')
