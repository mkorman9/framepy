import framepy.client
import unittest
import mock
import requests


class ClientTest(unittest.TestCase):
    def test_get_should_be_performed_for_single_host(self):
        # given
        requests.get = ClientTest.mock_http_method(200)
        hosts_list = ['127.0.0.1']

        # when
        framepy.client.get('/', hosts_list)

        # then
        requests.get.assert_called_once_with('http://127.0.0.1/')

    def test_post_should_be_performed_for_single_host(self):
        # given
        requests.post = ClientTest.mock_http_method(200)
        hosts_list = ['127.0.0.1']

        # when
        framepy.client.post('/', hosts_list)

        # then
        requests.post.assert_called_once_with('http://127.0.0.1/')

    def test_put_should_be_performed_for_single_host(self):
        # given
        requests.put = ClientTest.mock_http_method(200)
        hosts_list = ['127.0.0.1']

        # when
        framepy.client.put('/', hosts_list)

        # then
        requests.put.assert_called_once_with('http://127.0.0.1/')

    def test_delete_should_be_performed_for_single_host(self):
        # given
        requests.delete = ClientTest.mock_http_method(200)
        hosts_list = ['127.0.0.1']

        # when
        framepy.client.delete('/', hosts_list)

        # then
        requests.delete.assert_called_once_with('http://127.0.0.1/')

    def test_fallback_should_be_called_if_connection_fails(self):
        # given
        requests.get = ClientTest.mock_http_method(200)
        requests.get.side_effect = requests.ConnectionError
        hosts_list = ['127.0.0.1']

        fallback = mock.MagicMock()

        # when
        framepy.client.get('/', hosts_list, fallback=fallback)

        # then
        requests.get.assert_called_once_with('http://127.0.0.1/')
        fallback.assert_called_once_with('/')

    def test_fallback_should_be_called_if_request_fails(self):
        # given
        requests.get = ClientTest.mock_http_method(503)
        hosts_list = ['127.0.0.1']

        fallback = mock.MagicMock()

        # when
        framepy.client.get('/', hosts_list, fallback=fallback)

        # then
        requests.get.assert_called_once_with('http://127.0.0.1/')
        fallback.assert_called_once_with('/')

    @staticmethod
    def mock_http_method(return_code):
        class Operation(object):
            def __init__(self, status_code):
                self.status_code = status_code

            def json(self):
                return {}

        request_mock = mock.MagicMock()
        request_mock.return_value = Operation(return_code)
        return request_mock
