import threading
import unittest

from assertpy import assert_that
from framepy import core

from framepy import beans
from mock import mock
import pika
import pika.exceptions

from framepy import amqp
from framepy import _thread_level_cache


class AmqpTest(unittest.TestCase):
    def test_before_setup_should_create_connection_parameters(self):
        # given
        properties = {
            'broker_address': 'localhost:5673',
            'broker_username': 'test',
            'broker_password': 'test123'
        }
        module = amqp.Module()
        beans = {}

        # when
        module.before_setup(properties, {}, beans)

        # then
        assert_that('amqp_engine' in beans).is_true()
        assert_that(beans['amqp_engine'].host).is_equal_to('localhost')
        assert_that(beans['amqp_engine'].port).is_equal_to(5673)
        assert_that(beans['amqp_engine'].credentials.username).is_equal_to('test')
        assert_that(beans['amqp_engine'].credentials.password).is_equal_to('test123')

    def test_before_setup_should_create_connection_parameters_with_default_port(self):
        # given
        properties = {
            'broker_address': 'localhost',
            'broker_username': 'test',
            'broker_password': 'test123'
        }
        module = amqp.Module()
        beans = {}

        # when
        module.before_setup(properties, {}, beans)

        # then
        assert_that('amqp_engine' in beans).is_true()
        assert_that(beans['amqp_engine'].host).is_equal_to('localhost')
        assert_that(beans['amqp_engine'].port).is_equal_to(amqp.DEFAULT_AMQP_PORT)
        assert_that(beans['amqp_engine'].credentials.username).is_equal_to('test')
        assert_that(beans['amqp_engine'].credentials.password).is_equal_to('test123')

    def test_before_setup_should_create_connection_parameters_with_invalid_broker_address_using_default_values(self):
        # given
        properties = {
            'broker_address': ':12:12:12',
            'broker_username': 'test',
            'broker_password': 'test123'
        }
        module = amqp.Module()
        beans = {}

        # when
        module.before_setup(properties, {}, beans)

        # then
        assert_that('amqp_engine' in beans).is_true()
        assert_that(beans['amqp_engine'].host).is_equal_to('localhost')
        assert_that(beans['amqp_engine'].port).is_equal_to(amqp.DEFAULT_AMQP_PORT)
        assert_that(beans['amqp_engine'].credentials.username).is_equal_to('test')
        assert_that(beans['amqp_engine'].credentials.password).is_equal_to('test123')

    @mock.patch('framepy.amqp.get_channel')
    def test_should_initialize_listeners(self, get_channel):
        # given
        module = amqp.Module()
        listener = core.Mapping(ListenerClass(), 'listener')
        context = mock.MagicMock()
        bean_initializer = beans.BeansInitializer()
        channel = get_channel.return_value

        # when
        module.after_setup({}, {'listeners_mappings': [listener]}, context, bean_initializer)

        # then
        channel.queue_declare.assert_called_once()
        channel.basic_qos.assert_called_once()
        channel.basic_consume.assert_called_once()
        channel.start_consuming.assert_called_once()

    @mock.patch('pika.BlockingConnection')
    def test_should_establish_connection_and_return_working_channel(self, blocking_connection):
        # given
        self._clear_thread_level_cache()

        context = mock.MagicMock()
        expected_channel = blocking_connection.return_value.channel.return_value

        # when
        channel = amqp.get_channel(context)

        # then
        assert_that(channel).is_equal_to(expected_channel)
        blocking_connection.assert_called_once_with(context.amqp_engine)

    @mock.patch('pika.BlockingConnection')
    def test_should_raise_connection_error_if_cannot_connect_to_broker(self, blocking_connection):
        # given
        self._clear_thread_level_cache()
        self._mock_wait_time()

        context = mock.MagicMock()
        blocking_connection.side_effect = pika.exceptions.ConnectionClosed()

        # when then
        with self.assertRaises(amqp.ConnectionError):
            amqp.get_channel(context)

        assert_that(blocking_connection.call_count).is_equal_to(3)

    @mock.patch('framepy.amqp.get_channel')
    def test_should_send_message(self, get_channel):
        # given
        channel = get_channel.return_value
        context = mock.MagicMock()
        routing_key = 'queue_name'
        message = 'sample message'
        durable = True
        exchange = ''

        # when
        amqp.send_message(context, routing_key, message, durable=durable, exchange=exchange)

        # then
        channel.queue_declare.asset_called_once_with(queue=routing_key, durable=durable)
        _, publish_kwargs = channel.basic_publish.call_args
        assert_that(publish_kwargs['exchange']).is_equal_to(exchange)
        assert_that(publish_kwargs['routing_key']).is_equal_to(routing_key)
        assert_that(publish_kwargs['body']).is_equal_to(message)

    @staticmethod
    def _clear_thread_level_cache():
        _thread_level_cache.cache = threading.local()

    @staticmethod
    def _mock_wait_time():
        amqp.WAIT_TIME_AFTER_CONNECTION_FAILURE = 0


class ListenerClass(amqp.BaseListener):
    def on_message(self, channel, method, properties, body):
        pass
