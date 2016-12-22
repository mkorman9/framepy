import framepy


@framepy.controller('')
class EmptyController(framepy.web.BaseController):
    pass


@framepy.controller('/data/sample')
class SampleDataController(framepy.web.BaseController):
    @framepy.web.method('GET')
    def get_sample_data(self):
        return framepy.web.ResponseEntity(data='ok')


@framepy.controller('/data/echo')
class ArgumentEchoController(framepy.web.BaseController):
    @framepy.web.method('GET')
    def echo_argument(self, argument):
        return framepy.web.ResponseEntity(data=argument)
