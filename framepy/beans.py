import core


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
        for key, bean in self.all_beans.iteritems():
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
