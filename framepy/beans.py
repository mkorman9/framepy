import functools
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
    def __init__(self):
        self.initial_mappings = []
        for key, bean in annotated_beans.items():
            self.initial_mappings.append(core.Mapping(bean(), key))
        self.all_beans = {bean.path: bean.bean for bean in self.initial_mappings}

    def update_beans(self, beans):
        self.all_beans.update(beans)

    def initialize_all(self, context):
        for key, bean in self.all_beans.items():
            self.initialize_bean(key, bean, context)

    def initialize_bean(self, target_bean_name, target_bean, context):
        try:
            if hasattr(target_bean, 'initialize'):
                target_bean.initialize(context)
        except Exception as e:
            raise BeanInitializationException("Cannot initialize bean '{0}'".format(target_bean_name), e)

        setattr(context, target_bean_name, target_bean)


class BeansConfigurationsResolver(object):
    def __init__(self):
        self._beans_to_create = {}
        for configuration_class in annotated_configurations:
            self._resolve_configuration_class(configuration_class)

    def get_beans(self):
        return self._beans_to_create

    def _resolve_configuration_class(self, configuration_class):
        beans_in_class = [getattr(configuration_class, property) for property in dir(configuration_class)
                          if callable(getattr(configuration_class, property)) and
                          hasattr(getattr(configuration_class, property), '_bean_key')]
        for bean in beans_in_class:
            self._beans_to_create[bean._bean_key] = bean()


class BeanInitializationException(Exception):
    pass


class AutowiredException(Exception):
    pass
