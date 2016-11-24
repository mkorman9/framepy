import random
import requests
import framepy

HTTP_SERVER_ERRORS_BORDER = 500
PROTOCOL = 'http://'


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
            framepy.log.error('Invoking {0} on node {1} failed!'.format(context_path, host))

        hosts = [h for h in hosts if h != host]

    if fallback is not None:
        return fallback(context_path, **kwargs)


def get(context_path, hosts_list, fallback=None, **kwargs):
    return _perform_operation(context_path, requests.get, hosts_list, fallback, **kwargs)


def post(context_path, hosts_list, fallback=None, **kwargs):
    return _perform_operation(context_path, requests.post, hosts_list, fallback, **kwargs)


def put(context_path, hosts_list, fallback=None, **kwargs):
    return _perform_operation(context_path, requests.put, hosts_list, fallback, **kwargs)


def delete(context_path, hosts_list, fallback=None, **kwargs):
    return _perform_operation(context_path, requests.delete, hosts_list, fallback, **kwargs)
