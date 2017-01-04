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

    def test_data_access_exception(self):
        # given
        message = 'some message'

        # when
        exception = db.DataAccessException(message)

        # then
        assert_that(exception.message).is_equal_to(message)


class GenericRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.repository = db.GenericRepository()
        self.repository.__basetable__ = mock.MagicMock()

        self.transaction = mock.MagicMock()

    def test_should_query_for_all_entities(self):
        # given

        # when
        self.repository.all(self.transaction)

        # then
        query = self.transaction.query
        query.assert_called_once_with(self.repository.__basetable__)
        query.return_value.all.assert_called_once_with()

    def test_should_query_for_filtered_entities(self):
        # given
        condition = mock.MagicMock()

        # when
        self.repository.find(self.transaction, condition)

        # then
        query = self.transaction.query
        query.assert_called_once_with(self.repository.__basetable__)
        query.return_value.filter.assert_called_once_with(condition)
        query.return_value.filter.return_value.all.assert_called_once_with()

    def test_should_query_for_single_entity(self):
        # given
        id = self.repository.__basetable__.id

        # when
        self.repository.one(self.transaction, id)

        # then
        query = self.transaction.query
        query.assert_called_once_with(self.repository.__basetable__)
        query.return_value.filter.assert_called_once_with(True)
        query.return_value.filter.return_value.one.assert_called_once_with()

    def test_should_add_single_entity(self):
        # given
        entity = mock.MagicMock()

        # when
        self.repository.add(self.transaction, entity)

        # then
        self.transaction.add.assert_called_once_with(entity)

    def test_should_delete_single_entity(self):
        # given
        entity = mock.MagicMock()

        # when
        self.repository.delete(self.transaction, entity)

        # then
        self.transaction.delete.assert_called_once_with(entity)
