import requests
import hmac
import hashlib
from logger import logger

LOG = logger.LOG


class BnApiEnums(object):
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

    def ping_server(self):
        """
        :return: {}
        """
        try:
            if not self._host:
                raise ValueError("Did't got host param from config")
            endpoint = "/api/v1/ping"
            url = self._host + endpoint
            LOG.debug("Try to get ping from server. url:{}".format(url))
            responce = requests.get(url=url, timeout=self._request_timeout)
            return responce.json()
        except Exception as ex:
            LOG.error("Error fired with ping server:{}".format(ex.args[-1]))

    def fetch_server_time(self):
        """
        :return:
        {
          "serverTime": 1499827319559
        }
        """
        try:
            if not self._host:
                raise ValueError("Did't got host param from config")
            endpoint = "/api/v1/time"
            url = self._host + endpoint
            LOG.debug("Try to get binance server time. url:{}".format(url))
            responce = requests.get(url=url, timeout=self._request_timeout)
            return responce.json()
        except Exception as ex:
            LOG.error("Error fired with fetch_server_time:{}".format(ex.args[-1]))

    def exchange_info(self):
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
        try:
            if not self._host:
                raise ValueError("Did't got host param from config")
            endpoint = "/api/v1/exchangeInfo"
            url = self._host + endpoint
            LOG.debug("Try to get exchange_info from server. url:{}".format(url))
            responce = requests.get(url=url, timeout=self._request_timeout)
            return responce.json()
        except Exception as ex:
            LOG.error("Error fired with exchange_info:{}".format(ex.args[-1]))

    def fetch_order_book(self, symbol: str, limit: int = None):
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
        try:
            if not symbol:
                raise ValueError("Did't got mandatory param symbol: {}".format(symbol))
            if not self._host:
                raise ValueError("Did't got host param from config")
            query_params = "symbol={}".format(symbol)
            if limit:
                query_params += "&limit={}".format(str(limit))
            endpoint = "/api/v1/depth"
            url = self._host + endpoint + "?" + query_params
            LOG.debug("Try to get order book by symbol. url:{}".format(url))
            responce = requests.get(url=url, timeout=self._request_timeout)
            return responce.json()
        except Exception as ex:
            LOG.error("Error fired with fetch_order_book:{}".format(ex.args[-1]))

    def fetch_trades_list(self, symbol: str, limit: int = None):
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
        try:
            if not symbol:
                raise ValueError("Did't got mandatory param symbol: {}".format(symbol))
            if not self._host:
                raise ValueError("Did't got host param from config")
            query_params = "symbol={}".format(symbol)
            if limit:
                query_params += "&limit={}".format(str(limit))
            endpoint = "/api/v1/trades"
            url = self._host + endpoint + "?" + query_params
            LOG.debug("Try to get order book by symbol. url:{}".format(url))
            responce = requests.get(url=url, timeout=self._request_timeout)
            return responce.json()
        except Exception as ex:
            LOG.error("Error fired with fetch_trades_list:{}".format(ex.args[-1]))

    def fetch_agg_trades(
            self,
            symbol: str,
            from_id: int = None,
            start_time: int = None,
            end_time: int = None,
            limit: int = None
    ):
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
        try:
            if not symbol:
                raise ValueError("Did't got mandatory param symbol: {}".format(symbol))
            if not self._host:
                raise ValueError("Did't got host param from config")
            query_params = "symbol={0}".format(symbol)
            if from_id:
                query_params += "&fromId={}".format(from_id)
            if start_time:
                query_params += "&startTime={}".format(start_time)
            if end_time:
                query_params += "&endTime={}".format(end_time)
            if limit:
                query_params += "&limit={}".format(str(limit))
            endpoint = "/api/v1/aggTrades"
            url = self._host + endpoint + "?" + query_params
            LOG.debug("Try to get aggregate trades list by symbol. url:{}".format(url))
            responce = requests.get(url=url, timeout=self._request_timeout)
            return responce.json()
        except Exception as ex:
            LOG.error("Error fired with fetch_agg_trades:{}".format(ex.args[-1]))

    def fetch_ticker_24h(self, symbol: str = None):
        """
        :param symbol: symbol

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
        try:
            if not self._host:
                raise ValueError("Did't got host param from config")
            query_params = ""
            if symbol:
                query_params += "?symbol={}".format(symbol)
            endpoint = "/api/v1/ticker/24hr"
            url = self._host + endpoint + "?" + query_params
            LOG.debug("Try to get 24hr ticker price change stat. url:{}".format(url))
            return requests.get(url=url, timeout=self._request_timeout).json()
        except Exception as ex:
            LOG.error("Error fired with fetch_ticker_24h:{}".format(ex.args[-1]))

    def fetch_order_book_ticker(self, symbol: str = None):
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
        try:
            if not self._host:
                raise ValueError("Did't got host param from config")
            query_params = ""
            if symbol:
                query_params += "?symbol={}".format(symbol)
            endpoint = "/api/v3/ticker/bookTicker"
            url = self._host + endpoint + "?" + query_params
            LOG.debug("Try to get order book ticker. url:{}".format(url))
            return requests.get(url=url, timeout=self._request_timeout).json()
        except Exception as ex:
            LOG.error("Error fired with fetch_order_book_ticker:{}".format(ex.args[-1]))

    def create_new_order(
            self,
            symbol: str,
            side: str,
            order_type: str,
            quantity: float,
            timestamp: int,
            **kwargs
    ):
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
          "symbol": "BTCUSDT",
          "orderId": 28,
          "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
          "transactTime": 1507725176595,
          "price": "0.00000000",
          "origQty": "10.00000000",
          "executedQty": "10.00000000",
          "status": "FILLED",
          "timeInForce": "GTC",
          "type": "MARKET",
          "side": "SELL"
        }
        """
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

            query_params = "symbol={}&side={}&type={}&quantity={}&timestamp={}".format(
                symbol,
                side,
                order_type,
                f"{quantity:.8f}",
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
                query_params += "&timeInForce={}".format(timeInForce)
            if price:
                query_params += "&price={:.8f}".format(price)
            if newClientOrderId:
                query_params += "&newClientOrderId={}".format(newClientOrderId)
            if stopPrice:
                query_params += "&stopPrice={:.8f}".format(stopPrice)
            if icebergQty:
                query_params += "&icebergQty={:.8f}".format(icebergQty)
            if newOrderRespType:
                query_params += "&newOrderRespType={}".format(newOrderRespType)
            if recvWindow:
                query_params += "&recvWindow={}".format(recvWindow)

            signature = hmac.new(self._secret_key.encode(), query_params.encode(), hashlib.sha256).hexdigest()
            query_params += "&signature={}".format(signature)
            headers = {'X-MBX-APIKEY': '{}'.format(self._api_key)}
            endpoint = "/api/v3/order"
            url = self._host + endpoint + "?" + query_params
            LOG.debug("Try to create_new_order. url:{}".format(url))
            return requests.post(url=url, headers=headers, timeout=self._request_timeout).json()
        except Exception as ex:
            LOG.error("Error fired with create_new_order:{}".format(ex.args[-1]))

    def create_new_test_order(
            self,
            symbol: str,
            side: str,
            order_type: str,
            quantity: float,
            timestamp: int,  # need to multiply in x1000
            **kwargs
    ):
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

            query_params = "symbol={}&side={}&type={}&quantity={}&timestamp={}".format(
                symbol,
                side,
                order_type,
                f"{quantity:.8f}",
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
                query_params += "&timeInForce={}".format(timeInForce)
            if price:
                query_params += "&price={:.8f}".format(price)
            if newClientOrderId:
                query_params += "&newClientOrderId={}".format(newClientOrderId)
            if stopPrice:
                query_params += "&stopPrice={:.8f}".format(stopPrice)
            if icebergQty:
                query_params += "&icebergQty={:.8f}".format(icebergQty)
            if newOrderRespType:
                query_params += "&newOrderRespType={}".format(newOrderRespType)
            if recvWindow:
                query_params += "&recvWindow={}".format(recvWindow)

            signature = hmac.new(self._secret_key.encode(), query_params.encode(), hashlib.sha256).hexdigest()
            query_params += "&signature={}".format(signature)
            headers = {'X-MBX-APIKEY': '{}'.format(self._api_key)}
            endpoint = "/api/v3/order/test"
            url = self._host + endpoint + "?" + query_params
            LOG.debug("Try to {}. url:{}".format(LOG.func_name(), url))
            return requests.post(url=url, headers=headers, timeout=self._request_timeout).json()
        except Exception as ex:
            LOG.error("Error fired with create_new_order:{}".format(ex.args[-1]))

    def query_open_orders(self, timestamp: int, symbol: str = None, recvWindow: int = None):
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
        try:
            if not self._host:
                raise ValueError("Did't got host param from config")
            if not self._api_key:
                raise ValueError("Did't got api key from config")
            if not self._secret_key:
                raise ValueError("Did't got secret key from config")
            if not timestamp:
                raise ValueError("Did't got timestamp param")

            query_params = "timestamp={}".format(str(timestamp))
            if symbol:
                query_params += "&symbol={}".format(symbol)
            if recvWindow:
                query_params += "&recvWindow={}".format(str(recvWindow))

            signature = hmac.new(self._secret_key.encode(), query_params.encode(), hashlib.sha256).hexdigest()
            query_params += "&signature={}".format(signature)
            headers = {'X-MBX-APIKEY': '{}'.format(self._api_key)}
            endpoint = "/api/v3/openOrders"
            url = self._host + endpoint + "?" + query_params
            LOG.debug("Try to {}. url:{}".format(LOG.func_name(), url))
            return requests.get(url=url, headers=headers, timeout=self._request_timeout).json()
        except Exception as ex:
            LOG.error("Error fired in {} with:{}".format(LOG.func_name(), ex.args[-1]))

    def cancel_order(
            self,
            symbol: str,
            timestamp: int,  # need to multiply in x1000
            orderId: int=None,
            origClientOrderId: str=None,
            newClientOrderId: str=None,
            recvWindow: int=None
    ):
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

            query_params = "timestamp={}&symbol={}".format(str(timestamp), symbol)
            if orderId:
                query_params += "&orderId={}".format(str(orderId))
            if origClientOrderId:
                query_params += "&origClientOrderId={}".format(origClientOrderId)
            if newClientOrderId:
                query_params += "&newClientOrderId={}".format(newClientOrderId)
            if recvWindow:
                query_params += "&recvWindow={}".format(recvWindow)

            signature = hmac.new(self._secret_key.encode(), query_params.encode(), hashlib.sha256).hexdigest()
            query_params += "&signature={}".format(signature)
            headers = {'X-MBX-APIKEY': '{}'.format(self._api_key)}
            endpoint = "/api/v3/order"
            url = self._host + endpoint + "?" + query_params
            LOG.debug("Try to {}. url:{}".format(LOG.func_name(), url))
            return requests.delete(url=url, headers=headers, timeout=self._request_timeout).json()
        except Exception as ex:
            LOG.error("Error fired in {} with:{}".format(LOG.func_name(), ex.args[-1]))

    def query_acc_info(self, timestamp: int, recvWindow: int=None):
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
        try:
            if not self._host:
                raise ValueError("Did't got host param from config")
            if not self._api_key:
                raise ValueError("Did't got api key from config")
            if not self._secret_key:
                raise ValueError("Did't got secret key from config")
            if not timestamp:
                raise ValueError("Did't got timestamp param")

            query_params = "timestamp={}".format(str(timestamp))
            if recvWindow:
                query_params += "&recvWindow={}".format(recvWindow)

            signature = hmac.new(self._secret_key.encode(), query_params.encode(), hashlib.sha256).hexdigest()
            query_params += "&signature={}".format(signature)
            headers = {'X-MBX-APIKEY': '{}'.format(self._api_key)}
            endpoint = "/api/v3/account"
            url = self._host + endpoint + "?" + query_params
            LOG.debug("Try to {}. url:{}".format(LOG.func_name(), url))
            return requests.get(url=url, headers=headers, timeout=self._request_timeout).json()
        except Exception as ex:
            LOG.error("Error fired in {} with:{}".format(LOG.func_name(), ex.args[-1]))

    def my_trades(self, symbol: str, timestamp: int, limit: int=None, fromId: int=None, recvWindow: int=None):
        """
        :input timestamp: need to multiply in x1000

        :scheme:
        Name 	    Type 	Mandatory 	Description
        ------------------------------------------------------------
        symbol 	    STRING 	YES
        timestamp 	LONG 	YES
        limit 	    INT 	NO 	        Default 500; max 500.
        fromId 	    LONG 	NO 	        TradeId to fetch from. Default gets most recent trades.
        recvWindow 	LONG 	NO


        :return:
        [
          {
            "id": 28457,
            "orderId": 100234,
            "price": "4.00000100",
            "qty": "12.00000000",
            "commission": "10.10000000",
            "commissionAsset": "BNB",
            "time": 1499865549590,
            "isBuyer": true,
            "isMaker": false,
            "isBestMatch": true
          }
        ]
        """
        try:
            if not self._host:
                raise ValueError("Did't got host param from config")
            if not self._api_key:
                raise ValueError("Did't got api key from config")
            if not self._secret_key:
                raise ValueError("Did't got secret key from config")
            if not symbol:
                raise ValueError("Did't got symbol param")
            if not timestamp:
                raise ValueError("Did't got timestamp param")

            query_params = "symbol={}&timestamp={}".format(symbol, str(timestamp))
            if recvWindow:
                query_params += "&recvWindow={}".format(str(recvWindow))
            if limit:
                query_params += "&limit={}".format(str(limit))
            if fromId:
                query_params += "&fromId={}".format(str(fromId))

            signature = hmac.new(self._secret_key.encode(), query_params.encode(), hashlib.sha256).hexdigest()
            query_params += "&signature={}".format(signature)
            headers = {'X-MBX-APIKEY': '{}'.format(self._api_key)}
            endpoint = "/api/v3/myTrades"
            url = self._host + endpoint + "?" + query_params
            LOG.debug("Try to {}. url:{}".format(LOG.func_name(), url))
            return requests.get(url=url, headers=headers, timeout=self._request_timeout).json()
        except Exception as ex:
            LOG.error("Error fired in {} with:{}".format(LOG.func_name(), ex.args[-1]))


if __name__ == '__main__':
    import json
    from core import config as conf
    from utils import utc_timestamp as tm

    conf.init_global_config("/home/andrew/dev/crypto_bot/bot.cfg")
    api = BinanceRestApi(conf.global_core_conf)
    LOG.debug(json.dumps(api.exchange_info(), sort_keys=False, indent=2))
    tr = api.my_trades(symbol="MCOBTC", timestamp=tm.utc_timestamp(), limit=1)
"""
    LOG.debug(json.dumps(api.ping_server()))
    LOG.debug(json.dumps(api.fetch_server_time()))
    LOG.debug(json.dumps(api.query_acc_info(timestamp=int(time.time()*1000)), sort_keys=False, indent=2))
    result = api.query_open_orders(timestamp=int(time.time() * 1000))
    LOG.debug(json.dumps(result, sort_keys=False, indent=2))
    for order in result:
        LOG.debug(
            json.dumps(
                api.cancel_order(
                    symbol=order["symbol"],
                    timestamp=int(time.time() * 1000),
                    orderId=order["orderId"]),
                sort_keys=False,
                indent=2
            )
        )
    LOG.debug(json.dumps(
        api.create_new_order(
            "NEOBTC",
            BinanceApiEnums.ORDER_SIDE_BUY,
            BinanceApiEnums.ORDER_TYPE_LIMIT,
            quantity=0.32,
            timestamp=int(time.time() * 1000),
            price=0.01,
            timeInForce=BinanceApiEnums.TIME_IN_FORCE_GTC
        ),
        sort_keys=False, indent=2
    ))
"""
