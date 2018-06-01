from sqlalchemy import create_engine, MetaData

from aiohttpdemo_polls.db import question, choice
from aiohttpdemo_polls.settings import BASE_DIR, get_config


DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"


ADMIN_DB_URL = DSN.format(
	user='postgres', password='KOMADUAN', database='postgres',
	host='localhost', port=5432)
admin_engine = create_engine(ADMIN_DB_URL, isolation_level='AUTOCOMMIT')


USER_CONFIG_PATH = BASE_DIR / 'config' / 'polls.yaml'
USER_CONFIG = get_config(['-c', USER_CONFIG_PATH.as_posix()])	# Return a str representation of path with forward slashes (/).
USER_DB_URL = DSN.format(**USER_CONFIG['postgres'])
user_engine = create_engine(USER_DB_URL)


TEST_CONFIG_PATH = BASE_DIR / 'config' / 'polls_test.yaml'
TEST_CONFIG = get_config(['-c', TEST_CONFIG_PATH.as_posix()])
TEST_DB_URL = DSN.format(**TEST_CONFIG['postgres'])
test_engine = create_engine(TEST_DB_URL)


def setup_db(config):
	db_name = config['database']
	db_user = config['user']
	db_password = config['password']

	conn = admin_engine.connect()

	conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
	# conn.execute("CREATE USER IF NOT EXISTS %s WITH PASSWORD '%s'" % (db_user, db_password))
	conn.execute("CREATE DATABASE %s ENCODING 'UTF8'" % db_name)
	conn.execute("GRANT ALL PRIVILEGES ON DATABASE %s TO %s" % (db_name,db_user))

	conn.close()



def teardown_db(config):

	db_name = config['database']
	db_user = config['user']

	conn = admin_engine.connect()

	conn.execute("""
		SELECT pg_terminate_backend(pg_stat_activity.pid)
		FROM pg_stat_activity
		WHERE pg_stat_activity.datname = '%s'
			AND pid <> pg_backend_pid();""" % db_name)
	conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
	conn.execute("DROP ROLE IF EXISTS %s" % db_user)

	conn.close()



def create_tables(engine=test_engine):
	meta = MetaData()
	meta.create_all(bind=engine, tables=[question, choice])


def drop_tables(engine=test_engine):
	meta = MetaData()
	meta.drop_all(bind=engine, tables=[question, choice])



def sample_data(engine=test_engine):
	conn = engine.connect()

	conn.execute(question.insert(),[
		{'question_text': 'Where are you from?', 
		'pub_data': '2018-06-01 08:58:49.629+02'}
		])
	conn.execute(choice.insert(),[
		{'choice_text': 'Asia', 'votes': 0, 'question_id': 1},
		{'choice_text': 'Europe', 'votes': 0, 'question_id': 1},
		{'choice_text': 'USA', 'votes': 0, 'question_id': 1}
		])

	conn.close()


if __name__ == '__main__':
	setup_db(USER_CONFIG['postgres'])
	create_tables(engine=user_engine)
	sample_data(engine=user_engine)
	# drop_tables()
	# teardown_db(config)