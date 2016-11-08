import unittest
import mock
import framepy.db
from assertpy import assert_that


class DbTest(unittest.TestCase):
    @mock.patch('sqlalchemy.orm.sessionmaker')
    def test_should_register_sessionmaker(self, sessionmaker):
        # given
        module = framepy.db.Module()
        db_engine = mock.MagicMock()
        sessionmaker_instance = mock.MagicMock()
        sessionmaker.return_value = sessionmaker_instance

        # when
        result = module.register_custom_beans(db_engine, None)

        # then
        assert_that(result['_session_maker']).is_equal_to(sessionmaker_instance)

    @mock.patch('sqlalchemy.orm.sessionmaker')
    def test_should_not_register_sessionmaker_if_empty_db_engine(self, sessionmaker):
        # given
        module = framepy.db.Module()
        db_engine = None

        # when
        result = module.register_custom_beans(db_engine, None)

        # then
        self.assertNotIn('_session_maker', result)

    def test_transation_successful(self):
        # given
        session = mock.MagicMock()

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
        assert_that(catched_exception).is_true()
