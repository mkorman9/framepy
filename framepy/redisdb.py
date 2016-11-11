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

        self.redis_host = redis_host
        self.redis_port = redis_port

    def register_custom_beans(self, context, args):
        return {'_redis_pool': redis.ConnectionPool(host=self.redis_host, port=self.redis_port, db=0)}

    def after_setup(self, context, args):
        pass


def get_connection(context):
    return redis.Redis(connection_pool=context._redis_pool)
