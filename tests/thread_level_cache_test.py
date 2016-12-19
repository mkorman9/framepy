import unittest
import mock
from assertpy import assert_that

from framepy import _thread_level_cache


class ThreadLevelCacheTest(unittest.TestCase):
    def test_should_create_object_only_once_then_hit_cache(self):
        # given
        field_key = 'some_field'
        field_creation_procedure = mock.MagicMock()
        field_creation_procedure.return_value = 'some_value'

        # when
        object1 = _thread_level_cache.fetch_from_cache_or_create_new(field_key, field_creation_procedure)
        object2 = _thread_level_cache.fetch_from_cache_or_create_new(field_key, field_creation_procedure)

        # then
        field_creation_procedure.assert_called_once()
        assert_that(object1).is_equal_to(object2).is_equal_to('some_value')
