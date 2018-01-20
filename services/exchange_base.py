from logger import logger

LOG = logger.LOG
worker=None


class IExchangeBase(object):
    def run_worker(self):
        global worker
        worker = self

    def release(self):
        global worker
        if worker:
            del worker
