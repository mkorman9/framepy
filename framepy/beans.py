class Module(object):
    name = '_beans'

    def setup_engine(self, loaded_properties, args):
        return args.get('beans', [])

    def register_custom_beans(self, beans, args):
        return {bean.path: bean.bean for bean in beans}

    def after_setup(self, context, args):
        for bean in args.get('beans', []):
            setattr(bean.bean, 'context', context)
            if hasattr(bean.bean, 'initialize'):
                bean.bean.initialize()
