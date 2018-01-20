from typing import List
from logger import logger
import json
from utils import utc_timestamp as tm
from utils import algorithm as alg
import exchange_base
import binance_rest_api as api

LOG = logger.LOG


class ApiWrapperBase(object):
    def exchange_symbols_info(self) -> List[dict]:
        pass

    def create_new_order(
            self,
            symbol: str,
            side: str,
            order_type: str,
            quantity: float,
            price: float=None,
            time_in_force: str=None
    ) -> bool:
        pass

    def cancel_order(self, order: dict) -> bool:
        pass

    def open_orders_by_side(self, order_side: str) -> List[dict]:
        pass

    def sorted_trade_pairs_btc(self) -> List[dict]:
        pass

    def acc_balance_for_assets(self) -> List[dict]:
        pass

    def my_trades_by_symbol(self, symbol: str) -> List[dict]:
        pass


class ApiWrapperMain(ApiWrapperBase):
    def __init__(self, config):
        self._api = api.BinanceRestApi(config)
        self._config = config

    def exchange_symbols_info(self) -> List[dict]:
        res = self._api.exchange_info()["symbols"]
        LOG.debug(res, content_type="json")
        return res

    def create_new_order(
            self,
            symbol: str,
            side: str,
            order_type: str,
            quantity: float,
            price: float=None,
            time_in_force: str=None
    ) -> bool:
        res = self._api.create_new_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            timestamp=tm.utc_timestamp(),
            price=price,
            timeInForce=time_in_force
        )
        LOG.debug(res, content_type="json")
        return "code" not in res and "msg" not in res

    def cancel_order(self, order: dict) -> bool:
        res = self._api.cancel_order(
            symbol=order["symbol"],
            timestamp=tm.utc_timestamp(),
            orderId=order["orderId"],
            recvWindow=5000
        )
        LOG.debug(res, content_type="json")
        return "code" not in res and "msg" not in res

    def open_orders_by_side(self, order_side: str) -> List[dict]:
        open_orders_lst: List[dict] = self._api.query_open_orders(timestamp=tm.utc_timestamp(), recvWindow=5000)
        res = list(filter(lambda order: order["side"] == order_side, open_orders_lst))
        LOG.debug(res, content_type="json")
        return res

    def sorted_trade_pairs_btc(self) -> List[dict]:
        def sort_func(key):
            ask = float(key["askPrice"])
            bid = float(key["bidPrice"])
            volume24h = float(key["quoteVolume"])
            rank = ((ask - bid) / bid) * volume24h
            LOG.debug("symbol:{} rank:{}".format(key["symbol"], str(rank)))
            return rank

        pairs_lst: List[dict] = self._api.fetch_ticker_24h()
        only_btc_pairs_lst: list = \
            filter(
                lambda pair:
                "BTC" in pair["symbol"]
                and "USDT" not in pair["symbol"]
                and float(pair["lastPrice"]) > self._config.getfloat("Exchange", "min_pair_price", fallback=0.000001),
                pairs_lst
            )
        res = sorted(only_btc_pairs_lst, key=sort_func, reverse=True)
        LOG.debug(res, content_type="json")
        return res

    def acc_balance_for_assets(self) -> List[dict]:
        res = self._api.query_acc_info(timestamp=tm.utc_timestamp(), recvWindow=5000)
        balances_lst: List[dict] = res['balances']
        res = list(filter(
            lambda asset: float(asset["free"]) + float(asset["locked"]), balances_lst))
        LOG.debug(res, content_type="json")
        return res

    def my_trades_by_symbol(self, symbol: str) -> List[dict]:
        res = self._api.my_trades(symbol=symbol, timestamp=tm.utc_timestamp(), recvWindow=5000)
        LOG.debug(res, content_type="json")
        return res


