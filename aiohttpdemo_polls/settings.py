import argparse
import pathlib

import trafaret as T
from trafaret_config import commandline


TRAFARET = T.Dict({
	T.Key('postgres'):
		T.Dict({
			'database': T.String(),
			'user': T.String(),
			'password': T.String(),
			'host': T.String(),
			'port': T.Int(),
			'minsize': T.Int(),
			'maxsize': T.Int(),
			}),

	T.Key('host'): T.IP,
	T.Key('port'): T.Int(),
	})


BASE_DIR = pathlib.Path(__file__).parent.parent		# polls/aiohttpdemo_polls/settings
DEFAULT_CONFIG_PATH = BASE_DIR / 'config' / 'polls.yaml'


def get_config(argv=None):
	ap = argparse.ArgumentParser()
	commandline.standard_argparse_options(ap, default_config=DEFAULT_CONFIG_PATH) # ??

	# ignore unknown options
	options, unknown = ap.parse_known_args(argv)

	config = commandline.config_from_options(options, TRAFARET)
	return config