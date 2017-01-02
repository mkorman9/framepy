import redis
import framepy
from framepy import modules
from framepy import _utils

DEFAULT_REDIS_PORT = 6379


class Module(modules.Module):
    def before_setup(self, properties, arguments, beans):
        redis_host = _utils.resolve_property_or_report_error(
            properties=properties,
            key='redis_host',
            log_message='[Redis] Missing redis_host!'
        )
        redis_port = _utils.resolve_property_or_report_error(
            properties=properties,
            key='redis_port',
            log_message='[Redis] Missing redis_port! Setting default value {}'.format(DEFAULT_REDIS_PORT),
            default_value=DEFAULT_REDIS_PORT
        )
        password = _utils.resolve_property_or_report_error(
            properties=properties,
            key='redis_password',
            log_message='[Redis] Missing password! Skipping authentication'
        )

        beans['_redis_pool'] = redis.ConnectionPool(host=redis_host, port=int(redis_port), db=0, password=password)
        beans['redis_template'] = RedisTemplate()

    def after_setup(self, properties, arguments, context, beans_resolver):
        pass


class ConnectionError(Exception):
    pass


class RedisTemplate(framepy.BaseBean):
    def get_connection(self):
        connection = redis.Redis(connection_pool=self.context._redis_pool)
        try:
            connection.ping()
        except redis.exceptions.ConnectionError:
            framepy.log.error('[Redis] Connection pool returned invalid connection!')
            raise ConnectionError('Cannot connect to Redis')
        return connection