# noinspection PyUnusedLocal
class ApiWrapperTest(ApiWrapperBase):
    def __init__(self, config):
        self._api = api.BinanceRestApi(config)
        self._config = config

    def exchange_symbols_info(self) -> List[dict]:
        symbols = """[
        {
              "symbol": "ETHBTC",
              "status": "TRADING",
              "baseAsset": "ETH",
              "baseAssetPrecision": 8,
              "quoteAsset": "BTC",
              "quotePrecision": 8,
              "orderTypes": [
                "LIMIT",
                "LIMIT_MAKER",
                "MARKET",
                "STOP_LOSS_LIMIT",
                "TAKE_PROFIT_LIMIT"
              ],
              "icebergAllowed": true,
              "filters": [
                {
                  "filterType": "PRICE_FILTER",
                  "minPrice": "0.00000100",
                  "maxPrice": "100000.00000000",
                  "tickSize": "0.00000100"
                },
                {
                  "filterType": "LOT_SIZE",
                  "minQty": "0.00100000",
                  "maxQty": "100000.00000000",
                  "stepSize": "0.00100000"
                },
                {
                  "filterType": "MIN_NOTIONAL",
                  "minNotional": "0.00100000"
                }
              ]
            },
            {
              "symbol": "LTCBTC",
              "status": "TRADING",
              "baseAsset": "LTC",
              "baseAssetPrecision": 8,
              "quoteAsset": "BTC",
              "quotePrecision": 8,
              "orderTypes": [
                "LIMIT",
                "LIMIT_MAKER",
                "MARKET",
                "STOP_LOSS_LIMIT",
                "TAKE_PROFIT_LIMIT"
              ],
              "icebergAllowed": true,
              "filters": [
                {
                  "filterType": "PRICE_FILTER",
                  "minPrice": "0.00000100",
                  "maxPrice": "100000.00000000",
                  "tickSize": "0.00000100"
                },
                {
                  "filterType": "LOT_SIZE",
                  "minQty": "0.01000000",
                  "maxQty": "100000.00000000",
                  "stepSize": "0.01000000"
                },
                {
                  "filterType": "MIN_NOTIONAL",
                  "minNotional": "0.00200000"
                }
              ]
            },
            {
              "symbol": "NEOBTC",
              "status": "TRADING",
              "baseAsset": "NEO",
              "baseAssetPrecision": 8,
              "quoteAsset": "BTC",
              "quotePrecision": 8,
              "orderTypes": [
                "LIMIT",
                "LIMIT_MAKER",
                "MARKET",
                "STOP_LOSS_LIMIT",
                "TAKE_PROFIT_LIMIT"
              ],
              "icebergAllowed": true,
              "filters": [
                {
                  "filterType": "PRICE_FILTER",
                  "minPrice": "0.00000100",
                  "maxPrice": "100000.00000000",
                  "tickSize": "0.00000100"
                },
                {
                  "filterType": "LOT_SIZE",
                  "minQty": "0.01000000",
                  "maxQty": "100000.00000000",
                  "stepSize": "0.01000000"
                },
                {
                  "filterType": "MIN_NOTIONAL",
                  "minNotional": "0.00200000"
                }
              ]
            },
            {
              "symbol": "BNBBTC",
              "status": "TRADING",
              "baseAsset": "BNB",
              "baseAssetPrecision": 8,
              "quoteAsset": "BTC",
              "quotePrecision": 8,
              "orderTypes": [
                "LIMIT",
                "LIMIT_MAKER",
                "MARKET",
                "STOP_LOSS_LIMIT",
                "TAKE_PROFIT_LIMIT"
              ],
              "icebergAllowed": true,
              "filters": [
                {
                  "filterType": "PRICE_FILTER",
                  "minPrice": "0.00000010",
                  "maxPrice": "100000.00000000",
                  "tickSize": "0.00000010"
                },
                {
                  "filterType": "LOT_SIZE",
                  "minQty": "0.01000000",
                  "maxQty": "90000000.00000000",
                  "stepSize": "0.01000000"
                },
                {
                  "filterType": "MIN_NOTIONAL",
                  "minNotional": "0.00200000"
                }
              ]
            }
        ]
        """
        res = json.loads(symbols)
        LOG.debug(res, content_type="json")
        return res

    def create_new_order(
            self,
            symbol: str,
            side: str,
            order_type: str,
            quantity: float,
            price: float=None,
            time_in_force: str=None
    ) -> bool:
        res = """{
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
                }"""
        res1 = """{
              "code":-1121,
              "msg":"Invalid symbol."
            }"""
        res = json.loads(res1)
        LOG.debug(res, content_type="json")
        return "code" not in res and "msg" not in res

    def cancel_order(self, order: dict) -> bool:
        res = """{
          "symbol": "LTCBTC",
          "origClientOrderId": "myOrder1",
          "orderId": 1,
          "clientOrderId": "cancelMyOrder1"
        }"""
        res = json.loads(res)
        LOG.debug(res, content_type="json")
        return "code" not in res and "msg" not in res

    def open_orders_by_side(self, order_side: str) -> List[dict]:
        res = """
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
            "isWorking": true
          },
                    {
            "symbol": "NEOBTC",
            "orderId": 2,
            "clientOrderId": "myOrder2",
            "price": "0.5",
            "origQty": "3.0",
            "executedQty": "2.0",
            "status": "NEW",
            "timeInForce": "GTC",
            "type": "LIMIT",
            "side": "BUY",
            "stopPrice": "0.0",
            "icebergQty": "0.0",
            "time": 1499827319559,
            "isWorking": true
          }
        ]
        """
        open_orders_lst: List[dict] = json.loads(res)
        res = list(filter(lambda order: order["side"] == order_side, open_orders_lst))
        LOG.debug(res, content_type="json")
        return res

    def sorted_trade_pairs_btc(self) -> List[dict]:
        res = """
        [{
            "symbol": "ETHBTC",
            "priceChange": "-0.00136600",
            "priceChangePercent": "-1.509",
            "weightedAvgPrice": "0.09063035",
            "prevClosePrice": "0.09053200",
            "lastPrice": "0.08917400",
            "lastQty": "2.84200000",
            "bidPrice": "0.08901700",
            "bidQty": "2.84300000",
            "askPrice": "0.08917500",
            "askQty": "0.11200000",
            "openPrice": "0.09054000",
            "highPrice": "0.09300000",
            "lowPrice": "0.08790000",
            "volume": "225326.98700000",
            "quoteVolume": "20421.46389541",
            "openTime": 1516348099976,
            "closeTime": 1516434499976,
            "firstId": 23588603,
            "lastId": 24005148,
            "count": 416546
          },
          {
            "symbol": "LTCBTC",
            "priceChange": "-0.00057400",
            "priceChangePercent": "-3.400",
            "weightedAvgPrice": "0.01668581",
            "prevClosePrice": "0.01679900",
            "lastPrice": "0.01630600",
            "lastQty": "0.52000000",
            "bidPrice": "0.01628500",
            "bidQty": "5.16000000",
            "askPrice": "0.01631000",
            "askQty": "8.94000000",
            "openPrice": "0.01688000",
            "highPrice": "0.01696400",
            "lowPrice": "0.01620100",
            "volume": "121125.22000000",
            "quoteVolume": "2021.07237290",
            "openTime": 1516348099784,
            "closeTime": 1516434499784,
            "firstId": 5477004,
            "lastId": 5526041,
            "count": 49038
          },
          {
            "symbol": "BNBBTC",
            "priceChange": "-0.00001670",
            "priceChangePercent": "-1.290",
            "weightedAvgPrice": "0.00129709",
            "prevClosePrice": "0.00129470",
            "lastPrice": "0.00127790",
            "lastQty": "294.18000000",
            "bidPrice": "0.00127660",
            "bidQty": "18.06000000",
            "askPrice": "0.00127780",
            "askQty": "69.00000000",
            "openPrice": "0.00129460",
            "highPrice": "0.00132650",
            "lowPrice": "0.00125000",
            "volume": "2491698.64000000",
            "quoteVolume": "3231.96716569",
            "openTime": 1516348099960,
            "closeTime": 1516434499960,
            "firstId": 7038445,
            "lastId": 7134298,
            "count": 95854
          },
          {
            "symbol": "NEOBTC",
            "priceChange": "-0.00107500",
            "priceChangePercent": "-8.515",
            "weightedAvgPrice": "0.01211788",
            "prevClosePrice": "0.01262400",
            "lastPrice": "0.01155000",
            "lastQty": "0.17000000",
            "bidPrice": "0.01152400",
            "bidQty": "108.06000000",
            "askPrice": "0.01155000",
            "askQty": "1.27000000",
            "openPrice": "0.01262500",
            "highPrice": "0.01289000",
            "lowPrice": "0.01122700",
            "volume": "400967.49000000",
            "quoteVolume": "4858.87546368",
            "openTime": 1516348099948,
            "closeTime": 1516434499948,
            "firstId": 6566166,
            "lastId": 6648636,
            "count": 82471
          }]
        """

        def sort_func(key):
            ask = float(key["askPrice"])
            bid = float(key["bidPrice"])
            volume24h = float(key["quoteVolume"])
            rank = ((ask - bid) / bid) * volume24h
            LOG.debug("symbol:{} rank:{}".format(key["symbol"], str(rank)))
            return rank

        pairs_lst: List[dict] = json.loads(res)
        only_btc_pairs_lst: list = \
            filter(
                lambda pair:
                "BTC" in pair["symbol"]
                and "USDT" not in pair["symbol"]
                and float(pair["lastPrice"]) > self._config.getfloat("Exchange", "min_pair_price", fallback=0.000001),
                pairs_lst
            )
        res = sorted(only_btc_pairs_lst, key=sort_func, reverse=True)
        LOG.debug(res, content_type="json")
        return res

    def acc_balance_for_assets(self) -> List[dict]:
        res = """
        [
            {
                "asset": "BTC",
                "free":"0.00003077",
                "locked":"0.00320000"
            },
            {
                "asset": "LTC",
                "free": "12.68006011",
                "locked": "0.00000000"
            }
        ]
        """
        balances_lst: List[dict] = json.loads(res)
        res = list(filter(
            lambda asset: float(asset["free"]) + float(asset["locked"]), balances_lst))
        LOG.debug(res, content_type="json")
        return res

    def my_trades_by_symbol(self, symbol: str) -> List[dict]:
        res = """
        [
            {
            "id": 925417,
            "orderId": 4624304,
            "price": "0.00220000",
            "qty": "1.47000000",
            "commission": "0.00000323",
            "commissionAsset": "BTC",
            "time": 1516227560285,
            "isBuyer": false,
            "isMaker": true,
            "isBestMatch": true
            }
        ]
        """
        res = json.loads(res)
        LOG.debug(res, content_type="json")
        return res


