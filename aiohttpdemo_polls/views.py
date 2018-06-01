import aiohttp_jinja2
from aiohttp import web
import db
# app['db']=engine, table of question, table of choice.
# get_question(conn, question_id)
# vote(conn, question_id, choice_id)


'''
Handlers for different URLs are defined (see routes.py)

app.router.add_get('/', index)		
app.router.add_get('/poll/{question_id}', poll, name='poll')
app.router.add_get('/poll/{question_id}/results', results, name='results')

app.router.add_post('/poll/{question_id}/vote', vote, name='vote')'''


@aiohttp_jinja2.template('index.html')
async def index(request):
	async with request.app['db'].acquire() as conn:			# aiopg.sa.create_engine(URL)
		cursor = await conn.execute(db.question.select())	# table of question defined in db.py
		records = await cursor.fetchall() 
		questions = [dict(row) for row in records]		# https://stackoverflow.com/questions/10588375/can-i-assign-values-in-rowproxy-using-the-sqlalchemy
		return {'questions': questions}			# pass value of questions to the variable of questions in template of index.html.
'''
fetchall(), like aiopg.Cursor.fetchall(), but returns a list of RowProxy. 
RowProxy: a collections.abc.Mapping for representing a row in query result; Keys are column names, values are result values.
'''



@aiohttp_jinja2.template('detail.html')
async def poll(request):
	async with request.app['db'].acquire() as conn:
		question_id = request.match_info['question_id']
		
		try:
			question, choices = await db.get_question(conn, question_id)	# get_question() defined in db.py
		
		except db.RecordNotFound as e:			# class RecordNotFound defined in db.py
			raise web.HTTPNotFound(text=str(e))
		
		return {
			'question': question,
			'choices': choices
		}



@aiohttp_jinja2.template('results.html')
async def results(request):
	async with request.app['db'].acquire() as conn:
		question_id = request.match_info['question_id']

		try:
			question, choices = await db.get_question(conn, question_id)
		except db.RecordNotFound as e:
			raise web.HTTPNotFound(text=str(e))
		return {
			'question': question,
			'choices': choices
		}



async def vote(request):
	async with request.app['db'].acquire() as conn:
		question_id = int(request.match_info['question_id'])	# why int()
		data = await request.post()		# see detail.html -->  the post of <form>.

		try:
			choice_id = int(data['choice'])	# 'choice' is the name of <form><input>, value="{{ choice.id }}".
		except (KeyError, TypeError, ValueError) as e:
			raise web.HTTPBadRequest(text='You have not specified choice value') from e
		try:
			await db.vote(conn, question_id, choice_id)
		except db.RecordNotFound as e:
			raise web.HTTPNotFound(text=str(e))

		router = request.app.router		# get router info of app
		url = router['results'].url_for(question_id=str(question_id))
		# router['results']:   router.add_get('/poll/{question_id}/results', results, name='results')
		return web.HTTPFound(location=url)