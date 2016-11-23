import core
import inspect


annotated_beans = {}


def bean(key):
    def wrapped(potential_bean_class):
        annotated_beans[key] = potential_bean_class
        return potential_bean_class
    return wrapped


class Module(object):
    name = '_beans'

    def __init__(self):
        self.initial_mappings = []
        for key, bean in annotated_beans.iteritems():
            self.initial_mappings.append(core.Mapping(bean(), key))
        self.all_beans = {}

    def setup_engine(self, loaded_properties, args):
        return self.initial_mappings + args.get('beans', [])

    def register_custom_beans(self, beans, args):
        self.all_beans = {bean.path: bean.bean for bean in beans}
        return self.all_beans

    def after_setup(self, context, args):
        for key, bean in self.all_beans.iteritems():
            self._initialize_bean(key, bean, context)

    def _initialize_bean(self, target_bean_name, target_bean, context):
        args_of_initialize = filter(lambda arg: arg not in ['self', 'context'],
                                    inspect.getargspec(target_bean.initialize).args)
        dependencies_to_inject = {'context': context}

        for arg_name in args_of_initialize:
            for key, bean in self.all_beans.iteritems():
                if arg_name == key and bean != target_bean:
                    dependencies_to_inject[key] = bean
                    break
            else:
                raise NoBeanToInjectException("Cannot inject bean with name '{0}' to {1}"
                                              .format(arg_name, target_bean.__class__.__name__))

        try:
            target_bean.initialize(**dependencies_to_inject)
        except Exception as e:
            raise BeanInitializationException("Cannot initialize bean '{0}'".format(target_bean_name), e)


class NoBeanToInjectException(Exception):
    pass


class BeanInitializationException(Exception):
    pass
