import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative
import cherrypy
import contextlib
import modules

Table = sqlalchemy.ext.declarative.declarative_base()


class Module(modules.Module):
    def before_setup(self, properties, arguments, beans):
        database_url = properties.get('database_url')

        if database_url is None or not database_url:
            cherrypy.log.error('No database url found in properties. Skipping ORM engine creation.')
            return None

        # mysql+pymysql://{username}:{password}@url
        beans['db_engine'] = sqlalchemy.create_engine(database_url)
        beans['_session_maker'] = sqlalchemy.orm.sessionmaker(bind=beans['db_engine'])

    def after_setup(self, properties, arguments, context, beans_initializer):
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
