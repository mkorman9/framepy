import core


class Module(object):
    name = '_beans'

    def __init__(self, annotated_beans):
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
            setattr(bean, 'context', context)
            if hasattr(bean, 'initialize'):
                bean.initialize()
