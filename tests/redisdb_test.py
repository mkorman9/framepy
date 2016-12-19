import unittest
import mock
import redis
from assertpy import assert_that

from framepy import redisdb


class RedisdbTest(unittest.TestCase):
    def test_connection_pool_bean_should_be_registered(self):
        # given
        redis.ConnectionPool = mock.MagicMock(spec=redis.ConnectionPool)
        beans_map = {}
        properties = {'redis_host': '127.0.0.1', 'redis_port': '1122', 'redis_password': 'test'}

        # when
        redisdb.Module().before_setup(properties, {}, beans_map)

        # then
        assert_that('_redis_pool' in beans_map).is_true()
        redis.ConnectionPool.assert_called_once_with(host='127.0.0.1', port=1122, db=0, password='test')

    def test_get_connection_should_return_valid_connection(self):
        # given
        connection = mock.MagicMock()
        redis.Redis = mock.MagicMock()
        context = mock.MagicMock()

        redis.Redis.return_value = connection

        # when
        returned_connection = redisdb.get_connection(context)

        # then
        assert_that(returned_connection).is_equal_to(connection)
        redis.Redis.assert_called_once_with(connection_pool=context._redis_pool)
        connection.ping.assert_called_once()
