import unittest
from assertpy import assert_that
import mock

from framepy import testing
from framepy import db


class TestingFrameworkTest(unittest.TestCase):
    def test_should_mock_logic_by_appending_fake_context_and_mocking_transaction_api(self):
        # given
        context = mock.MagicMock()

        # when
        logic_object = testing.mock_logic(LogicStub, context)

        # then
        assert_that(logic_object.context).is_equal_to(context)
        assert_that(db.transaction(context)).is_type_of(testing.FakeTransactionContextManager)


class LogicStub(object):
    pass
