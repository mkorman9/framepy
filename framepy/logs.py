import cherrypy
import logging
from cherrypy._cplogging import LogManager

ERROR_LOG_FORMATTER = logging.Formatter('[%(asctime)s] %(levelname)s %(filename)s:%(funcName)s: %(message)s')
ACCESS_LOG_FORMATTER = '{h} {l} {u} "{r}" {s} {b} "{f}" "{a}"'


def setup_logging(logger):
    _hack_cherrypy_logs()

    application_log_handler = _setup_application_log()
    access_log_handler = _setup_access_log_handler()

    logger.addHandler(application_log_handler)

    cherrypy.log.error_log.handlers = []
    cherrypy.log.error_log.addHandler(application_log_handler)
    cherrypy.log.access_log.handlers = []
    cherrypy.log.access_log.addHandler(access_log_handler)


def _hack_cherrypy_logs():
    LogManager.time = lambda *_: ''
    LogManager.access_log_format = ACCESS_LOG_FORMATTER


def _setup_access_log_handler():
    access_log_handler = logging.StreamHandler()
    access_log_handler.setLevel(logging.INFO)
    access_log_handler.setFormatter(ERROR_LOG_FORMATTER)
    return access_log_handler


def _setup_application_log():
    application_log_handler = logging.StreamHandler()
    application_log_handler.setLevel(logging.INFO)
    application_log_handler.setFormatter(ERROR_LOG_FORMATTER)
    return application_log_handler
