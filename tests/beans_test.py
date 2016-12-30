import unittest
import mock

import framepy
from framepy import beans
from framepy import core
from assertpy import assert_that


class BeansTest(unittest.TestCase):
    def setUp(self):
        self.annotated_beans = {'a': StubA, 'b': StubB, 'c': StubC}
        beans.annotated_beans = {}
        beans.annotated_configurations = []

    def test_should_create_instances_of_existing_beans(self):
        # given
        context = core.Context({})

        # when
        beans_resolver = beans.BeansResolver(framepy.beans.BeansInitializer(), self.annotated_beans, {})
        beans_resolver.resolve(context)

        # then
        all_beans_keys = [property for property in dir(context) if not property.startswith('_')]
        all_beans = [getattr(context, property) for property in dir(context) if not property.startswith('_')]
        initialized_classes = {bean.__class__.__name__ for bean in all_beans}
        initialized_keys = set(all_beans_keys)
        assert_that(initialized_keys).is_equal_to({'a', 'b', 'c'})
        assert_that(initialized_classes).is_equal_to({'StubA', 'StubB', 'StubC'})

    def test_all_beans_should_be_injected_and_initialized(self):
        # given
        beans_resolver = framepy.beans.BeansResolver(framepy.beans.BeansInitializer(), self.annotated_beans, {})
        context = core.Context({})

        # when
        beans_resolver.resolve(context)

        # then
        beans = [getattr(context, property) for property in dir(context) if not property.startswith('_')]
        assert_that(all(bean.initialized_with_context for bean in beans)).is_true()
        assert_that(all(bean.a().__class__.__name__ == 'StubA' for bean in beans)).is_true()
        assert_that(all(bean.b().__class__.__name__ == 'StubB' for bean in beans)).is_true()
        assert_that(all(bean.c().__class__.__name__ == 'StubC' for bean in beans)).is_true()

    def test_exception_should_be_thrown_when_bean_cannot_be_initialized(self):
        # given
        beans.annotated_beans = {'invalidBean': StubThrowingExceptionOnInitialize}
        beans_initializer = beans.BeansResolver(framepy.beans.BeansInitializer(), beans.annotated_beans, {})
        context = mock.MagicMock()

        # when then
        with self.assertRaises(beans.BeanInitializationException):
            beans_initializer.resolve(context)

    def test_should_detect_configuration_class_and_add_it_to_list(self):
        # given
        @beans.configuration
        class TestConfiguration(object):
            pass

        # when then
        assert_that(beans.annotated_configurations).is_equal_to([TestConfiguration])

    def test_should_create_bean_from_method(self):
        # given
        @beans.configuration
        class TestConfiguration(object):
            @staticmethod
            @beans.create_bean('bean')
            def bean():
                return 'sample bean'

        resolver = beans.BeansResolver(framepy.beans.BeansInitializer(), beans.annotated_beans,
                                       beans.annotated_configurations)
        context = core.Context({})

        # when
        resolver.resolve(context)

        # then
        assert_that(context.bean).is_equal_to('sample bean')

    def test_should_create_bean_from_parametrized_method(self):
        # given
        @beans.configuration
        class TestConfiguration(object):
            @staticmethod
            @beans.create_bean('bean')
            def bean():
                return 'sample bean'

            @staticmethod
            @beans.create_bean('bean2')
            def bean2(bean):
                return bean + '2'

        resolver = beans.BeansResolver(framepy.beans.BeansInitializer(), beans.annotated_beans,
                                       beans.annotated_configurations)
        context = core.Context({})

        # when
        resolver.resolve(context)

        # then
        assert_that(context.bean).is_equal_to('sample bean')
        assert_that(context.bean2).is_equal_to('sample bean2')


class BaseBeanStub(framepy.BaseBean):
    def initialize(self, context):
        super(BaseBeanStub, self).initialize(context)
        self.initialized_with_context = context

    @framepy.autowired('a')
    def a(self):
        pass

    @framepy.autowired('b')
    def b(self):
        pass

    @framepy.autowired('c')
    def c(self):
        pass


class StubA(BaseBeanStub):
    pass


class StubB(BaseBeanStub):
    pass


class StubC(BaseBeanStub):
    pass


class StubThrowingExceptionOnInitialize(BaseBeanStub):
    def initialize(self, context):
        super(StubThrowingExceptionOnInitialize, self).initialize(context)
        raise Exception()
