import redis
import cherrypy

DEFAULT_REDIS_PORT = 6379


class Module(object):
    name = 'redisdb'

    def setup_engine(self, loaded_properties, args):
        redis_host = loaded_properties.get('redis_host')
        redis_port = loaded_properties.get('redis_port')

        if redis_host is None or not redis_host:
            cherrypy.log.error('Missing redis_host!')
            return
        if redis_port is None or not redis_port:
            cherrypy.log.error('Missing redis_port! Setting default value ' + str(DEFAULT_REDIS_PORT))
            redis_port = DEFAULT_REDIS_PORT

        return redis.ConnectionPool(host=redis_host, port=int(redis_port), db=0)

    def register_custom_beans(self, connection_pool, args):
        return {'_redis_pool': connection_pool}

    def after_setup(self, context, args):
        pass


def get_connection(context):
    return redis.Redis(connection_pool=context._redis_pool)
