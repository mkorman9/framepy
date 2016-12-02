import json
import cherrypy
import core
import modules
import _method_inspection

annotated_controllers = {}


class Module(modules.Module):
    def before_setup(self, properties, arguments, beans):
        self._map_controllers_from_arguments(arguments)

    def after_setup(self, properties, arguments, context, beans_initializer):
        controllers_mappings = [core.Mapping(controller(), key) for key, controller in annotated_controllers.iteritems()]

        for m in controllers_mappings:
            beans_initializer.initialize_bean('__controller_'.format(m.bean.__class__.__name__), m.bean, context)
            cherrypy.tree.mount(m.bean, m.path)

    def _map_controllers_from_arguments(self, arguments):
        controllers = arguments.get('controllers') or []
        for controller_class, path in controllers:
            annotated_controllers[path] = controller_class


def controller(path):
    def wrapped(potential_controller_class):
        annotated_controllers[path] = potential_controller_class
        return potential_controller_class
    return wrapped


class PayloadEntity(object):
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


class PayloadConstraint(object):
    def __init__(self, name, required=True, type='string', min=0, max=0xffffffff, default=None, nested=None):
        self.name = name
        self.required = required
        self.type = type
        self.min = min
        self.max = max
        self.default = default
        self.nested = nested


class PayloadBinder(object):
    def __init__(self, payload, payload_template):
        self.types_resolvers = {'int': self._resolve_int, 'float': self._resolve_float, 'string': self._resolve_string}
        self.errors = []
        self._payload_template = payload_template
        self._bind_payload(payload)

    def has_errors(self):
        return len(self.errors) > 0

    def _bind_payload(self, payload):
        constraints = [getattr(self._payload_template, constraint)
                       for constraint in self._payload_template.__dict__
                       if isinstance(getattr(self._payload_template, constraint), PayloadConstraint)]
        fields = {}
        for constraint in constraints:
            value = payload.get(constraint.name, None)
            value_to_bind = self._process_nested_payload(value, constraint) if constraint.nested is not None \
                else self._process_fields(value, constraint)

            if value_to_bind is not None:
                fields[constraint.name] = value_to_bind

        self.entity = PayloadEntity(fields)

    def _process_nested_payload(self, value, constraint):
        if value is None and constraint.required:
            self.errors.append({'field': constraint.name, 'error': 'MISSING_FIELD'})
            return None
        elif value is not None:
            another_binder = PayloadBinder(value, constraint.nested)
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
                    raise UnknownFieldType('Unknown field type {0}'.format(constraint.type))
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


class UnknownFieldType(Exception):
    pass


def payload(payload_template):
    def payload_retriever(func):
        def wrapped(instance, *args, **kwargs):
            try:
                payload_json = json.load(cherrypy.request.body)
            except ValueError:
                return ResponseEntity(status='error', error='Cannot parse request body')

            payload_binder = PayloadBinder(payload_json, payload_template)
            kwargs.update({'payload': payload_binder})
            return func(instance, *args, **kwargs)
        return wrapped
    return payload_retriever


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

    @cherrypy.expose
    def default(self, *vpath, **params):
        self._setup_default_response_header()
        try:
            method = self._find_handling_method()
            result = self._dispatch_event(method, vpath, params)

            if cherrypy.response.headers['Content-Type'] == 'application/json':
                if result.status == 'error' and cherrypy.response.status != 404:
                    self._set_bad_request_error()
                return result.tojson()
            else:
                return result
        except ValueError as e:
            self._set_bad_request_error()
            core.log.warning(e)
            return ResponseEntity(status='error', error='Bad Request').tojson()

    def _set_bad_request_error(self):
        self._setup_default_response_header()
        cherrypy.response.status = 400

    def _setup_default_response_header(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'

    def _find_handling_method(self):
        return getattr(self, cherrypy.request.method.upper(), None)

    def _call_target_method_with_matching_list_of_arguments(self, method, params, vpath):
        method_inspector = _method_inspection.MethodInspector(method)
        if method_inspector.contains_args():
            method_inspector.check_if_arguments_match_target_method(params, vpath)
            result = method(*vpath, **params)
        else:
            result = method()
        return result

    def _dispatch_event(self, method, vpath, params):
        if not method:
            cherrypy.response.status = 404
            return ResponseEntity(status='error', error="Not found")

        return self._call_target_method_with_matching_list_of_arguments(method, params, vpath)
