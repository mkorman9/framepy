import requests
import json
import os
import framepy
import threading
import time
import modules

from framepy import core

SESSION_FIELD = 'session'
PID_FIELD = 'pid'

sessions_cache = threading.local()


class Module(modules.Module):
    def before_setup(self, properties, arguments, beans):
        app_name = properties.get('app_name')
        remote_config_url = properties.get('remote_config_url')
        public_hostname = properties.get('public_hostname')

        if app_name is None or not app_name:
            framepy.log.error('[Eureka] Missing app_name! Skipping registration in eureka cluster')
            return
        if remote_config_url is None or not remote_config_url:
            framepy.log.error('[Eureka] Missing remote_config_url! Skipping registration in eureka cluster')
            return
        if public_hostname is None or not public_hostname:
            framepy.log.error('[Eureka] Missing public_hostname! Skipping registration in eureka cluster')
            return

        if not remote_config_url.endswith('/'):
            remote_config_url += '/'
        remote_config_url += 'eureka'

        _register_instance(remote_config_url, app_name, public_hostname, properties)
        _register_heartbeat_service(remote_config_url, app_name, public_hostname)

        beans['_eureka_url'] = remote_config_url

    def after_setup(self, properties, arguments, context, beans_initializer):
        pass


def list_instances(context, service_name):
    response = _get_session_from_cache().get(context._eureka_url + '/apps/' + service_name, headers={'accept': 'application/json'})
    if response.status_code < 200 or response.status_code >= 300:
        raise Exception('Cannot retrieve instances of service ' + service_name)

    instances_list = response.json()['application']['instance']
    return [instance['hostName'] + ':' + str(instance['port']['$']) for instance in instances_list]


def _register_instance(eureka_url, app_name, hostname, properties):
    instance_data = {
        'instance': {
            'hostName': hostname,
            'ipAddr': hostname,
            'app': app_name,
            'status': 'UP',
            'port': {
                "$": properties.get('server_port', core.DEFAULT_PORT),
                "@enabled": 'true'
            },
            'dataCenterInfo': {
                "@class": "com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo",
                "name": "MyOwn"
            }
        }
    }

    try:
        response = _get_session_from_cache().post(eureka_url + '/apps/' + app_name, json.dumps(instance_data),
                                 headers={'Content-Type': 'application/json'})
        if response.status_code < 200 or response.status_code >= 300:
            framepy.log.error('[Eureka] Cannot register instance on server! Status code {0}'.format(response.status_code))
    except requests.exceptions.ConnectionError:
        framepy.log.error('[Eureka] Cannot connect to server!')


def _send_heartbeat(eureka_url, app_name, hostname):
    response = _get_session_from_cache().put(eureka_url + '/apps/' + app_name + '/' + hostname,
                            headers={'Content-Type': 'application/json'})
    if response.status_code < 200 or response.status_code >= 300:
        framepy.log.error('[Eureka] Sending heartbeat to cluster failed! Status code {0}'.format(response.status_code))


def _register_heartbeat_service(remote_config_url, app_name, public_hostname):
    def heartbeat_sending_thread():
        while True:
            time.sleep(10)
            _send_heartbeat(remote_config_url, app_name, public_hostname)

    thread = threading.Thread(target=heartbeat_sending_thread)
    thread.daemon = True
    thread.start()


def _get_session_from_cache():
    if not hasattr(sessions_cache, PID_FIELD):
        setattr(sessions_cache, PID_FIELD, os.getpid())
    if not hasattr(sessions_cache, SESSION_FIELD) or getattr(sessions_cache, PID_FIELD) != os.getpid():
        channel = requests.session()
        setattr(sessions_cache, SESSION_FIELD, channel)
        return channel
    else:
        return getattr(sessions_cache, SESSION_FIELD)
