import requests
import json
import framepy
import threading
import time
from framepy import core
from framepy import modules
from framepy import _thread_level_cache
from framepy import _utils

SESSION_FIELD = 'eureka_http_session'


class Module(modules.Module):
    def before_setup(self, properties, arguments, beans):
        app_name = _utils.resolve_property_or_report_error(
            properties=properties,
            key='app_name',
            log_message='[Eureka] Missing app_name! Skipping registration in eureka cluster'
        )
        remote_config_url = _utils.resolve_property_or_report_error(
            properties=properties,
            key='remote_config_url',
            log_message='[Eureka] Missing remote_config_url! Skipping registration in eureka cluster'
        )
        public_hostname = _utils.resolve_property_or_report_error(
            properties=properties,
            key='public_hostname',
            log_message='[Eureka] Missing public_hostname! Skipping registration in eureka cluster'
        )

        remote_config_url = self._build_eureka_url(remote_config_url)

        eureka_template = EurekaTemplate()
        eureka_template._register_instance(remote_config_url, app_name, public_hostname, properties)
        eureka_template._register_heartbeat_service(remote_config_url, app_name, public_hostname)

        beans['_eureka_url'] = remote_config_url
        beans['eureka_template'] = eureka_template

    def after_setup(self, properties, arguments, context, beans_initializer):
        pass

    @staticmethod
    def _build_eureka_url(remote_config_url):
        return _utils.normalize_url(remote_config_url) + 'eureka'


class EurekaTemplate(framepy.BaseBean):
    def list_instances(self, service_name):
        response = self._get_session_from_cache().get(
            self.context._eureka_url + '/apps/' + service_name, headers={'accept': 'application/json'}
        )
        if response.status_code < 200 or response.status_code >= 300:
            raise Exception('Cannot retrieve instances of service ' + service_name)

        instances_list = response.json()['application']['instance']
        return [instance['hostName'] + ':' + str(instance['port']['$']) for instance in instances_list]

    def _register_instance(self, eureka_url, app_name, hostname, properties):
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
            response = self._get_session_from_cache().post(eureka_url + '/apps/' + app_name, json.dumps(instance_data),
                                                           headers={'Content-Type': 'application/json'})
            if self._response_status_not_ok(response):
                framepy.log.error('[Eureka] Cannot register instance on server! Status code {0}'.format(response.status_code))
        except requests.exceptions.ConnectionError:
            framepy.log.error('[Eureka] Cannot connect to server!')

    def _send_heartbeat(self, eureka_url, app_name, hostname):
        response = self._get_session_from_cache().put(eureka_url + '/apps/' + app_name + '/' + hostname,
                                                      headers={'Content-Type': 'application/json'})
        if self._response_status_not_ok(response):
            framepy.log.error('[Eureka] Sending heartbeat to cluster failed! Status code {0}'.format(response.status_code))

    def _register_heartbeat_service(self, remote_config_url, app_name, public_hostname):
        def heartbeat_sending_thread():
            while True:
                time.sleep(10)
                self._send_heartbeat(remote_config_url, app_name, public_hostname)

        thread = threading.Thread(target=heartbeat_sending_thread)
        thread.daemon = True
        thread.start()

    @staticmethod
    def _response_status_not_ok(response):
        return response.status_code < 200 or response.status_code >= 300

    @staticmethod
    def _get_session_from_cache():
        return _thread_level_cache.fetch_from_cache_or_create_new(SESSION_FIELD, lambda: requests.session())
