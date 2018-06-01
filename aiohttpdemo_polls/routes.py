import pathlib
from views import index, poll, results, vote	# views.py contains defined handlers.


PROJECT_ROOT = pathlib.Path(__file__).parent	# PROJECT_ROOT: aiohttpdemo_polls



# router.add_route(method, path, handler, *, name=None, expect_handler=None)
# router.add_get(path, handler, *, name=None, allowe_head=True, **kwargs), shortcut for adding a GET handler.
# e.g.  router.add_get(path, handler, name='route') adds two routes: first for GET with name 'route' and second for HEAD with name 'route-head'.

def setup_routes(app):
	app.router.add_get('/', index, name='index')		# path: '/', handler:index.
	app.router.add_get('/poll/{question_id}', poll, name='poll')
	app.router.add_get('/poll/{question_id}/results', results, name='results')

	app.router.add_post('/poll/{question_id}/vote', vote, name='vote')	# router.add_post(path, handler, **kwargs)

	setup_static_routes(app)




# add_static(prefix, path, *, name=None, expect_handler=None,....)
# -prefix(str): URL path prefix for handled static files. 
# -path: path to the folder that contains handled static files, str or pathlib.Path.

def setup_static_routes(app):
	app.router.add_static('/static/', path=PROJECT_ROOT / 'static', name='static')

'''
Warning: Use add_static() for development only. 
In production, static content should be processed by web servers like nginx or apache.
'''