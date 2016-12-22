import unittest
from mock import mock
import cherrypy

from framepy import _configuration
from framepy import core
from framepy import logs
from framepy import modules


class CoreTest(unittest.TestCase):
    def test_context_should_be_initialized(self):
        # given
        custom_module = mock.MagicMock(spec=modules.Module)
        properties_items = {'server_host': 'localhost', 'server_port': '8080'}
        properties_file_mock = self._create_properties_file_mock(properties_items)
        cherrypy_update_config_mock = self._create_mock_for_cherrypy_config_update()
        logging_mock = self._create_mock_of_logging_system()

        # when
        core.init_context(properties_file_mock, modules=(custom_module,))

        # then
        cherrypy_update_config_mock.assert_called_once()
        logging_mock.assert_called_once_with(core.log)
        custom_module.before_setup.assert_called_once()
        custom_module.after_setup.assert_called_once()

    @staticmethod
    def _create_properties_file_mock(properties_items):
        _configuration._load_properties = lambda _: properties_items
        return mock.MagicMock()

    @staticmethod
    def _create_mock_for_cherrypy_config_update():
        cherrypy.config.update = mock.MagicMock()
        return cherrypy.config.update

    @staticmethod
    def _create_mock_of_logging_system():
        logs.setup_logging = mock.MagicMock()
        return logs.setup_logging
