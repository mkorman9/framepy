import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative
import cherrypy
import contextlib


Table = sqlalchemy.ext.declarative.declarative_base()


class Module(object):
    name = 'db'

    def setup_engine(self, loaded_properties, args):
        database_url = loaded_properties.get('database_url')

        if database_url is None or not database_url:
            cherrypy.log.error('No database url found in properties. Skipping ORM engine creation.')
            return None

        # mysql+pymysql://{username}:{password}@url
        return sqlalchemy.create_engine(database_url)

    def register_custom_beans(self, db_engine, args):
        return {'_session_maker': sqlalchemy.orm.sessionmaker(bind=db_engine)} if db_engine is not None else {}

    def after_setup(self, context, args):
        pass


@contextlib.contextmanager
def transaction(context):
    session = None
    try:
        session = context._session_maker()
        yield session
        session.commit()
    except Exception as e:
        if session is not None:
            session.rollback()
        raise e
    finally:
        if session is not None:
            session.close()


class GenericRepository(object):
    def all(self, transaction):
        return transaction.query(self.__basetable__).all()

    def one(self, transaction, id):
        return transaction.query(self.__basetable__).filter(self.__basetable__.id == id).one()

    def add(self, transaction, entity):
        transaction.add(entity)

    def delete(self, transaction, entity):
        transaction.delete(entity)


class DataAccessException(Exception):
    pass
