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
        assert_that(all(bean.initialized_with_context for bean in beans)).is_true()
        assert_that(all(bean.__class__ == StubA or bean.initialized_a == 'StubA' for bean in beans)).is_true()
        assert_that(all(bean.__class__ == StubB or bean.initialized_b == 'StubB' for bean in beans)).is_true()
        assert_that(all(bean.__class__ == StubC or bean.initialized_c == 'StubC' for bean in beans)).is_true()


class BaseBeanStub(framepy.BaseBean):
    def initialize(self, context):
        super(BaseBeanStub, self).initialize(context)
        self.initialized_with_context = context

    def set_a(self, bean):
        self.initialized_a = bean.__class__.__name__

    def set_b(self, bean):
        self.initialized_b = bean.__class__.__name__

    def set_c(self, bean):
        self.initialized_c = bean.__class__.__name__


class StubA(BaseBeanStub):
    pass


class StubB(BaseBeanStub):
    pass


class StubC(BaseBeanStub):
    pass
