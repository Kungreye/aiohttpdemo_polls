from aiohttp import web
import aiohttp_jinja2
import jinja2
import os

from settings import get_config
from db import init_pg, close_pg
from routes import setup_routes
from middlewares import setup_middlewares

import logging
import sys


async def init_app(argv=None):	# argv, is ??
	app = web.Application()		# aiohttp.web.Application object supports dict interface.

	app['config'] = get_config(argv)

	# setup jinja2 template renderer
	# aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('/path/to/templates/folder'))
	_templates_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
	aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(_templates_path))

	# create db connection on startup, shutdown on exit.
	app.on_startup.append(init_pg)
	app.on_cleanup.append(close_pg)

	# setup routes; routes direct to handlers (i.e. views.py in this demo).
	setup_routes(app)

	# setup middlewares
	setup_middlewares(app)

	return app


def main(argv):		# argv, what?
	logging.basicConfig(level=logging.DEBUG)

	app = init_app(argv)

	config = get_config(argv)
	web.run_app(app, 
				host=config['host'], 
				port=config['port'])	# this port is for app; different from psql's port.


if __name__ == '__main__':
	main(sys.argv[1:])