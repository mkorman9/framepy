import logging
import unittest
from unittest import mock

from assertpy import assert_that

from framepy import _utils
from framepy import core


class UtilsTest(unittest.TestCase):
    def test_normalize_url_non_normalized_url_should_return_normalized_url(self):
        # given
        url = 'http://127.0.0.1'

        # when
        normalized_url = _utils.normalize_url(url)

        # then
        assert_that(normalized_url).is_equal_to('http://127.0.0.1/')

    def test_normalize_url_already_normalized_url_should_return_the_same_url(self):
        # given
        url = 'http://127.0.0.1/'

        # when
        normalized_url = _utils.normalize_url(url)

        # then
        assert_that(normalized_url).is_equal_to('http://127.0.0.1/')

    def test_resolve_property_should_resolve_from_map(self):
        # given
        properties = {'someProperty': 'someValue'}

        # when
        result = _utils.resolve_property_or_report_error(properties, 'someProperty', 'log message')

        # then
        assert_that(result).is_equal_to('someValue')

    def test_resolve_property_should_resolve_from_default_value_and_log_event(self):
        # given
        properties = {}
        core.log.error = mock.MagicMock(spec=logging.Logger)

        # when
        result = _utils.resolve_property_or_report_error(properties, 'someProperty', 'log message', default_value='val')

        # then
        assert_that(result).is_equal_to('val')
        core.log.error.assert_called_once_with('log message')
