import unittest
import mock

import framepy.beans
from assertpy import assert_that


class BeansTest(unittest.TestCase):
    def setUp(self):
        framepy.beans.annotated_beans = {'a': StubA, 'b': StubB, 'c': StubC}

    def test_should_create_instances_of_existing_beans(self):
        # given when
        beans_initializer = framepy.beans.BeansInitializer()

        # then
        initialized_classes = {bean.__class__.__name__ for bean in beans_initializer.all_beans.values()}
        initialized_keys = set(beans_initializer.all_beans.keys())
        assert_that(initialized_keys).is_equal_to({'a', 'b', 'c'})
        assert_that(initialized_classes).is_equal_to({'StubA', 'StubB', 'StubC'})

    def test_all_beans_should_be_injected_and_initialized(self):
        # given
        beans_initializer = framepy.beans.BeansInitializer()
        context = mock.MagicMock()

        # when
        beans_initializer.initialize_all(context)

        # then
        beans = beans_initializer.all_beans.values()
        for v in beans:
            print(v.a())

        assert_that(all(bean.initialized_with_context for bean in beans)).is_true()
        assert_that(all(bean.a().__class__.__name__ == 'StubA' for bean in beans)).is_true()
        assert_that(all(bean.b().__class__.__name__ == 'StubB' for bean in beans)).is_true()
        assert_that(all(bean.c().__class__.__name__ == 'StubC' for bean in beans)).is_true()

    def test_exception_should_be_thrown_when_bean_cannot_be_initialized(self):
        # given
        framepy.beans.annotated_beans = {'invalidBean': StubThrowingExceptionOnInitialize}
        beans_initializer = framepy.beans.BeansInitializer()
        context = mock.MagicMock()

        # when then
        with self.assertRaises(framepy.beans.BeanInitializationException):
            beans_initializer.initialize_all(context)


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
