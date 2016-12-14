import redis
import framepy
from framepy import modules

DEFAULT_REDIS_PORT = 6379


class Module(modules.Module):
    def before_setup(self, properties, arguments, beans):
        redis_host = properties.get('redis_host')
        redis_port = properties.get('redis_port')
        password = properties.get('redis_password')

        if redis_host is None or not redis_host:
            framepy.log.error('[Redis] Missing redis_host!')
            return
        if redis_port is None or not redis_port:
            framepy.log.error('[Redis] Missing redis_port! Setting default value ' + str(DEFAULT_REDIS_PORT))
            redis_port = DEFAULT_REDIS_PORT
        if password is None or not password:
            framepy.log.error('[Redis] Missing password! Skipping authentication')
            password = None

        beans['_redis_pool'] = redis.ConnectionPool(host=redis_host, port=int(redis_port), db=0, password=password)

    def after_setup(self, properties, arguments, context, beans_initializer):
        pass


class ConnectionError(Exception):
    pass


def get_connection(context):
    connection = redis.Redis(connection_pool=context._redis_pool)
    try:
        connection.ping()
    except redis.exceptions.ConnectionError:
        framepy.log.error('[Redis] Connection pool returned invalid connection!')
        raise ConnectionError('Cannot connect to Redis')
    return connection
