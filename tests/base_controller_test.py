import json
import unittest
import cherrypy
from assertpy import assert_that

from framepy import web

FAKE_DATA = 'fake_data'
PLAIN_TEXT_MIME = 'text/plain'
JSON_MIME = 'application/json'


class BaseControllerTest(unittest.TestCase):
    def setUp(self):
        cherrypy.response.headers = {}
        cherrypy.response.status = 200

    def test_calling_for_non_existing_method_should_return_404(self):
        # given
        self._set_request_method('GET')
        controller = ControllerWithoutMethods()

        # when
        response = self._parse_json_response(controller.default())

        # then
        self._assert_response_status(404)
        self._assert_content_type(JSON_MIME)
        assert_that(response['status']).is_equal_to('error')
        assert_that(response['error']).is_equal_to('Not found')

    def test_should_call_method_without_arguments(self):
        # given
        self._set_request_method('GET')
        controller = ControllerWithGET()

        # when
        response = self._parse_json_response(controller.default())

        # then
        self._assert_response_status(200)
        self._assert_content_type(JSON_MIME)
        assert_that(response['status']).is_equal_to('ok')
        assert_that(response['data']).is_equal_to(FAKE_DATA)

    def test_should_use_proper_content_type(self):
        # given
        self._set_request_method('GET')
        controller = ControllerGeneratingPlainString()

        # when
        response = controller.default()

        # then
        self._assert_response_status(200)
        self._assert_content_type(PLAIN_TEXT_MIME)
        assert_that(response).is_equal_to(FAKE_DATA)

    def test_should_return_bad_request_after_calling_method_without_expected_argument(self):
        # given
        self._set_request_method('PUT')
        controller = ControllerWithPUTExpectingArgument()

        # when
        response = self._parse_json_response(controller.default())

        # then
        self._assert_response_status(400)
        self._assert_content_type(JSON_MIME)
        assert_that(response['status']).is_equal_to('error')
        assert_that(response['error']).is_equal_to('Bad Request')

    def test_should_call_method_with_argument(self):
        # given
        self._set_request_method('PUT')
        controller = ControllerWithPUTExpectingArgument()
        argument = FAKE_DATA

        # when
        response = self._parse_json_response(controller.default(argument=argument))

        # then
        self._assert_response_status(200)
        self._assert_content_type(JSON_MIME)
        assert_that(response['status']).is_equal_to('ok')
        assert_that(response['data']).is_equal_to(argument)

    @staticmethod
    def _parse_json_response(response):
        return json.loads(response.decode(web.DEFAULT_ENCODING))

    @staticmethod
    def _set_request_method(method):
        cherrypy.request.method = method

    @staticmethod
    def _assert_content_type(content_type):
        assert_that(cherrypy.response.headers['Content-Type']).is_equal_to(content_type)

    @staticmethod
    def _assert_response_status(status_code):
        assert_that(cherrypy.response.status).is_equal_to(status_code)


class ControllerWithoutMethods(web.BaseController):
    pass


class ControllerWithGET(web.BaseController):
    @web.method('GET')
    def get(self):
        return web.ResponseEntity(data=FAKE_DATA)


class ControllerGeneratingPlainString(web.BaseController):
    @web.method('GET')
    @web.content_type(PLAIN_TEXT_MIME)
    def get(self):
        return FAKE_DATA


class ControllerWithPUTExpectingArgument(web.BaseController):
    @web.method('PUT')
    def put(self, argument):
        return web.ResponseEntity(data=argument)
