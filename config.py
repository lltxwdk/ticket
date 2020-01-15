import os
import yaml
import namedtupled
from utils.log import logger

def parsing_config():

    file = os.path.join(os.getcwd(),'conf\\config.yaml')
    
    with open(file, 'r', encoding='utf-8') as f:

        s = yaml.safe_load(f)

        
    return s

Config = namedtupled.map(parsing_config())

