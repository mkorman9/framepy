import requests
import json
import cherrypy
import threading
import time


class Module(object):
    name = 'eureka'

    def setup_engine(self, loaded_properties, args):
        app_name = loaded_properties.get('app_name')
        remote_config_url = loaded_properties.get('remote_config_url')
        public_hostname = loaded_properties.get('public_hostname')

        if app_name is None or not app_name:
            cherrypy.log.error('Missing app_name! Skipping registration in eureka cluster')
            return
        if remote_config_url is None or not remote_config_url:
            cherrypy.log.error('Missing remote_config_url! Skipping registration in eureka cluster')
            return
        if public_hostname is None or not public_hostname:
            cherrypy.log.error('Missing public_hostname! Skipping registration in eureka cluster')
            return

        if not remote_config_url.endswith('/'):
            remote_config_url += '/'
        remote_config_url += 'eureka'

        _register_instance(remote_config_url, app_name, public_hostname)
        _register_heartbeat_service(remote_config_url, app_name, public_hostname)

        return remote_config_url

    def register_custom_beans(self, remote_config_url, args):
        return {'_eureka_url': remote_config_url}

    def after_setup(self, context, args):
        pass


def list_instances(context, service_name):
    response = requests.get(context._eureka_url + '/apps/' + service_name, headers={'accept': 'application/json'})
    if response.status_code < 200 or response.status_code >= 300:
        raise Exception('Cannot retrieve instances of service ' + service_name)

    instances_list = response.json()['application']['instance']
    return [instance['hostName'] + ':' + str(instance['port']['$']) for instance in instances_list]


def _register_instance(eureka_url, app_name, hostname):
    data_center_info = {
        "@class":"com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo",
        "name": "MyOwn"
    }

    instance_data = {
        'instance': {
            'hostName': hostname,
            'ipAddr': hostname,
            'app': app_name,
            'status': 'UP',
            'port': {
                "$": 8080,
                "@enabled": 'true'
            },
            'dataCenterInfo': data_center_info
        }
    }

    try:
        response = requests.post(eureka_url + '/apps/' + app_name, json.dumps(instance_data),
                                 headers={'Content-Type': 'application/json'})
        if response.status_code < 200 or response.status_code >= 300:
            cherrypy.log.error('Cannot register instance on eureka server! Status code ' + str(response.status_code))
    except requests.exceptions.ConnectionError:
        cherrypy.log.error('Cannot connect to eureka server!')


def _send_heartbeat(eureka_url, app_name, hostname):
    response = requests.put(eureka_url + '/apps/' + app_name + '/' + hostname,
                            headers={'Content-Type': 'application/json'})
    if response.status_code < 200 or response.status_code >= 300:
        cherrypy.log.error('Sending heartbeat to eureka cluster failed! Status code ' + str(response.status_code))


def _register_heartbeat_service(remote_config_url, app_name, public_hostname):
    def heartbeat_sending_thread():
        while True:
            time.sleep(10)
            _send_heartbeat(remote_config_url, app_name, public_hostname)

    thread = threading.Thread(target=heartbeat_sending_thread)
    thread.daemon = True
    thread.start()
