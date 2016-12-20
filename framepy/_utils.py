from . import core

DEFAULT_URL = 'http://localhost'


def normalize_url(url):
    """
    :type url: str
    :rtype: str
    """
    if not url:
        return DEFAULT_URL
    if not url.endswith('/'):
        url += '/'
    return url


def resolve_property_or_report_error(properties, key, log_message, default_value=None):
    """
    :type properties: dict[string, string]
    :type key: str
    :type log_message: str
    :type default_value: *
    """
    value = properties.get(key, None)
    if not value:
        core.log.error(log_message)
        value = default_value
    return value
