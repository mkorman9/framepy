import ConfigParser
import collections
import logging
from logging import handlers
import beans
import cherrypy


DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 8080
DEFAULT_APPLICATION_LOG = 'log/application.log'
DEFAULT_ACCESS_LOG = 'log/access.log'
DEFAULT_MAX_LOGS = 10
DEFAULT_MAX_LOG_SIZE = 10
MB_SIZE = 1000000
Mapping = collections.namedtuple('Mapping', ['bean', 'path'])


class Context(object):
    def __init__(self, entries):
        self.__dict__.update(entries)


def _setup_logging(load_properties):
    log = cherrypy.log
    log.error_file = ""
    log.access_file = ""

    maxBytes = getattr(log, "rot_maxBytes", load_properties.get('logs_max_size', DEFAULT_MAX_LOG_SIZE) * MB_SIZE)
    backupCount = getattr(log, "rot_backupCount", load_properties.get('logs_max_files', DEFAULT_MAX_LOGS))

    fname = getattr(log, "rot_error_file", load_properties.get('logs_application_file', DEFAULT_APPLICATION_LOG))
    h = handlers.RotatingFileHandler(fname, 'a', maxBytes, backupCount)
    h.setLevel(logging.INFO)
    h.setFormatter(cherrypy._cplogging.logfmt)
    log.error_log.addHandler(h)

    fname = getattr(log, "rot_access_file", load_properties.get('logs_access_file', DEFAULT_ACCESS_LOG))
    h = handlers.RotatingFileHandler(fname, 'a', maxBytes, backupCount)
    h.setLevel(logging.INFO)
    h.setFormatter(cherrypy._cplogging.logfmt)
    log.access_log.addHandler(h)


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
        engine = module.setup_engine(loaded_properties, kwargs)
        var_name = module.name + '_engine'
        beans[var_name] = engine
        beans.update(module.register_custom_beans(engine, kwargs))

    return Context(beans)


def _register_controllers(context, controllers_mappings):
    for m in controllers_mappings:
        m.bean.context = context
        m.bean.initialize()
        cherrypy.tree.mount(m.bean, m.path)


def _after_setup(context, modules, kwargs):
    for module in modules:
        module.after_setup(context, kwargs)


def start_application(properties,
                      controllers_mappings,
                      modules=(),
                      **kwargs):
    modules = (beans.Module(),) + modules

    loaded_properties = _load_properties(properties)
    _update_config(loaded_properties)
    _setup_logging(loaded_properties)
    context = _create_context(loaded_properties, modules, kwargs)

    _register_controllers(context, controllers_mappings)
    _after_setup(context, modules, kwargs)

    cherrypy.engine.start()
    cherrypy.engine.block()
