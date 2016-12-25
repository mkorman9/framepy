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
        session.post.return_value = self._fake_ok_response('')

        thread = thread_class.return_value

        # when
        module.before_setup(properties, {}, beans)

        # then
        assert_that('_eureka_url' in beans).is_true()
        assert_that(beans['_eureka_url']).is_equal_to('http://localhost/eureka')
        thread.start.assert_called_once_with()

    @mock.patch('framepy.eureka._get_session_from_cache')
    def test_should_list_instances(self, get_session_from_cache):
        # given
        context = mock.MagicMock()
        service_name = 'some_service'

        service_response = b'{"application": {"instance":[{"hostName":"localhost", "port":{"$":8080}}]}}'
        session = get_session_from_cache.return_value
        session.get.return_value = self._fake_ok_response(service_response)

        # when
        instances = eureka.list_instances(context, service_name)

        # then
        assert_that(instances).is_equal_to(['localhost:8080'])

    @mock.patch('framepy.eureka._get_session_from_cache')
    def test_should_throw_exeception_if_cannot_find_service(self, get_session_from_cache):
        # given
        context = mock.MagicMock()
        service_name = 'some_service'

        session = get_session_from_cache.return_value
        session.get.return_value = self._fake_not_ok_response()

        # when then
        with self.assertRaises(Exception):
            eureka.list_instances(context, service_name)

    def _fake_ok_response(self, content):
        response = requests.Response()
        response.status_code = 200
        response._content = content
        return response

    def _fake_not_ok_response(self):
        response = requests.Response()
        response.status_code = 404
        return response
