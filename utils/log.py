import os
import datetime
import yaml
import logging.config

log_conf = 'conf\\log.yaml'

LOG_DIR = os.path.join(os.getcwd(), 'logs')

def setup_logging(default_path=log_conf, default_level=logging.INFO):

    if os.path.exists("logs"):
        pass
    else:
        os.makedirs(LOG_DIR)

    path = default_path

    if os.path.exists(path):
        with open(path,'rt') as f:
            config = yaml.load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
        print('the input path doesn\'t exist')

setup_logging(default_path=log_conf)

logger = logging.getLogger()

