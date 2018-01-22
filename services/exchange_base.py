from logger import logger

LOG = logger.LOG


class IExchangeBase(object):
    def run_worker(self):
        pass

    def release(self):
        pass