import unittest

from assertpy import assert_that

from framepy import amqp


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
