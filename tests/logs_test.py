import unittest
from assertpy import assert_that
from mock import mock

from framepy import logs
import cherrypy


class LogsTest(unittest.TestCase):
    def test_should_setup_custom_loggers(self):
        # given
        logger = mock.MagicMock()

        # when
        logs.setup_logging(logger)

        # then
        logger.addHandler.assert_called_once()
        assert_that(len(cherrypy.log.error_log.handlers)).is_equal_to(1)
        assert_that(len(cherrypy.log.access_log.handlers)).is_equal_to(1)
