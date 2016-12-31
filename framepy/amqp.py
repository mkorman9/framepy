import framepy
import pika
import pika.exceptions
import threading
import time
from framepy import core
from framepy import modules
from framepy import _thread_level_cache
from framepy import _utils

WAIT_TIME_AFTER_CONNECTION_FAILURE = 2
CONNECTION_RETRIES_COUNT = 3
DEFAULT_AMQP_PORT = 5672
CHANNEL_FIELD = 'channel'

annotated_listeners = {}


def listener(queue_name):
    def wrapped(potential_listener_class):
        annotated_listeners[queue_name] = potential_listener_class
        return potential_listener_class
    return wrapped


class Module(modules.Module):
    def before_setup(self, properties, arguments, beans):
        self._map_listeners_from_arguments(arguments)

        broker_address = _utils.resolve_property_or_report_error(
            properties=properties,
            key='broker_address',
            log_message='[AMQP] broker_address not found in properties!',
            default_value=''
        )
        broker_username = _utils.resolve_property_or_report_error(
            properties=properties,
            key='broker_username',
            log_message='[AMQP] broker_username not found in properties!'
        )
        broker_password = _utils.resolve_property_or_report_error(
            properties=properties,
            key='broker_password',
            log_message='[AMQP] broker_password not found in properties!'
        )

        broker_host, broker_port = self._parse_address(broker_address)

        credentials = pika.PlainCredentials(broker_username, broker_password)
        beans['amqp_engine'] = pika.ConnectionParameters(broker_host, broker_port, '/', credentials)

    def after_setup(self, properties, arguments, context, beans_initializer):
        listeners_mappings = arguments.get('listeners_mappings', [])
        for key, bean in annotated_listeners.items():
            listeners_mappings.append(core.Mapping(bean(), key))

        for m in listeners_mappings:
            beans_initializer.initialize_single_bean('__listener_' + m.path, m.bean, context)
            _register_listener(context, m.path, m.bean.on_message)

    def _map_listeners_from_arguments(self, arguments):
        listeners = arguments.get('listeners') or []
        for listener_class, path in listeners:
            annotated_listeners[path] = listener_class

    def _parse_address(self, broker_address):
        address_parts = broker_address.split(':')

        if len(address_parts) == 1:
            broker_host = broker_address
            broker_port = DEFAULT_AMQP_PORT
        elif len(address_parts) == 2:
            broker_host = address_parts[0]
            broker_port = int(address_parts[1])
        else:
            framepy.log.error('Invalid broker address!')
            return None, None
        return broker_host, broker_port


class BaseListener(core.BaseBean):
    def on_message(self, channel, method, properties, body):
        pass


class ConnectionError(Exception):
    pass


def send_message(context, routing_key, message, durable=True, exchange=''):
    sending_channel = get_channel(context)
    sending_channel.queue_declare(queue=routing_key, durable=durable)
    sending_channel.basic_publish(exchange=exchange,
                                  routing_key=routing_key,
                                  body=message,
                                  properties=pika.BasicProperties(
                                      delivery_mode=2,
                                  ))


def get_channel(context):
    return _thread_level_cache.fetch_from_cache_or_create_new(CHANNEL_FIELD,
                                                              lambda: _establish_connection(context).channel())


def _establish_connection(context):
    new_connection = None
    connection_established = False
    tries_count = CONNECTION_RETRIES_COUNT
    while not connection_established:
        if tries_count:
            try:
                new_connection = pika.BlockingConnection(context.amqp_engine)
                connection_established = True
            except pika.exceptions.ConnectionClosed:
                time.sleep(WAIT_TIME_AFTER_CONNECTION_FAILURE)
                tries_count -= 1
        else:
            framepy.log.error('[AMQP] Cannot establish connection with {0}:{1}'.format(context.amqp_engine.host,
                                                                                       context.amqp_engine.port))
            raise ConnectionError('Cannot establish AMQP connection')
    return new_connection


def _register_listener(context, routing_key, callback):
    thread_local_channel = get_channel(context)

    def receive_action(channel, method, properties, body):
        try:
            callback(channel, method, properties, body)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            framepy.log.error('[AMQP] Error receiving message from queue {0}, exception: {1}'.format(routing_key, e))

    def listener_thread():
        thread_local_channel.queue_declare(queue=routing_key, durable=True)
        thread_local_channel.basic_qos(prefetch_count=1)
        thread_local_channel.basic_consume(receive_action, routing_key)
        thread_local_channel.start_consuming()

    thread = threading.Thread(target=listener_thread)
    thread.daemon = True
    thread.start()
