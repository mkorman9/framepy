import functools

from framepy import _method_inspection

from framepy import core

annotated_beans = {}
annotated_configurations = []


def bean(key):
    def wrapped(potential_bean_class):
        annotated_beans[key] = potential_bean_class
        return potential_bean_class
    return wrapped


def autowired(key):
    def autowired_decorator(method):

        @functools.wraps(method)
        def wrapped(self):
            if not hasattr(self, 'context'):
                raise AutowiredException('Cannot autowire dependency to non-bean object')
            if not hasattr(self.context, key):
                raise AutowiredException("Bean '{}' does not exist in context".format(key))
            return getattr(self.context, key)
        return wrapped
    return autowired_decorator


def configuration(configuration_class):
    annotated_configurations.append(configuration_class)
    return configuration_class


def create_bean(key):
    def create_bean_decorator(method):
        method._bean_key = key
        return method
    return create_bean_decorator


class BeansInitializer(object):
    def initialize(self, context, beans_list):
        for bean_name, bean in beans_list.items():
            try:
                if hasattr(bean, 'initialize'):
                    bean.initialize(context)
            except Exception as e:
                raise BeanInitializationException("Cannot initialize bean '{0}'".format(bean_name), e)

            setattr(context, bean_name, bean)

    def initialize_single_bean(self, bean_name, bean_object, context):
        self.initialize(context, {bean_name: bean_object})


class BeansResolver(object):
    def __init__(self, beans_initializer, bean_classes, bean_configuration_classes):
        self._beans_initializer = beans_initializer
        self._bean_classes = bean_classes
        self._bean_configuration_classes = bean_configuration_classes
        self._initialized_beans = {}

    def resolve(self, context):
        instantiated_class_beans = self._instantiate_bean_classes()
        self._beans_initializer.initialize(context, instantiated_class_beans)

        instantiated_configuration_beans = self._instantiate_beans_within_configurations()
        self._beans_initializer.initialize(context, instantiated_configuration_beans)

    def _instantiate_bean_classes(self):
        instantiated_beans = {}
        for bean_name, bean_class in self._bean_classes.items():
            instantiated_beans[bean_name] = bean_class()
        return instantiated_beans

    def _instantiate_beans_within_configurations(self):
        instantiated_beans = {}
        for configuration_class in self._bean_configuration_classes:
            methods_creating_beans = [getattr(configuration_class, property) for property in dir(configuration_class)
                                      if callable(getattr(configuration_class, property)) and
                                      hasattr(getattr(configuration_class, property), '_bean_key')]
            for method_creating_bean in methods_creating_beans:
                instantiated_beans[method_creating_bean._bean_key] = method_creating_bean()
        return instantiated_beans




class BeanInitializationException(Exception):
    pass


class AutowiredException(Exception):
    pass
