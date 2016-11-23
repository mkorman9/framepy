
class Module(object):
    def before_setup(self, properties, arguments, beans):
        raise NotImplementedError()

    def after_setup(self, properties, arguments, context, beans_initializer):
        raise NotImplementedError()
