import asyncio
import aiohttp
import async_timeout
import hmac
import hashlib
import json
import time
from typing import List
from core import global_event_loop as gloop
from logger import logger


LOG = logger.LOG


class BinanceApiEnums(object):
    KLINE_INTERVAL_1MINUTE = '1m'
    KLINE_INTERVAL_3MINUTE = '3m'
    KLINE_INTERVAL_5MINUTE = '5m'
    KLINE_INTERVAL_15MINUTE = '15m'
    KLINE_INTERVAL_30MINUTE = '30m'
    KLINE_INTERVAL_1HOUR = '1h'
    KLINE_INTERVAL_2HOUR = '2h'
    KLINE_INTERVAL_4HOUR = '4h'
    KLINE_INTERVAL_6HOUR = '6h'
    KLINE_INTERVAL_8HOUR = '8h'
    KLINE_INTERVAL_12HOUR = '12h'
    KLINE_INTERVAL_1DAY = '1d'
    KLINE_INTERVAL_3DAY = '3d'
    KLINE_INTERVAL_1WEEK = '1w'
    KLINE_INTERVAL_1MONTH = '1M'

    ORDER_TYPE_LIMIT = 'LIMIT'
    ORDER_TYPE_MARKET = 'MARKET'
    ORDER_TYPE_STOP_LOSS = 'STOP_LOSS'
    ORDER_TYPE_STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
    ORDER_TYPE_TAKE_PROFIT = 'TAKE_PROFIT'
    ORDER_TYPE_TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
    ORDER_TYPE_LIMIT_MAKER = 'LIMIT_MAKER'

    ORDER_SIDE_BUY = 'BUY'
    ORDER_SIDE_SELL = 'SELL'

    TIME_IN_FORCE_GTC = 'GTC'  # Good till cancelled
    TIME_IN_FORCE_IOC = 'IOC'  # Immediate or cancel
    TIME_IN_FORCE_FOK = 'FOK'  # Fill or kill

    ORDER_STATUS_NEW = 'NEW'
    ORDER_STATUS_PARTIALLY_FILLED = 'PARTIALLY_FILLED'
    ORDER_STATUS_FILLED = 'FILLED'
    ORDER_STATUS_CANCELED = 'CANCELED'
    ORDER_STATUS_PENDING_CANCEL = 'PENDING_CANCEL'
    ORDER_STATUS_REJECTED = 'REJECTED'
    ORDER_STATUS_EXPIRED = 'EXPIRED'

    SYMBOL_TYPE_SPOT = 'SPOT'


