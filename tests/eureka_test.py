import unittest
from unittest import mock
import requests

from assertpy import assert_that

from framepy import eureka


class EurekaTest(unittest.TestCase):
    @mock.patch('threading.Thread')
    @mock.patch('framepy.eureka._get_session_from_cache')
    def test_eureka_should_be_initialized(self, get_session, thread_class):
        # given
        properties = {
            'app_name': 'sample_app',
            'remote_config_url': 'http://localhost',
            'public_hostname': 'localhost'
        }
        module = eureka.Module()
        beans = {}

        session = get_session.return_value
        session.post.return_value = self._fake_ok_response()

        thread = thread_class.return_value

        # when
        module.before_setup(properties, {}, beans)

        # then
        assert_that('_eureka_url' in beans).is_true()
        assert_that(beans['_eureka_url']).is_equal_to('http://localhost/eureka')
        thread.start.assert_called_once_with()

    def _fake_ok_response(self):
        response = requests.Response()
        response.status_code = 200
        return response
