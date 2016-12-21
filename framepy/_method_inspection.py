import inspect


class MethodInspector(object):
    def __init__(self, method):
        self._args = inspect.signature(method).parameters

    def contains_args(self):
        return len(self._args) > 0

    def check_if_arguments_match_target_method(self, args, kwargs):
        if not self._contains_varargs() and (len(args) + len(kwargs) != len(self._arguments_without_special_ones())):
            raise ValueError('Provided arguments does not match target endpoint')

    def _arguments_without_special_ones(self):
        return list(filter(lambda arg: arg not in ['self', 'payload'], self._args.keys()))

    def _contains_varargs(self):
        for arg_name in self._args:
            if self._args[arg_name].kind == inspect.Parameter.VAR_KEYWORD or \
                            self._args[arg_name].kind == inspect.Parameter.VAR_POSITIONAL:
                return True
        return False
