import aiopg.sa
from sqlalchemy import (
	MetaData, 
	Table, 
	Column, 
	Integer, 
	String, 
	DateTime,
	ForeignKey
)
from sqlalchemy.sql import func


__all__ = ['question', 'choice']

meta = MetaData()


question = Table(
	'question', meta,

	Column('id', Integer, primary_key=True),
	Column('question_text', String(200), nullable=False),
	Column('pub_date', DateTime, default=func.now())
	)


choice = Table(
	'choice', meta,

	Column('id', Integer, primary_key=True),
	Column('choice_text', String, nullable=False),
	Column('votes', Integer, server_default="0", nullable=False),	# votes, default 0.

	Column('question_id', Integer, ForeignKey('question.id', ondelete='CASCADE'))	# when PrimaryKey item deleted, ForeignKey item also deleted.

	)


class RecordNotFound(Exception):
	"""Requested record in database was not found"""


async def init_pg(app):
	conf = app['config']['postgres']
	
	# aiopg.sa, async driver for PostgreSQL.
	engine = await aiopg.sa.create_engine(
		database=conf['database'],
		user=conf['user'],
		password=conf['password'],
		host=conf['host'],
		port=conf['port'],
		minsize=conf['minsize'],
		maxsize=conf['maxsize'],
	)

	app['db'] = engine 		# engine can directly use engine.connect()


async def close_pg(app):
	app['db'].close()
	await app['db'].wait_closed()


# c short for column (SQLAlchemy Expresssion Language)
async def get_question(conn, question_id):
	result = await conn.execute(
		question.select().where(question.c.id==question_id))	
	question_record = await result.first()
	
	if not question_record:
		msg = f'Question with id: {question_id} does not exists'
		raise RecordNotFound(msg)

	result = await conn.execute(
		choice.select().where(choice.c.question_id==question_id).order_by(choice.c.id))
	choice_records = await result.fetchall()
	return question_record, choice_records



'''http://docs.sqlalchemy.org/en/latest/core/dml.html#sqlalchemy.sql.expression.UpdateBase.returning'''
async def vote(conn, question_id, choice_id):
	result = await conn.execute(
		choice.update()
		.returning(*choice.c)
		.where(choice.c.question_id == question_id)
		.where(choice.c.id == choice_id)
		.values(votes = choice.c.votes+1))	# votes can be directly used.
	record = await result.fetchone()
	if not record:
		msg = f'Question with id {question_id} or choice with id: {choice_id} does not exist'
		raise RecordNotFound(msg)