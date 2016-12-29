import functools
from framepy import core

annotated_beans = {}


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


class BeansInitializer(object):
    def __init__(self):
        self.initial_mappings = []
        for key, bean in annotated_beans.items():
            self.initial_mappings.append(core.Mapping(bean(), key))
        self.all_beans = {bean.path: bean.bean for bean in self.initial_mappings}

    def initialize_all(self, context):
        for key, bean in self.all_beans.items():
            self.initialize_bean(key, bean, context)

    def initialize_bean(self, target_bean_name, target_bean, context):
        try:
            target_bean.initialize(context)
        except Exception as e:
            raise BeanInitializationException("Cannot initialize bean '{0}'".format(target_bean_name), e)

        setattr(context, target_bean_name, target_bean)


class BeanInitializationException(Exception):
    pass


class AutowiredException(Exception):
    pass
