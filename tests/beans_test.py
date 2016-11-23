import unittest

from framepy import core

import framepy.beans
import framepy.core
from assertpy import assert_that


class BeansTest(unittest.TestCase):
    beans = framepy.beans.Module({})

    class ExampleBeanDummy(core.BaseBean):
        pass

    class ExampleBeanSpy(core.BaseBean):
        def __init__(self):
            super(BeansTest.ExampleBeanSpy, self).__init__()
            self.initialized = False

        def initialize(self, context):
            super(BeansTest.ExampleBeanSpy, self).initialize(context)
            self.initialized = True

    def test_bean_should_be_registered(self):
        # given
        beans_list = [
            framepy.core.Mapping(BeansTest.ExampleBeanDummy(), 'dummy')
        ]
        args = {'beans': beans_list}

        engine = self.beans.setup_engine(None, args)

        # when
        attributes = self.beans.register_custom_beans(engine, args)
        self.beans.after_setup('some_context', args)

        # then
        assert_that(attributes).contains('dummy')
        assert_that('some_context').is_equal_to(attributes['dummy'].context)

    def test_bean_should_be_registered_and_initialized(self):
        # given
        beans_list = [
            framepy.core.Mapping(BeansTest.ExampleBeanDummy(), 'dummy'),
            framepy.core.Mapping(BeansTest.ExampleBeanSpy(), 'example_bean')
        ]
        args = {'beans': beans_list}

        engine = self.beans.setup_engine(None, args)

        # when
        attributes = self.beans.register_custom_beans(engine, args)
        self.beans.after_setup('some_context', args)

        # then
        assert_that(attributes).contains('dummy')
        assert_that(attributes).contains('example_bean')
        assert_that(attributes['example_bean'].initialized).is_true()
        assert_that('some_context').is_equal_to(attributes['example_bean'].context)