class BinanceRestApi(object):
    def __init__(self, config):
        if not config:
            raise ValueError("Did't got correct config")
        self._host: str = config.get("Exchange", "host", fallback="https://api.binance.com")
        self._api_key: str = config.get("Exchange", "api_key", fallback=None)
        self._secret_key: str = config.get("Exchange", "secret", fallback=None)
        self._request_timeout = 5

    def ping_server(self, callback) -> asyncio.Task:
        """
        :return: {}
        """

        async def _async_ping_server():
            try:
                async with aiohttp.ClientSession() as session:
                    with async_timeout.timeout(self._request_timeout):
                        async with session.get("https://api.binance.com/api/v1/ping") as response:
                            return await response.text()
            except Exception as exc:
                LOG.error("Error with _async_ping: {}".format(exc.args[-1]))
                return None

        try:
            if not self._host:
                raise ValueError("Did't got host param from config")
            LOG.debug("Try to get ping from server")
            return gloop.push_async_task(callback, _async_ping_server)
        except Exception as ex:
            LOG.error("Error fired with ping server:{}".format(ex.args[-1]))

    def fetch_server_time(self, callback) -> asyncio.Task:
        """
        :return:
        {
          "serverTime": 1499827319559
        }
        """

        async def _async_fetch_server_time():
            try:
                async with aiohttp.ClientSession() as session:
                    with async_timeout.timeout(self._request_timeout):
                        async with session.get("https://api.binance.com/api/v1/time") as response:
                            return await response.text()
            except Exception as exc:
                LOG.error("Error with _async_fetch_server_time: {}".format(exc.args[-1]))
                return None

        try:
            if not self._host:
                raise ValueError("Did't got host param from config")
            LOG.debug("Try to get binance server time")
            return gloop.push_async_task(callback, _async_fetch_server_time)
        except Exception as ex:
            LOG.error("Error fired with fetch_server_time:{}".format(ex.args[-1]))

    def exchange_info(self, callback) -> asyncio.Task:
        """
        :return:
        {
          "timezone": "UTC",
          "serverTime": 1508631584636,
          "rateLimits": [{
              "rateLimitType": "REQUESTS",
              "interval": "MINUTE",
              "limit": 1200
            },
            {
              "rateLimitType": "ORDERS",
              "interval": "SECOND",
              "limit": 10
            },
            {
              "rateLimitType": "ORDERS",
              "interval": "DAY",
              "limit": 100000
            }
          ],
          "exchangeFilters": [],
          "symbols": [{
            "symbol": "ETHBTC",
            "status": "TRADING",
            "baseAsset": "ETH",
            "baseAssetPrecision": 8,
            "quoteAsset": "BTC",
            "quotePrecision": 8,
            "orderTypes": ["LIMIT", "MARKET"],
            "icebergAllowed": false,
            "filters": [{
              "filterType": "PRICE_FILTER",
              "minPrice": "0.00000100",
              "maxPrice": "100000.00000000",
              "tickSize": "0.00000100"
            }, {
              "filterType": "LOT_SIZE",
              "minQty": "0.00100000",
              "maxQty": "100000.00000000",
              "stepSize": "0.00100000"
            }, {
              "filterType": "MIN_NOTIONAL",
              "minNotional": "0.00100000"
            }]
          }]
        }
        """

        async def _async_exchange_info():
            try:
                async with aiohttp.ClientSession() as session:
                    with async_timeout.timeout(self._request_timeout):
                        async with session.get("https://api.binance.com/api/v1/exchangeInfo") as response:
                            return await response.text()
            except Exception as exc:
                LOG.error("Error with _async_exchange_info: {}".format(exc.args[-1]))
                return None

        try:
            if not self._host:
                raise ValueError("Did't got host param from config")
            LOG.debug("Try to get exchange_info from server")
            return gloop.push_async_task(callback, _async_exchange_info)
        except Exception as ex:
            LOG.error("Error fired with exchange_info:{}".format(ex.args[-1]))

    def fetch_order_book(self, callback, symbol: str, limit: int = None) -> asyncio.Task:
        """
        :input:
        Name 	Type 	Mandatory 	Description
        symbol 	STRING 	YES
        limit 	INT 	NO 	        Default 100; max 1000. Valid limits:[5, 10, 20, 50, 100, 500, 1000]

        :return:
        {
          "lastUpdateId": 1027024,
          "bids": [
            [
              "4.00000000",     // PRICE
              "431.00000000",   // QTY
              []                // Ignore.
            ]
          ],
          "asks": [
            [
              "4.00000200",
              "12.00000000",
              []
            ]
          ]
        }
        """

        async def _async_fetch_order_book():
            try:
                query = "https://api.binance.com/api/v1/depth?symbol={}".format(str(limit))
                if limit:
                    query += "&limit={}".format(str(limit))
                async with aiohttp.ClientSession() as session:
                    with async_timeout.timeout(self._request_timeout):
                        async with session.get(query) as response:
                            return await response.text()
            except Exception as exc:
                LOG.error("Error with _async_fetch_order_book: {}".format(exc.args[-1]))
                return None

        try:
            if not symbol:
                raise ValueError("Did't got mandatory param symbol: {}".format(symbol))
            if not self._host:
                raise ValueError("Did't got host param from config")
            LOG.debug("Try to get order book by symbol {}".format(symbol))
            return gloop.push_async_task(callback, _async_fetch_order_book)
        except Exception as ex:
            LOG.error("Error fired with fetch_order_book:{}".format(ex.args[-1]))

    def fetch_trades_list(self, callback, symbol: str, limit: int = None) -> asyncio.Task:
        """
        :input:
        Name 	Type 	Mandatory 	Description
        symbol 	STRING 	YES
        limit 	INT 	NO 	        Default 500; max 500.

        :return:
        [
          {
            "id": 28457,
            "price": "4.00000100",
            "qty": "12.00000000",
            "time": 1499865549590,
            "isBuyerMaker": true,
            "isBestMatch": true
          }
        ]
        """

        async def _async_fetch_trades_list():
            try:
                query = "https://api.binance.com/api/v1/trades?symbol={}".format(symbol)
                if limit:
                    query += "&limit={}".format(str(limit))
                async with aiohttp.ClientSession() as session:
                    with async_timeout.timeout(self._request_timeout):
                        async with session.get(query) as response:
                            return await response.text()
            except Exception as exc:
                LOG.error("Error with _async_fetch_trades_list: {}".format(exc.args[-1]))
                return None

        try:
            if not symbol:
                raise ValueError("Did't got mandatory param symbol: {}".format(symbol))
            if not self._host:
                raise ValueError("Did't got host param from config")
            LOG.debug("Try to get order book by symbol {}".format(symbol))
            return gloop.push_async_task(callback, _async_fetch_trades_list)
        except Exception as ex:
            LOG.error("Error fired with fetch_trades_list:{}".format(ex.args[-1]))

    def fetch_agg_trades(
            self,
            callback,
            symbol: str,
            from_id: int = None,
            start_time: int = None,
            end_time: int = None,
            limit: int = None
    ) -> asyncio.Task:
        """
        Get compressed, aggregate trades.
        Trades that fill at the time, from the same order, with the same price will have the quantity aggregated.

        :input:
        Name 	    Type 	Mandatory 	Description
        symbol 	    STRING 	YES
        fromId 	    LONG 	NO 	        ID to get aggregate trades from INCLUSIVE.
        startTime 	LONG 	NO 	        Timestamp in ms to get aggregate trades from INCLUSIVE.
        endTime 	LONG 	NO 	        Timestamp in ms to get aggregate trades until INCLUSIVE.
        limit 	    INT 	NO 	        Default 500; max 500.

        :return:
        [
          {
            "a": 26129,         // Aggregate tradeId
            "p": "0.01633102",  // Price
            "q": "4.70443515",  // Quantity
            "f": 27781,         // First tradeId
            "l": 27781,         // Last tradeId
            "T": 1498793709153, // Timestamp
            "m": true,          // Was the buyer the maker?
            "M": true           // Was the trade the best price match?
          }
        ]
        """

        async def _async_fetch_agg_trades():
            try:
                query = "https://api.binance.com/api/v1/aggTrades?symbol={0}".format(symbol)
                if from_id:
                    query += "&fromId={}".format(from_id)
                if start_time:
                    query += "&startTime={}".format(start_time)
                if end_time:
                    query += "&endTime={}".format(end_time)
                if limit:
                    query += "&limit={}".format(str(limit))
                async with aiohttp.ClientSession() as session:
                    with async_timeout.timeout(self._request_timeout):
                        async with session.get(query) as response:
                            return await response.text()
            except Exception as exc:
                LOG.error("Error with _async_fetch_agg_trades: {}".format(exc.args[-1]))
                return None

        try:
            if not symbol:
                raise ValueError("Did't got mandatory param symbol: {}".format(symbol))
            if not self._host:
                raise ValueError("Did't got host param from config")
            LOG.debug("Try to get aggregate trades list by symbol {}".format(symbol))
            return gloop.push_async_task(callback, _async_fetch_agg_trades)
        except Exception as ex:
            LOG.error("Error fired with fetch_agg_trades:{}".format(ex.args[-1]))

    def fetch_ticker_24h(self, callback, symbol: str = None) -> asyncio.Task:
        """
        :param symbol: symbol
        :param callback: callback

        :input:
        Name 	Type 	Mandatory 	Description
        symbol 	STRING 	NO

        :return:
        {
          "symbol": "BNBBTC",
          "priceChange": "-94.99999800",
          "priceChangePercent": "-95.960",
          "weightedAvgPrice": "0.29628482",
          "prevClosePrice": "0.10002000",
          "lastPrice": "4.00000200",
          "lastQty": "200.00000000",
          "bidPrice": "4.00000000",
          "askPrice": "4.00000200",
          "openPrice": "99.00000000",
          "highPrice": "100.00000000",
          "lowPrice": "0.10000000",
          "volume": "8913.30000000",
          "quoteVolume": "15.30000000",
          "openTime": 1499783499040,
          "closeTime": 1499869899040,
          "fristId": 28385,   // First tradeId
          "lastId": 28460,    // Last tradeId
          "count": 76         // Trade count
        }

        OR

        [
          {
            "symbol": "BNBBTC",
            "priceChange": "-94.99999800",
            "priceChangePercent": "-95.960",
            "weightedAvgPrice": "0.29628482",
            "prevClosePrice": "0.10002000",
            "lastPrice": "4.00000200",
            "lastQty": "200.00000000",
            "bidPrice": "4.00000000",
            "askPrice": "4.00000200",
            "openPrice": "99.00000000",
            "highPrice": "100.00000000",
            "lowPrice": "0.10000000",
            "volume": "8913.30000000",
            "quoteVolume": "15.30000000",
            "openTime": 1499783499040,
            "closeTime": 1499869899040,
            "fristId": 28385,   // First tradeId
            "lastId": 28460,    // Last tradeId
            "count": 76         // Trade count
          }
        ]
        """

        async def _async_fetch_ticker_24h():
            try:
                query = "https://api.binance.com/api/v1/ticker/24hr"
                if symbol:
                    query += "?symbol={}".format(symbol)
                async with aiohttp.ClientSession() as session:
                    with async_timeout.timeout(self._request_timeout):
                        async with session.get(query) as response:
                            return await response.text()
            except Exception as exc:
                LOG.error("Error with _async_fetch_ticker_24h: {}".format(exc.args[-1]))
                return None

        try:
            if not self._host:
                raise ValueError("Did't got host param from config")
            LOG.debug("Try to get 24hr ticker price change statistics by symbol {}".format(symbol))
            return gloop.push_async_task(callback, _async_fetch_ticker_24h)
        except Exception as ex:
            LOG.error("Error fired with fetch_ticker_24h:{}".format(ex.args[-1]))

    def fetch_order_book_ticker(self, callback, symbol: str = None) -> asyncio.Task:
        """
        :input:
        Name 	Type 	Mandatory 	Description
        symbol 	STRING 	NO

        :return:
        {
          "symbol": "LTCBTC",
          "bidPrice": "4.00000000",
          "bidQty": "431.00000000",
          "askPrice": "4.00000200",
          "askQty": "9.00000000"
        }

        OR

        [
          {
            "symbol": "LTCBTC",
            "bidPrice": "4.00000000",
            "bidQty": "431.00000000",
            "askPrice": "4.00000200",
            "askQty": "9.00000000"
          },
          {
            "symbol": "ETHBTC",
            "bidPrice": "0.07946700",
            "bidQty": "9.00000000",
            "askPrice": "100000.00000000",
            "askQty": "1000.00000000"
          }
        ]
        """

        async def _async_fetch_order_book_ticker():
            try:
                query = "https://api.binance.com/api/v3/ticker/bookTicker"
                if symbol:
                    query += "?symbol={}".format(symbol)
                async with aiohttp.ClientSession() as session:
                    with async_timeout.timeout(self._request_timeout):
                        async with session.get(query) as response:
                            return await response.text()
            except Exception as exc:
                LOG.error("Error with _async_fetch_order_book_ticker: {}".format(exc.args[-1]))
                return None

        try:
            if not self._host:
                raise ValueError("Did't got host param from config")
            LOG.debug("Try to get order book ticker by symbol {}".format(symbol))
            return gloop.push_async_task(callback, _async_fetch_order_book_ticker)
        except Exception as ex:
            LOG.error("Error fired with fetch_order_book_ticker:{}".format(ex.args[-1]))

    def create_new_order(
            self,
            callback,
            symbol: str,
            side: str,
            order_type: str,
            quantity: float,
            timestamp: int,
            **kwargs
    ) -> asyncio.Task:
        """
        :input:
        Name 	            Type 	Mandatory 	Description
        ------------------------------------------------------------
        symbol 	            STRING 	YES
        side 	            ENUM 	YES
        type 	            ENUM 	YES
        quantity 	        DECIMAL YES
        timestamp 	        LONG 	YES
        timeInForce         ENUM 	NO
        price 	            DECIMAL NO
        newClientOrderId 	STRING 	NO 	        A unique id for the order. Automatically generated if not sent.
        stopPrice 	        DECIMAL NO 	        Used with STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, and TAKE_PROFIT_LIMIT orders.
        icebergQty 	        DECIMAL NO 	        Used with LIMIT, STOP_LOSS_LIMIT, and TAKE_PROFIT_LIMIT to create an iceberg order.
        newOrderRespType 	ENUM 	NO 	        Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        recvWindow 	        LONG 	NO


        Additional mandatory parameters based on type:
        Type 	            Additional mandatory parameters
        ------------------------------------------------------------
        LIMIT 	            timeInForce, quantity, price
        MARKET 	            quantity
        STOP_LOSS 	        quantity, stopPrice
        STOP_LOSS_LIMIT 	timeInForce, quantity, price, stopPrice
        TAKE_PROFIT 	    quantity, stopPrice
        TAKE_PROFIT_LIMIT 	timeInForce, quantity, price, stopPrice
        LIMIT_MAKER 	    quantity, price

        :return:
        {
          "symbol": "LTCBTC",
          "bidPrice": "4.00000000",
          "bidQty": "431.00000000",
          "askPrice": "4.00000200",
          "askQty": "9.00000000"
        }

        OR

        [
          {
            "symbol": "LTCBTC",
            "bidPrice": "4.00000000",
            "bidQty": "431.00000000",
            "askPrice": "4.00000200",
            "askQty": "9.00000000"
          },
          {
            "symbol": "ETHBTC",
            "bidPrice": "0.07946700",
            "bidQty": "9.00000000",
            "askPrice": "100000.00000000",
            "askQty": "1000.00000000"
          }
        ]
        """

        async def _async_create_new_order():
            try:
                entry_point = self._host + "/api/v3/order"
                query_string = "symbol={}&side={}&type={}&quantity={}&timestamp={}".format(
                    symbol,
                    side,
                    order_type,
                    str(quantity),
                    str(timestamp)
                )

                timeInForce = kwargs.get("timeInForce", None)
                newClientOrderId = kwargs.get("newClientOrderId", None)
                price = kwargs.get("price", None)
                stopPrice = kwargs.get("icebergQty", None)
                icebergQty = kwargs.get("icebergQty", None)
                newOrderRespType = kwargs.get("newOrderRespType", None)
                recvWindow = kwargs.get("recvWindow", None)

                if timeInForce:
                    query_string += "&timeInForce={}".format(timeInForce)
                if price:
                    query_string += "&price={}".format(price)
                if newClientOrderId:
                    query_string += "&newClientOrderId={}".format(newClientOrderId)
                if stopPrice:
                    query_string += "&stopPrice={}".format(stopPrice)
                if icebergQty:
                    query_string += "&icebergQty={}".format(icebergQty)
                if newOrderRespType:
                    query_string += "&newOrderRespType={}".format(newOrderRespType)
                if recvWindow:
                    query_string += "&recvWindow={}".format(recvWindow)

                signature = hmac.new(self._secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
                query_string += "&signature={}".format(signature)
                headers = {'X-MBX-APIKEY': '{}'.format(self._api_key)}
                async with aiohttp.ClientSession() as session:
                    with async_timeout.timeout(self._request_timeout):
                        url = entry_point + "?" + query_string
                        async with session.post(url, headers=headers) as response:
                            return await response.text()
            except Exception as exc:
                LOG.error("Error with _async_create_new_test_order: {}".format(exc.args[-1]))
                return None

        try:
            if not self._host:
                raise ValueError("Did't got host param from config")
            if not self._api_key:
                raise ValueError("Did't got api key from config")
            if not self._secret_key:
                raise ValueError("Did't got secret key from config")
            if not symbol:
                raise ValueError("Did't got symbol param")
            if not side:
                raise ValueError("Did't got side param")
            if not order_type:
                raise ValueError("Did't got type param")
            if not quantity:
                raise ValueError("Did't got quantity param")
            if not timestamp:
                raise ValueError("Did't got timestamp param")

            LOG.debug("Try to create_new_order by symbol {}".format(symbol))
            return gloop.push_async_task(callback, _async_create_new_order)
        except Exception as ex:
            LOG.error("Error fired with create_new_order:{}".format(ex.args[-1]))

    def create_new_test_order(
            self,
            callback,
            symbol: str,
            side: str,
            order_type: str,
            quantity: float,
            timestamp: int,  # need to multiply in x1000
            **kwargs
    ) -> asyncio.Task:
        """
        :input:
        Name 	            Type 	Mandatory 	Description
        ------------------------------------------------------------
        symbol 	            STRING 	YES
        side 	            ENUM 	YES
        type 	            ENUM 	YES
        quantity 	        DECIMAL YES
        timestamp 	        LONG 	YES
        timeInForce         ENUM 	NO
        price 	            DECIMAL NO
        newClientOrderId 	STRING 	NO 	        A unique id for the order. Automatically generated if not sent.
        stopPrice 	        DECIMAL NO 	        Used with STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, and TAKE_PROFIT_LIMIT orders.
        icebergQty 	        DECIMAL NO 	        Used with LIMIT, STOP_LOSS_LIMIT, and TAKE_PROFIT_LIMIT to create an iceberg order.
        newOrderRespType 	ENUM 	NO 	        Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        recvWindow 	        LONG 	NO


        Additional mandatory parameters based on type:
        Type 	            Additional mandatory parameters
        ------------------------------------------------------------
        LIMIT 	            timeInForce, quantity, price
        MARKET 	            quantity
        STOP_LOSS 	        quantity, stopPrice
        STOP_LOSS_LIMIT 	timeInForce, quantity, price, stopPrice
        TAKE_PROFIT 	    quantity, stopPrice
        TAKE_PROFIT_LIMIT 	timeInForce, quantity, price, stopPrice
        LIMIT_MAKER 	    quantity, price

        :return:
        {
          "symbol": "LTCBTC",
          "bidPrice": "4.00000000",
          "bidQty": "431.00000000",
          "askPrice": "4.00000200",
          "askQty": "9.00000000"
        }

        OR

        [
          {
            "symbol": "LTCBTC",
            "bidPrice": "4.00000000",
            "bidQty": "431.00000000",
            "askPrice": "4.00000200",
            "askQty": "9.00000000"
          },
          {
            "symbol": "ETHBTC",
            "bidPrice": "0.07946700",
            "bidQty": "9.00000000",
            "askPrice": "100000.00000000",
            "askQty": "1000.00000000"
          }
        ]
        """

        async def _async_create_new_test_order():
            try:
                entry_point = self._host + "/api/v3/order/test"
                query_string = "symbol={}&side={}&type={}&quantity={}&timestamp={}".format(
                    symbol,
                    side,
                    order_type,
                    str(quantity),
                    str(timestamp)
                )

                timeInForce = kwargs.get("timeInForce", None)
                newClientOrderId = kwargs.get("newClientOrderId", None)
                price = kwargs.get("price", None)
                stopPrice = kwargs.get("icebergQty", None)
                icebergQty = kwargs.get("icebergQty", None)
                newOrderRespType = kwargs.get("newOrderRespType", None)
                recvWindow = kwargs.get("recvWindow", None)

                if timeInForce:
                    query_string += "&timeInForce={}".format(timeInForce)
                if price:
                    query_string += "&price={}".format(price)
                if newClientOrderId:
                    query_string += "&newClientOrderId={}".format(newClientOrderId)
                if stopPrice:
                    query_string += "&stopPrice={}".format(stopPrice)
                if icebergQty:
                    query_string += "&icebergQty={}".format(icebergQty)
                if newOrderRespType:
                    query_string += "&newOrderRespType={}".format(newOrderRespType)
                if recvWindow:
                    query_string += "&recvWindow={}".format(recvWindow)

                signature = hmac.new(self._secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
                query_string += "&signature={}".format(signature)
                headers = {'X-MBX-APIKEY': '{}'.format(self._api_key)}
                async with aiohttp.ClientSession() as session:
                    with async_timeout.timeout(self._request_timeout):
                        url = entry_point + "?" + query_string
                        async with session.post(url, headers=headers) as response:
                            return await response.text()
            except Exception as exc:
                LOG.error("Error in {} with: {}".format(LOG.func_name(), exc.args[-1]))
                return None

        try:
            if not self._host:
                raise ValueError("Did't got host param from config")
            if not self._api_key:
                raise ValueError("Did't got api key from config")
            if not self._secret_key:
                raise ValueError("Did't got secret key from config")
            if not symbol:
                raise ValueError("Did't got symbol param")
            if not side:
                raise ValueError("Did't got side param")
            if not order_type:
                raise ValueError("Did't got type param")
            if not quantity:
                raise ValueError("Did't got quantity param")
            if not timestamp:
                raise ValueError("Did't got timestamp param")

            LOG.debug("Try to create_new_test_order by symbol {}".format(symbol))
            return gloop.push_async_task(callback, _async_create_new_test_order)
        except Exception as ex:
            LOG.error("Error fired with create_new_test_order:{}".format(ex.args[-1]))

    def query_open_orders(self, callback, timestamp: int, symbol: str = None, recvWindow: int = None) -> asyncio.Task:
        """
        :input timestamp: need to multiply in x1000

        :scheme:
        Name 	    Type 	Mandatory 	Description
        ------------------------------------------------------------
        timestamp 	LONG 	YES
        symbol 	    STRING 	NO
        recvWindow 	LONG 	NO


        :return:
        [
          {
            "symbol": "LTCBTC",
            "orderId": 1,
            "clientOrderId": "myOrder1",
            "price": "0.1",
            "origQty": "1.0",
            "executedQty": "0.0",
            "status": "NEW",
            "timeInForce": "GTC",
            "type": "LIMIT",
            "side": "BUY",
            "stopPrice": "0.0",
            "icebergQty": "0.0",
            "time": 1499827319559,
            "isWorking": trueO
          }
        ]
        """

        async def _async_f():
            try:
                entry_point = self._host + "/api/v3/openOrders"
                query_string = "timestamp={}".format(str(timestamp))

                if symbol:
                    query_string += "&symbol={}".format(symbol)
                if recvWindow:
                    query_string += "&recvWindow={}".format(str(recvWindow))

                signature = hmac.new(self._secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
                query_string += "&signature={}".format(signature)
                headers = {'X-MBX-APIKEY': '{}'.format(self._api_key)}
                async with aiohttp.ClientSession() as session:
                    with async_timeout.timeout(self._request_timeout):
                        url = entry_point + "?" + query_string
                        async with session.get(url, headers=headers) as response:
                            return await response.text()
            except Exception as exc:
                LOG.error("Error in {} with: {}".format(LOG.func_name(), exc.args[-1]))
                return None

        try:
            if not self._host:
                raise ValueError("Did't got host param from config")
            if not self._api_key:
                raise ValueError("Did't got api key from config")
            if not self._secret_key:
                raise ValueError("Did't got secret key from config")
            if not timestamp:
                raise ValueError("Did't got timestamp param")

            LOG.debug("Try to {} by symbol {}".format(LOG.func_name(), symbol))
            return gloop.push_async_task(callback, _async_f)
        except Exception as ex:
            LOG.error("Error fired in {} with:{}".format(LOG.func_name(), ex.args[-1]))

    def cancel_order(
            self,
            callback,
            symbol: str,
            timestamp: int,  # need to multiply in x1000
            orderId: int = None,
            origClientOrderId: str = None,
            newClientOrderId: str = None,
            recvWindow: int = None
    ) -> asyncio.Task:
        """
        :input:
        Name 	            Type 	Mandatory 	Description
        ------------------------------------------------------------
        symbol 	            STRING 	YES
        timestamp 	        LONG 	YES
        orderId 	        LONG 	NO
        origClientOrderId 	STRING 	NO
        newClientOrderId 	STRING 	NO 	        Used to uniquely identify this cancel. Automatically generated by default.
        recvWindow 	        LONG 	NO


        :return:
        {
          "symbol": "LTCBTC",
          "origClientOrderId": "myOrder1",
          "orderId": 1,
          "clientOrderId": "cancelMyOrder1"
        }
        """

        async def _async_f():
            try:
                entry_point = self._host + "/api/v3/order"
                query_string = "timestamp={}&symbol={}".format(str(timestamp), symbol)

                if orderId:
                    query_string += "&orderId={}".format(str(orderId))
                if origClientOrderId:
                    query_string += "&origClientOrderId={}".format(origClientOrderId)
                if newClientOrderId:
                    query_string += "&newClientOrderId={}".format(newClientOrderId)
                if recvWindow:
                    query_string += "&recvWindow={}".format(recvWindow)

                signature = hmac.new(self._secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
                query_string += "&signature={}".format(signature)
                headers = {'X-MBX-APIKEY': '{}'.format(self._api_key)}
                async with aiohttp.ClientSession() as session:
                    with async_timeout.timeout(self._request_timeout):
                        url = entry_point + "?" + query_string
                        async with session.delete(url, headers=headers) as response:
                            return await response.text()
            except Exception as exc:
                LOG.error("Error in {} with: {}".format(LOG.func_name(), exc.args[-1]))
                return None

        try:
            if not self._host:
                raise ValueError("Did't got host param from config")
            if not self._api_key:
                raise ValueError("Did't got api key from config")
            if not self._secret_key:
                raise ValueError("Did't got secret key from config")
            if not timestamp:
                raise ValueError("Did't got timestamp param")
            if not symbol:
                raise ValueError("Did't got symbol param")

            LOG.debug("Try to {} by symbol {}".format(LOG.func_name(), symbol))
            return gloop.push_async_task(callback, _async_f)
        except Exception as ex:
            LOG.error("Error fired in {} with:{}".format(LOG.func_name(), ex.args[-1]))

    def cancel_orders_list(
            self,
            callback,
            orders_list: List[dict],
            recvWindow: int = None
    ) -> asyncio.Task:
        async def _async_f():
            try:
                entry_point = self._host + "/api/v3/order"
                error: bool = False
                for order in orders_list:
                    query_string = "timestamp={}&symbol={}&orderId={}"\
                        .format(str(int(time.time() * 1000)), order["symbol"], order["orderId"])

                    if recvWindow:
                        query_string += "&recvWindow={}".format(str(recvWindow))
                    signature = hmac.new(self._secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
                    query_string += "&signature={}".format(signature)
                    headers = {'X-MBX-APIKEY': '{}'.format(self._api_key)}
                    async with aiohttp.ClientSession() as session:
                        with async_timeout.timeout(self._request_timeout):
                            url = entry_point + "?" + query_string
                            async with session.delete(url, headers=headers) as response:
                                result = await response.text()
                                parsed_json: dict = json.loads(result)
                                if not parsed_json or parsed_json.get("code") or parsed_json.get("msg"):
                                    error = True
                                    LOG.error("Error with trying to close order:{} with error:{}:{}"
                                              .format(order["orderId"], parsed_json.get("code"), parsed_json.get("msg")))
                return error
            except Exception as exc:
                LOG.error("Error in {} with: {}".format(LOG.func_name(), exc.args[-1]))
                return None

        try:
            if not self._host:
                raise ValueError("Did't got host param from config")
            if not self._api_key:
                raise ValueError("Did't got api key from config")
            if not self._secret_key:
                raise ValueError("Did't got secret key from config")

            LOG.debug("Try to {} by order list".format(LOG.func_name()))
            return gloop.push_async_task(callback, _async_f)
        except Exception as ex:
            LOG.error("Error fired in {} with msg:{}".format(LOG.func_name(), ex.args[-1]))

    def query_acc_info(self, callback, timestamp: int, recvWindow: int=None) -> asyncio.Task:
        """
        :input timestamp: need to multiply in x1000

        :scheme:
        Name 	    Type 	Mandatory 	Description
        ------------------------------------------------------------
        recvWindow 	LONG 	NO
        timestamp 	LONG 	YES


        :return:
        {
          "makerCommission": 15,
          "takerCommission": 15,
          "buyerCommission": 0,
          "sellerCommission": 0,
          "canTrade": true,
          "canWithdraw": true,
          "canDeposit": true,
          "updateTime": 123456789,
          "balances": [
            {
              "asset": "BTC",
              "free": "4723846.89208129",
              "locked": "0.00000000"
            },
            {
              "asset": "LTC",
              "free": "4763368.68006011",
              "locked": "0.00000000"
            }
          ]
        }
        """

        async def _async_f():
            try:
                entry_point = self._host + "/api/v3/account"
                query_string = "timestamp={}".format(str(timestamp))

                if recvWindow:
                    query_string += "&recvWindow={}".format(recvWindow)

                signature = hmac.new(self._secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
                query_string += "&signature={}".format(signature)
                headers = {'X-MBX-APIKEY': '{}'.format(self._api_key)}
                async with aiohttp.ClientSession() as session:
                    with async_timeout.timeout(self._request_timeout):
                        url = entry_point + "?" + query_string
                        async with session.get(url, headers=headers) as response:
                            return await response.text()
            except Exception as exc:
                LOG.error("Error in {} with: {}".format(LOG.func_name(), exc.args[-1]))
                return None

        try:
            if not self._host:
                raise ValueError("Did't got host param from config")
            if not self._api_key:
                raise ValueError("Did't got api key from config")
            if not self._secret_key:
                raise ValueError("Did't got secret key from config")
            if not timestamp:
                raise ValueError("Did't got timestamp param")

            LOG.debug("Try to {}".format(LOG.func_name()))
            return gloop.push_async_task(callback, _async_f)
        except Exception as ex:
            LOG.error("Error fired in {} with:{}".format(LOG.func_name(), ex.args[-1]))


"""
if __name__ == '__main__':
    from core import config
    config.init_global_config("/home/andrew/dev/crypto_bot/bot.cfg")

    def callback_ping(future: asyncio.Future):
        LOG.debug(str(future.result()))


    def callback_time(future: asyncio.Future):
        LOG.debug(str(future.result()))


    def callback_exchange_info(future: asyncio.Future):
        parsed_json = json.loads(str(future.result()))
        try:
            LOG.debug(json.dumps(parsed_json, sort_keys=True, indent=4))
        except KeyError:
            LOG.warning("Maybe your json is incorrect. Skip this event")


    def callback_order_book(future: asyncio.Future):
        parsed_json = json.loads(str(future.result()))
        try:
            LOG.debug(json.dumps(parsed_json, sort_keys=False, indent=2))
        except KeyError:
            LOG.warning("Maybe your json is incorrect. Skip this event")


    def callback_trades_list(future: asyncio.Future):
        parsed_json = json.loads(str(future.result()))
        try:
            LOG.debug(json.dumps(parsed_json, sort_keys=False, indent=2))
        except KeyError:
            LOG.warning("Maybe your json is incorrect. Skip this event")

    def callback_fetch_agg_trades(future: asyncio.Future):
        parsed_json = json.loads(str(future.result()))
        try:
            LOG.debug(json.dumps(parsed_json, sort_keys=False, indent=2))
        except KeyError:
            LOG.warning("Maybe your json is incorrect. Skip this event")

    def callback_fetch_ticker(future: asyncio.Future):
        parsed_json = json.loads(str(future.result()))
        only_btc_pairs = filter(lambda k: "BTC" in k["symbol"] and "USDT" not in k["symbol"], parsed_json)
        sorted_list = None
        if type(only_btc_pairs) == list:
            sorted_list = sorted(only_btc_pairs, key=lambda k: float(k["quoteVolume"]), reverse=True)
        try:
            LOG.debug(json.dumps(parsed_json, sort_keys=False, indent=2))
            if sorted_list:
                LOG.debug(json.dumps(sorted_list, sort_keys=False, indent=2))
        except KeyError:
            LOG.warning("Maybe your json is incorrect. Skip this event")

    def callback_fetch_order_book_ticker(future: asyncio.Future):
        parsed_json = json.loads(str(future.result()))
        try:
            LOG.debug(json.dumps(parsed_json, sort_keys=False, indent=2))
        except KeyError:
            LOG.warning("Maybe your json is incorrect. Skip this event")

    def callback_create_new_test_order(future: asyncio.Future):
        parsed_json = json.loads(str(future.result()))
        try:
            LOG.debug(json.dumps(parsed_json, sort_keys=False, indent=2))
        except KeyError:
            LOG.warning("Maybe your json is incorrect. Skip this event")

    def callback_1(future: asyncio.Future):
        parsed_json = json.loads(str(future.result()))
        try:
            LOG.debug(json.dumps(parsed_json, sort_keys=False, indent=2))
        except KeyError:
            LOG.warning("Maybe your json is incorrect. Skip this event")


    api = BinanceRestApi(config.global_core_conf)
    tasks = []
    #tasks.append(api.ping_server(callback_ping))
    #tasks.append(api.fetch_server_time(callback_time))
    # tasks.append(api.fetch_order_book(callback_order_book, "LSKBTC", 5))
    #tasks.append(api.fetch_trades_list(callback_trades_list, "LSKBTC"))
    #tasks.append(api.fetch_ticker_24h(callback_fetch_ticker, "LSKBTC"))
    #tasks.append(api.fetch_order_book_ticker(callback_fetch_order_book_ticker, "LSKBTC"))
    tasks.append(api.create_new_test_order(
        callback_create_new_test_order,
        "LSKBTC",
        BinanceApiEnums.ORDER_SIDE_SELL,
        BinanceApiEnums.ORDER_TYPE_LIMIT,
        quantity=1.47,
        timestamp=int(time.time() * 1000),
        timeInForce=BinanceApiEnums.TIME_IN_FORCE_GTC,
        price=0.0022
    ))
    #tasks.append(api.query_open_orders(callback_1, int(time.time() * 1000)))
    #tasks.append(api.cancel_order(callback_1, symbol="LSKBTC", timestamp=int(time.time() * 1000), orderId=4457796))
    #tasks.append(api.fetch_agg_trades(callback_fetch_agg_trades, "LSKBTC"))
    #tasks.append(api.exchange_info(callback_exchange_info))
    tasks.append(api.query_acc_info(callback_1, timestamp=int(time.time() * 1000)))

    wait_tasks = asyncio.wait(tasks)
    gloop.global_ev_loop.run_until_complete(wait_tasks)"""
