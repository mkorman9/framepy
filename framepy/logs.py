import cherrypy
import logging
from logging import handlers

DEFAULT_APPLICATION_LOG = 'log/application.log'
DEFAULT_ACCESS_LOG = 'log/access.log'
DEFAULT_MAX_LOGS = 10
DEFAULT_MAX_LOG_SIZE = 10
MB_SIZE = 1000000
FORMATTER = logging.Formatter('[%(asctime)s] %(levelname)s %(filename)s:%(funcName)s: %(message)s')


def setup_logging(logger, properties):
    system_log = cherrypy.log
    system_log.error_file = ""
    system_log.access_file = ""

    max_bytes = getattr(system_log, "rot_maxBytes", properties.get('logs_max_size', DEFAULT_MAX_LOG_SIZE) * MB_SIZE)
    backup_count = getattr(system_log, "rot_backupCount", properties.get('logs_max_files', DEFAULT_MAX_LOGS))

    error_log_file = getattr(system_log, "rot_error_file",
                             properties.get('logs_application_file', DEFAULT_APPLICATION_LOG))
    access_log_file = getattr(system_log, "rot_access_file", properties.get('logs_access_file', DEFAULT_ACCESS_LOG))

    application_log_handler = _setup_application_log(backup_count, error_log_file, max_bytes)
    access_log_handler = _setup_access_log_handler(access_log_file, backup_count, max_bytes)

    logger.addHandler(application_log_handler)
    logger.addHandler(logging.StreamHandler())

    system_log.error_log.addHandler(application_log_handler)
    system_log.access_log.handlers = []
    system_log.access_log.addHandler(access_log_handler)


def _setup_access_log_handler(access_log_file, backup_count, max_bytes):
    access_log_handler = handlers.RotatingFileHandler(access_log_file, 'a', max_bytes, backup_count)
    access_log_handler.setLevel(logging.INFO)
    access_log_handler.setFormatter(cherrypy._cplogging.logfmt)
    return access_log_handler


def _setup_application_log(backup_count, error_log_file, max_bytes):
    application_log_handler = handlers.RotatingFileHandler(error_log_file, 'a', max_bytes, backup_count)
    application_log_handler.setLevel(logging.INFO)
    application_log_handler.setFormatter(FORMATTER)
    return application_log_handler
