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
        """ Send GET http message to one of hosts specified by hosts_list.
        If communication fails (due to connection error or server error response) -
        message is retransmitted to another host.
        If communication to all hosts on lists failed - fallback function is called (if specified)
        :type context_path: basestring
        :param context_path: Path to HTTP resource (beginning with slash or not). For example /api/results
        :type hosts_list: list[string]
        :param hosts_list: List of hosts to ask for specified context path. May contain port after : sign
        :type fallback: object
        :param fallback: Fallback method to call if requests to all hosts failed. Result of this method is returned
        :type kwargs: dict
        :param kwargs: Arguments to pass to underlying requests library
        :rtype: requests.Response
        """
        return self._perform_operation(context_path, requests.get, hosts_list, fallback, **kwargs)

    def post(self, context_path, hosts_list, fallback=None, **kwargs):
        """ Send POST http message to one of hosts specified by hosts_list.
        If communication fails (due to connection error or server error response) -
        message is retransmitted to another host.
        If communication to all hosts on lists failed - fallback function is called (if specified)
        :type context_path: basestring
        :param context_path: Path to HTTP resource (beginning with slash or not). For example /api/results
        :type hosts_list: list[string]
        :param hosts_list: List of hosts to ask for specified context path. May contain port after : sign
        :type fallback: object
        :param fallback: Fallback method to call if requests to all hosts failed. Result of this method is returned
        :type kwargs: dict
        :param kwargs: Arguments to pass to underlying requests library
        :rtype: requests.Response
        """
        return self._perform_operation(context_path, requests.post, hosts_list, fallback, **kwargs)

    def put(self, context_path, hosts_list, fallback=None, **kwargs):
        """ Send PUT http message to one of hosts specified by hosts_list.
        If communication fails (due to connection error or server error response) -
        message is retransmitted to another host.
        If communication to all hosts on lists failed - fallback function is called (if specified)
        :type context_path: basestring
        :param context_path: Path to HTTP resource (beginning with slash or not). For example /api/results
        :type hosts_list: list[string]
        :param hosts_list: List of hosts to ask for specified context path. May contain port after : sign
        :type fallback: object
        :param fallback: Fallback method to call if requests to all hosts failed. Result of this method is returned
        :type kwargs: dict
        :param kwargs: Arguments to pass to underlying requests library
        :rtype: requests.Response
        """
        return self._perform_operation(context_path, requests.put, hosts_list, fallback, **kwargs)

    def delete(self, context_path, hosts_list, fallback=None, **kwargs):
        """ Send DELETE http message to one of hosts specified by hosts_list.
        If communication fails (due to connection error or server error response) -
        message is retransmitted to another host.
        If communication to all hosts on lists failed - fallback function is called (if specified)
        :type context_path: basestring
        :param context_path: Path to HTTP resource (beginning with slash or not). For example /api/results
        :type hosts_list: list[string]
        :param hosts_list: List of hosts to ask for specified context path. May contain port after : sign
        :type fallback: object
        :param fallback: Fallback method to call if requests to all hosts failed. Result of this method is returned
        :type kwargs: dict
        :param kwargs: Arguments to pass to underlying requests library
        :rtype: requests.Response
        """
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
