import random
import requests
from framepy import modules
import cherrypy

HTTP_SERVER_ERRORS_BORDER = 500
PROTOCOL = 'http://'


class Module(modules.Module):
    def before_setup(self, properties, arguments, beans):
        beans['http_template'] = HttpTemplate()

    def after_setup(self, properties, arguments, context, beans_initializer):
        pass


class HttpTemplate(object):
    def get(self, context_path, hosts_list, fallback=None, **kwargs):
        return self._perform_operation(context_path, requests.get, hosts_list, fallback, **kwargs)

    def post(self, context_path, hosts_list, fallback=None, **kwargs):
        return self._perform_operation(context_path, requests.post, hosts_list, fallback, **kwargs)

    def put(self, context_path, hosts_list, fallback=None, **kwargs):
        return self._perform_operation(context_path, requests.put, hosts_list, fallback, **kwargs)

    def delete(self, context_path, hosts_list, fallback=None, **kwargs):
        return self._perform_operation(context_path, requests.delete, hosts_list, fallback, **kwargs)

    @staticmethod
    def _perform_operation(context_path, operation, hosts_list, fallback, **kwargs):
        hosts = hosts_list[:]

        if not context_path.startswith('/'):
            context_path = '/' + context_path

        while hosts:
            host = random.choice(hosts)
            try:
                address = PROTOCOL + host + context_path
                response = operation(address, **kwargs)
                if response.status_code < HTTP_SERVER_ERRORS_BORDER:
                    return response.json()
            except requests.exceptions.ConnectionError:
                cherrypy.log.error('Invoking {0} on node {1} failed!'.format(context_path, host))

            hosts = [h for h in hosts if h != host]

        if fallback is not None:
            return fallback(context_path, **kwargs)
