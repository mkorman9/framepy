import ConfigParser
import collections
import logging
from logging import handlers
import beans
import cherrypy
import requests


DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 8000
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
    error_log = handlers.RotatingFileHandler(fname, 'a', maxBytes, backupCount)
    error_log.setLevel(logging.INFO)
    error_log.setFormatter(cherrypy._cplogging.logfmt)
    log.error_log.addHandler(error_log)

    fname = getattr(log, "rot_access_file", load_properties.get('logs_access_file', DEFAULT_ACCESS_LOG))
    h = handlers.RotatingFileHandler(fname, 'a', maxBytes, backupCount)
    h.setLevel(logging.INFO)
    h.setFormatter(cherrypy._cplogging.logfmt)
    log.access_log.handlers = []
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


def _load_remote_configuration(properties):
    remote_config_url = properties.get('remote_config_url')
    app_name = properties.get('app_name')

    if remote_config_url is None or not remote_config_url:
        cherrypy.log.error('Remote config URL not present. Skipping.')
        return properties
    if app_name is None or not app_name:
        cherrypy.log.error('Remote config URL is present but applciation name was not specified!')
        return properties

    if not remote_config_url.endswith('/'):
        remote_config_url += '/'

    remote_properties = {}
    try:
        config_server_response = requests.get(remote_config_url + app_name + '/default')
        if config_server_response.status_code != 200:
            cherrypy.log.error('Error loading remote properties! Status code ' + str(config_server_response.status_code))
            return properties

        sources = [source['source'] for source in config_server_response.json()['propertySources']]
        for source in sources:
            remote_properties.update(source)
    except requests.exceptions.ConnectionError:
        cherrypy.log.error('Error while connecting to remote config server!')
        return properties

    new_properties = properties.copy()
    new_properties.update(remote_properties)
    return new_properties


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


def _shutdown_modules(context, modules):
    for module in modules:
        module.shutdown(context)


def init_context(properties,
                 controllers_mappings,
                 modules=(),
                 **kwargs):
    modules = (beans.Module(),) + modules

    loaded_properties = _load_properties(properties)
    loaded_properties = _load_remote_configuration(loaded_properties)
    _update_config(loaded_properties)
    _setup_logging(loaded_properties)
    context = _create_context(loaded_properties, modules, kwargs)

    _register_controllers(context, controllers_mappings)
    _after_setup(context, modules, kwargs)

    return cherrypy.tree


def start_standalone_application():
    cherrypy.engine.start()
    cherrypy.engine.block()
