import unittest

from assertpy import assert_that
from mock import mock

from framepy import db


class DBTest(unittest.TestCase):
    @mock.patch('sqlalchemy.create_engine')
    @mock.patch('sqlalchemy.orm.sessionmaker')
    def test_should_create_db_connection(self, sessionmaker, create_engine):
        # given
        database_url = 'mysql+pymysql://test:test123@localhost/'
        properties = {
            'database_url': database_url
        }
        module = db.Module()
        beans = {}

        # when
        module.before_setup(properties, {}, beans)

        # then
        assert_that('_db_engine' in beans).is_true()
        assert_that('_session_maker' in beans).is_true()
        create_engine.assert_called_once_with(database_url)
        sessionmaker.assert_called_once_with(bind=beans['_db_engine'])

    def test_transaction_should_be_commited(self):
        # given
        context = mock.MagicMock()
        session = mock.MagicMock()
        context._session_maker.return_value = session

        # when
        with db.transaction(context):
            pass

        # then
        session.commit.assert_called_once()
        session.close.assert_called_once()

    def test_transaction_should_be_rolled_back_if_exception_is_raised(self):
        # given
        context = mock.MagicMock()
        session = mock.MagicMock()
        context._session_maker.return_value = session

        # when
        with self.assertRaises(Exception):
            with db.transaction(context):
                raise Exception()

        # then
        session.rollback.assert_called_once()
        session.close.assert_called_once()
