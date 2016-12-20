import requests
import cherrypy
import configparser
from itertools import chain
from framepy import _utils


def create_configuration(file):
    return _update_with_remote_configuration(_load_properties(file))


def _load_properties(file):
    parser = configparser.RawConfigParser()
    try:
        with open(file, 'r') as f:
            parser.read_file(f)
    except IOError:
        cherrypy.log.error('Cannot open properties file {0}'.format(file))
        raise IOError('Cannot open properties file {0}'.format(file))
    all_properties = [parser.items(section) for section in parser.sections()]
    return {key: value for (key, value) in list(chain(*all_properties))}


def _update_with_remote_configuration(properties):
    remote_config_url = properties.get('remote_config_url')
    app_name = properties.get('app_name')

    if not remote_config_url:
        cherrypy.log.error('Remote config URL not present. Skipping.')
        return properties
    if app_name is None or not app_name:
        cherrypy.log.error('Remote config URL is present but application name was not specified!')
        return properties

    remote_config_url = _utils.normalize_url(remote_config_url)

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
