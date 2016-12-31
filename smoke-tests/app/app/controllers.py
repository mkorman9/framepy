import framepy


class PayloadTemplate(object):
    someVariable = framepy.web.PayloadConstraint('someVariable', required=True, type='string')
    someVariable2 = framepy.web.PayloadConstraint('someVariable2', required=True, type='string')


class PayloadTemplateWithValueToModify(object):
    value = framepy.web.PayloadConstraint('value', required=True, type='int')


@framepy.bean('incrementing_logic')
class IncrementingLogic(framepy.BaseBean):
    def increment_value(self, obj):
        obj.value += 1
        return obj


class DecrementingLogic(framepy.BaseBean):
    def decrement_value(self, obj):
        obj.value -= 1
        return obj


@framepy.configuration
class Configuration(object):
    @staticmethod
    @framepy.create_bean('decrementing_logic')
    def decrementing_logic():
        return DecrementingLogic()


@framepy.controller('')
class EmptyController(framepy.web.BaseController):
    pass


@framepy.controller('/get/sample')
class SampleDataController(framepy.web.BaseController):
    @framepy.web.method('GET')
    def get_sample_data(self):
        return framepy.web.ResponseEntity(data='ok')


@framepy.controller('/get/echo')
class ArgumentEchoController(framepy.web.BaseController):
    @framepy.web.method('GET')
    def echo_argument(self, argument):
        return framepy.web.ResponseEntity(data=argument)


@framepy.controller('/post/echo')
class PayloadEchoController(framepy.web.BaseController):
    @framepy.web.payload('payload', PayloadTemplate)
    @framepy.web.method('POST')
    def echo_data(self, payload):
        return framepy.web.ResponseEntity(data=payload)


@framepy.controller('/post/increment')
class PayloadIncrementingLogicController(framepy.web.BaseController):
    @framepy.autowired('incrementing_logic')
    def logic(self):
        pass

    @framepy.web.payload('payload', PayloadTemplateWithValueToModify)
    @framepy.web.method('POST')
    def increment_value(self, payload):
        return framepy.web.ResponseEntity(data=self.logic().increment_value(payload))


@framepy.controller('/post/decrement')
class PayloadDecrementingLogicController(framepy.web.BaseController):
    @framepy.autowired('decrementing_logic')
    def logic(self):
        pass

    @framepy.web.payload('payload', PayloadTemplateWithValueToModify)
    @framepy.web.method('POST')
    def increment_value(self, payload):
        return framepy.web.ResponseEntity(data=self.logic().decrement_value(payload))
