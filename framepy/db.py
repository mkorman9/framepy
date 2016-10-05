import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative


Table = sqlalchemy.ext.declarative.declarative_base()


class Module(object):
    name = 'db'

    def setup_engine(self, loaded_properties, args):
        database_url = loaded_properties['database_url']
        database_username = loaded_properties['database_username']
        database_password = loaded_properties['database_password']

        if database_url is None:
            cherrypy.log.error('No database url found in properties. Skipping ORM engine creation.')
            return None

        database_url = database_url.replace('jdbc:mysql://',
                                            'mysql+pymysql://{0}:{1}@'.format(database_username, database_password))
        return sqlalchemy.create_engine(database_url)

    def register_custom_beans(self, db_engine, args):
        return {'_session_maker': sqlalchemy.orm.sessionmaker(bind=db_engine)} if db_engine is not None else {}

    def after_setup(self, context, args):
        pass


def transactional(context):
    def transactional_pack(func):
        def modify_kwargs(kwargs, session):
            new_kwargs = kwargs.copy()
            new_kwargs['session'] = session
            return new_kwargs

        def run_in_transaction(*args, **kwargs):
            session, result = None, None
            try:
                session = context._session_maker()
                result = func(*args, **modify_kwargs(kwargs, session))
                session.commit()
            except Exception as e:
                if session is not None:
                    session.rollback()
                raise e
            finally:
                if session is not None:
                    session.close()
            return result
        return run_in_transaction
    return transactional_pack


class DataAccessException(Exception):
    pass
