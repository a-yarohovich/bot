import asyncio
from logger import logger
from core import global_event_loop as gloop


LOG = logger.LOG


class Timer(object):
    def __init__(self, callback, timeout_sec: int):
        self._timeout = timeout_sec
        self._callback = callback
        self._task = None

    def start(self) -> bool:
        async def _async_f():
            try:
                await asyncio.sleep(self._timeout)
            except Exception as ex:
                LOG.error("Error with async_start_timer: {}".format(ex.args[-1]))
                return None

        try:
            if not self._callback:
                raise ValueError("Did't got callback param")
            if not self._timeout:
                raise ValueError("Did't got timeout param")
            LOG.debug("Starting timer for callback:{} and timeout:{}".format(self._callback, self._timeout))
            self._task = gloop.push_async_task(self._callback, _async_f)
        except Exception as ex:
            LOG.error("Error fired with fetch_server_time:{}".format(ex.args[-1]))
            return False
        return True

    def cancel(self):
        self._task.cancel()