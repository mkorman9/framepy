import unittest
import mock
import framepy.db


class DbTest(unittest.TestCase):
    def test_transation_successful(self):
        # given
        session = mock.MagicMock()
        session.commit = mock.MagicMock()
        session.rollback = mock.MagicMock()
        session.close = mock.MagicMock()

        context = mock.MagicMock()
        context._session_maker = mock.MagicMock(return_value=session)

        # when
        with framepy.db.transaction(context) as session:
            pass

        # then
        session.commit.assert_called_once_with()
        session.rollback.assert_not_called()
        session.close.assert_called_once_with()

    def test_transation_failing(self):
        # given
        session = mock.MagicMock()
        session.commit = mock.MagicMock()
        session.rollback = mock.MagicMock()
        session.close = mock.MagicMock()

        context = mock.MagicMock()
        context._session_maker = mock.MagicMock(return_value=session)

        catched_exception = False

        # when
        try:
            with framepy.db.transaction(context) as session:
                raise Exception
        except Exception:
            catched_exception = True

        # then
        session.commit.assert_not_called()
        session.rollback.assert_called_once_with()
        session.close.assert_called_once_with()
        self.assertTrue(catched_exception)
