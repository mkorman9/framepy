import ConfigParser
import collections
import logs
import logging
import beans
import cherrypy
import pkgutil
import web
import remote_configuration


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


def _update_config(load_properties):
    cherrypy.config.update({'server.socket_port': load_properties.get('server_port', DEFAULT_PORT),
                            'server.socket_host': load_properties.get('server_host', DEFAULT_HOST)})


def _load_properties(file):
    parser = ConfigParser.RawConfigParser()
    try:
        parser.readfp(open(file, 'r'))
    except IOError:
        cherrypy.log.error('Cannot open properties file {0}'.format(file))
        raise IOError('Cannot open properties file {0}'.format(file))
    return {key: value for (key, value) in parser.items('Properties')}


def _create_context(loaded_properties, modules, kwargs):
    beans = {}
    for module in modules:
        module.before_setup(loaded_properties, kwargs, beans)

    return Context(beans)


def _after_setup(context, modules, kwargs, properties, beans_initializer):
    beans_initializer.initialize_all(context)
    for module in modules:
        module.after_setup(properties, kwargs, context, beans_initializer)


def scan_packages(packages_filter=lambda _: True):
    for modname in (modname for importer, modname, ispkg in pkgutil.walk_packages('.')
                    if '.' in modname and packages_filter(modname)):
        __import__(modname)


def init_context(properties,
                 modules=(),
                 **kwargs):
    beans_initializer = beans.BeansInitializer()
    modules = (web.Module(),) + modules

    loaded_properties = _load_properties(properties)
    loaded_properties = remote_configuration.load_remote_configuration(loaded_properties)
    _update_config(loaded_properties)
    logs.setup_logging(log)
    context = _create_context(loaded_properties, modules, kwargs)

    _after_setup(context, modules, kwargs, loaded_properties, beans_initializer)

    return cherrypy.tree


def start_standalone_application():
    cherrypy.engine.start()
    cherrypy.engine.block()
