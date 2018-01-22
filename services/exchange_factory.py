from enum import Enum
from logger import logger
import exchange_base
import binance_worker

LOG = logger.LOG


class Exchanges(Enum):
    BINANCE = 1
    BITFINEX = 2


class ExchangeFactory(object):
    @staticmethod
    def create_exchange(exchange: Exchanges, config) -> exchange_base.IExchangeBase:
        if exchange == Exchanges.BINANCE:
            return binance_worker.BinanceWorker(config=config)
        elif exchange == Exchanges.BITFINEX:
            pass
