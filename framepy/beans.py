from framepy import core

annotated_beans = {}


def bean(key):
    def wrapped(potential_bean_class):
        annotated_beans[key] = potential_bean_class
        return potential_bean_class
    return wrapped


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
        for key, bean in self.all_beans.items():
            if bean != target_bean:
                property = 'set_' + key
                if hasattr(target_bean, property):
                    getattr(target_bean, property)(bean)

        try:
            target_bean.initialize(context)
        except Exception as e:
            raise BeanInitializationException("Cannot initialize bean '{0}'".format(target_bean_name), e)


class BeanInitializationException(Exception):
    pass
