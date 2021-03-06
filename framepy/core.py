import collections
from framepy import logs
from framepy import beans
from framepy import web
from framepy import _configuration
from framepy import client
import logging
import cherrypy
import pkgutil

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 8000
Mapping = collections.namedtuple('Mapping', ['bean', 'path'])

log = logging.getLogger('framepy_logger')


class Context(object):
    def __init__(self, entries):
        self.__dict__.update(entries)


class BaseBean(object):
    def __init__(self):
        self.context = None

    def initialize(self, context):
        self.context = context


def _setup_server_config(load_properties):
    cherrypy.config.update(
        {
            'server.socket_port': int(load_properties.get('server_port', DEFAULT_PORT)),
            'server.socket_host': load_properties.get('server_host', DEFAULT_HOST),
            'tools.encode.on': True,
            'tools.encode.encoding': 'utf-8'
        }
    )


def _setup_modules(loaded_properties, modules, kwargs):
    system_beans = {}
    for module in modules:
        module.before_setup(loaded_properties, kwargs, system_beans)

    context = Context(system_beans)
    beans_initializer = beans.BeansInitializer()
    beans_initializer.initialize(context, system_beans)

    return context


def _after_setup(context, modules, kwargs, properties):
    beans_initializer = beans.BeansInitializer()
    beans_resolver = beans.BeansResolver(beans_initializer, beans.annotated_beans, beans.annotated_configurations)
    beans_resolver.resolve(context)

    for module in modules:
        module.after_setup(properties, kwargs, context, beans_initializer)


def _create_context(kwargs, loaded_properties, modules):
    context = _setup_modules(loaded_properties, modules, kwargs)
    _after_setup(context, modules, kwargs, loaded_properties)


def _finish_system_initialization(loaded_properties):
    _setup_server_config(loaded_properties)
    logs.setup_logging(log)


def scan_packages(packages_filter=lambda _: True):
    """ Scans for annotated classes and methods in submodules.
    Must be called before init_context if you want to use declarative config.
    NOTE: Only scans for modules that are located in SUBPACKAGES, all modules from current package are skipped """
    for modname in (modname for importer, modname, ispkg in pkgutil.walk_packages('.')
                    if '.' in modname and packages_filter(modname)):
        __import__(modname)


def init_context(properties_file,
                 modules=(),
                 **kwargs):
    """ Initializes all modules and beans. Returns application object for WSGI.
    :type properties_file: basestring
    :param properties_file: .ini file path to read properties from
    :type modules: tuple[modules.Module]
    :param modules: Module objects to initialize and append to context
    :type kwargs: dict
    :param kwargs: Additional parameters that are specified for passed modules
    :rtype: cherrypy._cptree.Tree
    :return: WSGI application
    """
    modules = (web.Module(), client.Module()) + modules

    properties = _configuration.create_configuration(properties_file)

    _finish_system_initialization(properties)
    _create_context(kwargs, properties, modules)

    return cherrypy.tree


def start_standalone_application():
    """ Starts standalone HTTP server and blocks current thread.
    It's opposite method of running application to WSGI server,
    however init_context MUST be called before this in any case """
    cherrypy.engine.start()
    cherrypy.engine.block()
