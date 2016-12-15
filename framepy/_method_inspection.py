import inspect


class MethodInspector(object):
    def __init__(self, method):
        self._args = inspect.getargspec(method)

    def contains_args(self):
        return len(self._args.args) > 1 or self._contains_varargs()

    def check_if_arguments_match_target_method(self, args, kwargs):
        if not self._contains_varargs() and (len(args) + len(kwargs) != len(self._arguments_without_special_ones())):
            raise ValueError('Provided arguments does not match target endpoint')

    def _arguments_without_special_ones(self):
        return list(filter(lambda arg: arg not in ['self', 'payload'], self._args.args))

    def _contains_varargs(self):
        return self._args.varargs or self._args.keywords
