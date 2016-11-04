import cherrypy
import pika
import threading


DEFAULT_AMQP_PORT = 5672


class Module(object):
    name = 'amqp'

    def setup_engine(self, loaded_properties, args):
        def parse_address():
            broker_address = loaded_properties['broker_address']
            address_parts = broker_address.split(':')

            if len(address_parts) == 1:
                broker_host = broker_address
                broker_port = DEFAULT_AMQP_PORT
            elif len(address_parts) == 2:
                broker_host = address_parts[0]
                broker_port = int(address_parts[1])
            else:
                cherrypy.log.error('Invalid broker address!')
                return None, None
            return broker_host, broker_port

        broker_username = loaded_properties['broker_username']
        broker_password = loaded_properties['broker_password']
        broker_host, broker_port = parse_address()

        credentials = pika.PlainCredentials(broker_username, broker_password)
        return pika.ConnectionParameters(broker_host, broker_port, '/', credentials)

    def register_custom_beans(self, broker_engine, args):
        return {'_amqp_connection_cache':{}}

    def after_setup(self, context, args):
        listeners_mappings = args.get('listeners_mappings', [])
        for m in listeners_mappings:
            m.bean.context = context
            m.bean.initialize()
            _register_listener(context, m.path, m.bean.on_message)


class BaseListener(object):
    def __init__(self):
        self.context = None

    def initialize(self):
        pass

    def on_message(self, channel, method, properties, body):
        pass


def get_connection(context):
    if threading.currentThread().name in context._amqp_connection_cache:
        return context._amqp_connection_cache[threading.currentThread().name]
    else:
        new_connection = pika.BlockingConnection(context.amqp_engine)
        context._amqp_connection_cache[threading.currentThread().name] = new_connection
        return new_connection


def send_message(context, routing_key, message, durable=True, exchange=''):
    sending_connection = get_connection(context).channel()
    sending_connection.queue_declare(queue=routing_key, durable=durable)
    sending_connection.basic_publish(exchange=exchange,
                                     routing_key=routing_key,
                                     body=message,
                                     properties=pika.BasicProperties(
                                         delivery_mode=2,
                                     ))


def _register_listener(context, routing_key, callback):
    thread_local_channel = get_connection(context).channel()

    def receive_action(channel, method, properties, body):
        try:
            callback(channel, method, properties, body)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            cherrypy.log.error('Error receiving message from queue {0}, exception: {1}'.format(routing_key, e))

    def listener_thread():
        thread_local_channel.queue_declare(queue=routing_key, durable=True)
        thread_local_channel.basic_qos(prefetch_count=1)
        thread_local_channel.basic_consume(receive_action, routing_key)
        thread_local_channel.start_consuming()

    thread = threading.Thread(target=listener_thread)
    thread.daemon = True
    thread.start()
