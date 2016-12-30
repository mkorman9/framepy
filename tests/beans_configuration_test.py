import unittest

from assertpy import assert_that
from mock import mock

from framepy import beans


class BeansConfigurationTest(unittest.TestCase):
    def setUp(self):
        beans.annotated_beans = {}
        beans.annotated_configurations = []

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

        initializer = beans.BeansInitializer()
        resolver = beans.BeansConfigurationsResolver(initializer)
        context = mock.MagicMock()

        # when
        resolver.resolve()
        initializer.initialize_all(context)

        # then
        assert_that(context.bean).is_equal_to('sample bean')
