from configparser import ConfigParser
from logger import logger

LOG = logger.LOG
global_core_conf: ConfigParser = ConfigParser()


def init_global_config(filename: str):
    global_core_conf.read(filename)
    for section in global_core_conf.sections():  # Printing config
        LOG.info('{0}:{1}'.format(section, dict({item[0]: item[1] for item in global_core_conf.items(section)})))
