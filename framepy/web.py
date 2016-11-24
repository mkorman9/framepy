import json
import cherrypy
import inspect
import core
import modules

annotated_controllers = {}


class Module(modules.Module):
    def before_setup(self, properties, arguments, beans):
        pass

    def after_setup(self, properties, arguments, context, beans_initializer):
        controllers_mappings = [core.Mapping(controller(), key) for key, controller in annotated_controllers.iteritems()]

        for m in controllers_mappings:
            beans_initializer.initialize_bean('__controller_'.format(m.bean.__class__.__name__), m.bean, context)
            cherrypy.tree.mount(m.bean, m.path)


def controller(path):
    def wrapped(potential_controller_class):
        annotated_controllers[path] = potential_controller_class
        return potential_controller_class
    return wrapped


class FormEntity(object):
    def __init__(self, entries):
        self.__dict__.update(entries)


class ResponseEntity(object):
    class JsonEncoder(json.JSONEncoder):
        def default(self, o):
            return o.__dict__
    _json_encoder = JsonEncoder()

    def __init__(self, status='ok', data='', error=''):
        self.status = status
        if data != '':
            self.data = data
        if error != '':
            self.error = error

    def tojson(self):
        return ResponseEntity._json_encoder.encode(self)


class FormConstraint(object):
    def __init__(self, name, required=True, type='string', min=0, max=0xffffffff, default=None, nested=None):
        self.name = name
        self.required = required
        self.type = type
        self.min = min
        self.max = max
        self.default = default
        self.nested = nested


class FormBinder(object):
    def __init__(self, form, form_template):
        self.types_resolvers = {'int': self._resolve_int, 'float': self._resolve_float, 'string': self._resolve_string}
        self.errors = []
        self._form_template = form_template
        self._bind_form(form)

    def has_errors(self):
        return len(self.errors) > 0

    def _bind_form(self, form):
        constraints = [getattr(self._form_template, constraint)
                       for constraint in self._form_template.__dict__
                       if isinstance(getattr(self._form_template, constraint), FormConstraint)]
        fields = {}
        for constraint in constraints:
            value = form.get(constraint.name, None)
            value_to_bind = self._process_nested_form(value, constraint) if constraint.nested is not None \
                else self._process_fields(value, constraint)

            if value_to_bind is not None:
                fields[constraint.name] = value_to_bind

        self.entity = FormEntity(fields)

    def _process_nested_form(self, value, constraint):
        if value is None and constraint.required:
            self.errors.append({'field': constraint.name, 'error': 'MISSING_FIELD'})
            return None
        elif value is not None:
            another_binder = FormBinder(value, constraint.nested)
            if another_binder.has_errors():
                self.errors.extend(another_binder.errors)
            return another_binder.entity

    def _process_fields(self, value, constraint):
        if value is None and constraint.required:
            self.errors.append({'field': constraint.name, 'error': 'MISSING_FIELD'})
            return None
        elif value is None and not constraint.required:
            value = constraint.default

        if value is not None:
            try:
                type_resolver = self.types_resolvers.get(constraint.type)
                if type_resolver is not None:
                    type_resolver(value, constraint)
                else:
                    raise UnknowFieldType('Unknown field type {0}'.format(constraint.type))
            except ValueError:
                self.errors.append({'field': constraint.name, 'error': 'BAD_TYPE'})
        return value

    def _resolve_int(self, value, constraint):
        int(value)
        if value > constraint.max:
            self.errors.append({'field': constraint.name, 'error': 'MAX'})
        if value < constraint.min:
            self.errors.append({'field': constraint.name, 'error': 'MIN'})

    def _resolve_float(self, value, constraint):
        float(value)
        if value > constraint.max:
            self.errors.append({'field': constraint.name, 'error': 'MAX'})
        if value < constraint.min:
            self.errors.append({'field': constraint.name, 'error': 'MIN'})

    def _resolve_string(self, value, constraint):
        str(value)
        if len(value) > constraint.max:
            self.errors.append({'field': constraint.name, 'error': 'MAX_LENGTH'})
        if len(value) < constraint.min:
            self.errors.append({'field': constraint.name, 'error': 'MIN_LENGTH'})


class UnknowFieldType(Exception):
    pass


def form(form_template):
    def form_retriever(func):
        def wrapped(instance, *args, **kwargs):
            try:
                form_json = json.load(cherrypy.request.body)
            except ValueError:
                return ResponseEntity(status='error', error='Cannot parse request body')

            form_binder = FormBinder(form_json, form_template)
            kwargs.update({'form': form_binder})
            return func(instance, *args, **kwargs)
        return wrapped
    return form_retriever


def content_type(mime):
    def value_retriever(func):
        def wrapped(instance, *args, **kwargs):
            cherrypy.response.headers['Content-Type'] = mime
            return func(instance, *args, **kwargs)
        return wrapped
    return value_retriever


def exception_handler():
    cherrypy.response.status = 500
    cherrypy.response.headers['Content-Type'] = 'application/json'
    cherrypy.response.body = ResponseEntity(status='error', error='Internal error').tojson()


class BaseController(core.BaseBean):
    _cp_config = {'request.error_response': exception_handler,
                  'show_tracebacks': False,
                  'show_mismatched_params': False,
                  'throw_errors': False}

    def _set_bad_request_error(self):
        cherrypy.response.status = 400
        cherrypy.response.headers['Content-Type'] = 'application/json'

    @cherrypy.expose
    def default(self, *vpath, **params):
        def find_handling_method():
            return getattr(self, cherrypy.request.method, None)

        def setup_default_response_header():
            cherrypy.response.headers['Content-Type'] = 'application/json'

        def dispatch_event(method):
            if not method:
                cherrypy.response.status = 404
                return ResponseEntity(status='error', error="Not found")
            method_args = inspect.getargspec(method)
            if len(method_args.args) > 1 or method_args.varargs or method_args.keywords:
                result = method(*vpath, **params)
            else:
                result = method()
            return result

        try:
            setup_default_response_header()
            method = find_handling_method()
            result = dispatch_event(method)

            if cherrypy.response.headers['Content-Type'] == 'application/json':
                if result.status == 'error' and cherrypy.response.status != 404:
                    self._set_bad_request_error()
                return result.tojson()
            else:
                return result
        except ValueError:
            self._set_bad_request_error()
            return ResponseEntity(status='error', error='Bad Request').tojson()
