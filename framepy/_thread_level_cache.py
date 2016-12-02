import os
import threading

PID_FIELD_NAME = 'pid'

cache = threading.local()


def fetch_from_cache_or_create_new(field_name, field_creation_procedure):
    if not hasattr(cache, PID_FIELD_NAME):
        setattr(cache, PID_FIELD_NAME, os.getpid())
    if not hasattr(cache, field_name) or getattr(cache, PID_FIELD_NAME) != os.getpid():
        entity = field_creation_procedure()
        setattr(cache, field_name, entity)
        return entity
    else:
        return getattr(cache, field_name)
