import unittest
from assertpy import assert_that
from mock import mock

from framepy import logs
import cherrypy


class LogsTest(unittest.TestCase):
    @mock.patch('cherrypy.log')
    def test_should_setup_custom_loggers(self, cherrypy_log):
        # given
        logger = mock.MagicMock()

        # when
        logs.setup_logging(logger)

        # then
        logger.addHandler.assert_called_once()
        cherrypy_log.error_log.addHandler.assert_called_once()
        cherrypy_log.access_log.addHandler.assert_called_once()
