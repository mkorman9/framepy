import unittest
import framepy.beans
import framepy.core


class BeansTest(unittest.TestCase):
    beans = framepy.beans.Module()

    class ExampleBeanDummy(object):
        pass

    class ExampleBeanSpy(object):
        def __init__(self):
            self.initialized = False

        def initialize(self):
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
        self.assertTrue('dummy' in attributes)
        self.assertEqual('some_context', attributes['dummy'].context)

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
        self.assertTrue('dummy' in attributes)
        self.assertTrue('example_bean' in attributes)
        self.assertTrue(attributes['example_bean'].initialized)
        self.assertEqual('some_context', attributes['example_bean'].context)