class BinanceWorker(exchange_base.IExchangeBase):
    def __init__(self, config, api_wrapper: ApiWrapperBase=None):
        self._config = config
        if not api_wrapper:
            self._api_wr = ApiWrapperMain(config=config)
        else:
            self._api_wr = api_wrapper

    def run_worker(self):
        super().run_worker()
        self._work()

    def release(self):
        super().release()

    def _work(self):
        try:
            my_open_orders_buy: list = self._api_wr.open_orders_by_side(order_side=api.BnApiEnums.ORDER_SIDE_BUY)
            # Close all open orders with side = 'BUY'
            my_open_orders_buy[:] = [order for order in my_open_orders_buy if not self._api_wr.cancel_order(order)]
            if my_open_orders_buy:
                raise ValueError("Did't close all open orders for 'BUY' side")

            all_trade_pairs_btc: List[dict] = self._api_wr.sorted_trade_pairs_btc()
            potential_buy_list: List[dict] = all_trade_pairs_btc[:]
            my_acc_balance_assets: List[dict] = self._api_wr.acc_balance_for_assets()
            exchange_symbols_info: List[dict] = self._api_wr.exchange_symbols_info()

            if not all_trade_pairs_btc \
                    or not potential_buy_list \
                    or not my_acc_balance_assets \
                    or not exchange_symbols_info:
                raise ValueError("Something went wrong and one from mandatory params are None")

            self._generete_sell_orders_slow(all_trade_pairs_btc, my_acc_balance_assets, potential_buy_list, exchange_symbols_info)
            self._generate_buy_orders_slow(potential_buy_list, exchange_symbols_info)

        except Exception as ex:
            LOG.error("Unknown exception has fired. Type:{} msg:{}".format(type(ex), ex.args[-1]))
        finally:
            LOG.info("BinanceWorker is shutting down!")
            self.release()

    def _generete_sell_orders_slow(self, all_trade_pairs_btc, my_acc_balance_assets, potential_buy_list, exchange_symbols_info):
        # Loop for all of my assets except 'BTC' and create 'SELL' orders
        for asset in my_acc_balance_assets:
            if asset["asset"] == "BTC":
                continue
            symbol: str = asset["asset"] + "BTC"
            total_asset_balance = float(asset["free"]) + float(asset["locked"])
            # Find trade pair with 'BTC' on exchange in current moment for our asset
            trade_pair_for_asset = next(
                (pr for pr in all_trade_pairs_btc if pr["symbol"] == symbol), None)
            if trade_pair_for_asset:
                ask_in_btc: float = float(trade_pair_for_asset["askPrice"]) - 0.00000001
                asset_cost_in_btc = total_asset_balance * float(trade_pair_for_asset["lastPrice"])
            else:
                raise ValueError("trade_pair_for_asset is invalid")

            # If asset already bought early we don't buy it again
            asset_in_buy_lst = next((pr for pr in potential_buy_list if pr["symbol"] == symbol), None)
            min_allow_lots_size_in_btc = self._config.getfloat("Exchange", "min_lots_size_in_btc", fallback=0.0001)
            if asset_in_buy_lst and asset_cost_in_btc > min_allow_lots_size_in_btc:
                potential_buy_list.remove(asset_in_buy_lst)

            # Analise for new 'SELL' order
            asset_last_trade: dict = self._api_wr.my_trades_by_symbol(symbol)[0]
            min_profit_coef: float = self._config.getfloat("Exchange", "min_profit_coef", fallback=1.04)
            filter_price, filter_lot_size = self._get_filters_for_order_fast(exchange_symbols_info, symbol)
            quantity = round(total_asset_balance, alg.count_after_dot(float(filter_lot_size["stepSize"])))
            if not quantity or total_asset_balance < quantity:
                continue
            if ask_in_btc > (float(asset_last_trade["price"]) * min_profit_coef):
                if not self._api_wr.create_new_order(
                        symbol=symbol,
                        side=api.BnApiEnums.ORDER_SIDE_SELL,
                        order_type=api.BnApiEnums.ORDER_TYPE_LIMIT,
                        quantity=quantity,
                        price=ask_in_btc,
                        time_in_force=api.BnApiEnums.TIME_IN_FORCE_GTC
                ):
                    continue
            else:
                loss_time: int = self._config.getint("Exchange", "loss_time_sec", fallback=604800)  # default - 7 days
                if (tm.utc_timestamp() - int(asset_last_trade["time"])) > loss_time:
                    if not self._api_wr.create_new_order(
                            symbol=symbol,
                            side=api.BnApiEnums.ORDER_SIDE_SELL,
                            order_type=api.BnApiEnums.ORDER_TYPE_MARKET,
                            quantity=quantity
                    ):
                        continue

    def _generate_buy_orders_slow(self, potential_buy_list, exchange_symbols_info):
        # Loop for all potential_buy_list and create 'BUY' order
        trade_prs_lim = self._config.getint("Exchange", "trade_pairs_limit", fallback=10)
        potential_buy_list = potential_buy_list[0:trade_prs_lim]
        for buy_pair in potential_buy_list:
            symbol = buy_pair["symbol"]
            filter_price, filter_lot_size = self._get_filters_for_order_fast(exchange_symbols_info, symbol)
            # Calculate bid
            bid = float(buy_pair["bidPrice"]) + float(filter_price["tickSize"])
            if not bid or bid > float(filter_price["maxPrice"]) or bid < float(filter_price["minPrice"]):
                continue
            # Calculate quantity
            my_btc_asset_info = self._acc_btc_info()
            quantity = round(float(my_btc_asset_info["free"]) / bid,
                             alg.count_after_dot(float(filter_lot_size["stepSize"])))
            if not quantity:
                continue
            if not self._api_wr.create_new_order(
                    symbol=symbol,
                    side=api.BnApiEnums.ORDER_SIDE_BUY,
                    order_type=api.BnApiEnums.ORDER_TYPE_LIMIT,
                    quantity=quantity,
                    price=bid,
                    time_in_force=api.BnApiEnums.TIME_IN_FORCE_GTC
            ):
                continue

    def _acc_btc_info(self):
        pass

    @staticmethod
    def _get_filters_for_order_fast(exchange_symbols_info, symbol):
        symbol_info: dict = next((pr for pr in exchange_symbols_info if pr["symbol"] == symbol), None)
        if not symbol_info:
            raise ValueError("Bad symbol from potential_buy_list")
        price_filter: dict = symbol_info["filters"][0]
        lot_size_filter: dict = symbol_info["filters"][1]
        return price_filter, lot_size_filter


if __name__ == '__main__':
    from core import config as conf

    conf.init_global_config("/home/andrew/dev/crypto_bot/bot.cfg")
    api_wr_test = ApiWrapperTest(config=conf.global_core_conf)
    worker = BinanceWorker(config=conf.global_core_conf, api_wrapper=api_wr_test)
    worker.run_worker()

    # LOG.debug(worker.open_orders_by_side("SELL"), content_type="json")
    # LOG.debug(worker.sorted_trade_pairs_btc(), content_type="json")
    # LOG.debug(worker.acc_balance_for_assets(), content_type="json")
