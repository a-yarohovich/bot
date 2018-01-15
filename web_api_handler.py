import setup_path
import aiohttp
import async_timeout
from logger import logger
import global_event_loop as gloop


LOG = logger.LOG


class WebApiHandler(object):
    def __init__(self, config):
        self.sHost = config.get("Exchange", "host", fallback="api.binance.com")
        self.sUsername = config.get("Exchange", "username", fallback="guest")
        self.sPassword = config.get("Exchange", "password", fallback="guest")

    async def async_fetch_server_time(self):
        try:
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(10):
                    #async with session.get("https://api.binance.com/api/v1/time") as response:
                    async with session.get("http://google.com") as response:
                            return await response.text()
        except Exception as ex:
            LOG.error("Error with async_place_call: {}".format(ex.args[-1]))
            return None

    def fetch_server_time(self, on_fetch_server_time_cbk) -> bool:
        try:
            if not self.sHost:
                raise ValueError("Did't got host param from config")
            if not self.sUsername:
                raise ValueError("Did't got sUsername param from config")
            if not self.sPassword:
                raise ValueError("Did't got sPassword param from config")
            LOG.debug("Try to get binance server time")
            gloop.push_async_task(on_fetch_server_time_cbk, self.async_fetch_server_time)
        except Exception as ex:
            LOG.error("Error fired with fetch_server_time:{}".format(ex.args[-1]))
            return False
        return True
