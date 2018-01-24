from typing import List
from logger import logger
import json
from utils import utc_timestamp as tm
from utils import algorithm as alg
from services import exchange_base
from services import binance_rest_api as api

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
            price: float = None,
            time_in_force: str = None
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
        LOG.debug(res, content_type="json", max_symbols=1024)
        return res

    def create_new_order(
            self,
            symbol: str,
            side: str,
            order_type: str,
            quantity: float,
            price: float = None,
            time_in_force: str = None
    ) -> bool:
        res = self._api.create_new_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            timestamp=tm.utc_timestamp(),
            price=price,
            timeInForce=time_in_force,
            recvWindow=5000
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
        LOG.debug(res, content_type="json", max_symbols=1024)
        return res

    def sorted_trade_pairs_btc(self) -> List[dict]:
        def sort_func(key):
            ask = float(key["askPrice"])
            bid = float(key["bidPrice"])
            volume24h = float(key["quoteVolume"])
            change_percent = float(key["priceChangePercent"])
            rank = ((ask - bid) / bid) * volume24h * (1 + (change_percent / 100))
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
        LOG.debug(res, content_type="json", max_symbols=1024)
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
            price: float = None,
            time_in_force: str = None
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
        [
          {
            "symbol": "EOSBTC",
            "priceChange": "0.00009821",
            "priceChangePercent": "8.576",
            "weightedAvgPrice": "0.00118724",
            "prevClosePrice": "0.00114519",
            "lastPrice": "0.00124340",
            "lastQty": "1.00000000",
            "bidPrice": "0.00124214",
            "bidQty": "30.00000000",
            "askPrice": "0.00124340",
            "askQty": "3.00000000",
            "openPrice": "0.00114519",
            "highPrice": "0.00130000",
            "lowPrice": "0.00109300",
            "volume": "6393110.00000000",
            "quoteVolume": "7590.18247559",
            "openTime": 1516535006924,
            "closeTime": 1516621406924,
            "firstId": 4045016,
            "lastId": 4160476,
            "count": 115461
          },
          {
            "symbol": "SNTBTC",
            "priceChange": "-0.00000031",
            "priceChangePercent": "-1.205",
            "weightedAvgPrice": "0.00002508",
            "prevClosePrice": "0.00002575",
            "lastPrice": "0.00002541",
            "lastQty": "274.00000000",
            "bidPrice": "0.00002535",
            "bidQty": "2963.00000000",
            "askPrice": "0.00002541",
            "askQty": "1166.00000000",
            "openPrice": "0.00002572",
            "highPrice": "0.00002687",
            "lowPrice": "0.00002390",
            "volume": "11379364.00000000",
            "quoteVolume": "285.35789888",
            "openTime": 1516535005980,
            "closeTime": 1516621405980,
            "firstId": 1584774,
            "lastId": 1593206,
            "count": 8433
          },
          {
            "symbol": "ETCETH",
            "priceChange": "0.00032000",
            "priceChangePercent": "1.094",
            "weightedAvgPrice": "0.02934776",
            "prevClosePrice": "0.02924700",
            "lastPrice": "0.02956700",
            "lastQty": "20.35000000",
            "bidPrice": "0.02949500",
            "bidQty": "636.33000000",
            "askPrice": "0.02956700",
            "askQty": "35.36000000",
            "openPrice": "0.02924700",
            "highPrice": "0.03072300",
            "lowPrice": "0.02836000",
            "volume": "96461.83000000",
            "quoteVolume": "2830.93819821",
            "openTime": 1516535005296,
            "closeTime": 1516621405296,
            "firstId": 547099,
            "lastId": 553958,
            "count": 6860
          },
          {
            "symbol": "ETCBTC",
            "priceChange": "0.00005700",
            "priceChangePercent": "2.140",
            "weightedAvgPrice": "0.00268113",
            "prevClosePrice": "0.00266300",
            "lastPrice": "0.00272000",
            "lastQty": "17.92000000",
            "bidPrice": "0.00271800",
            "bidQty": "195.61000000",
            "askPrice": "0.00272200",
            "askQty": "653.61000000",
            "openPrice": "0.00266300",
            "highPrice": "0.00282000",
            "lowPrice": "0.00258000",
            "volume": "322692.60000000",
            "quoteVolume": "865.18123877",
            "openTime": 1516535006490,
            "closeTime": 1516621406490,
            "firstId": 2450000,
            "lastId": 2477595,
            "count": 27596
          },
          {
            "symbol": "MTHBTC",
            "priceChange": "-0.00000130",
            "priceChangePercent": "-5.242",
            "weightedAvgPrice": "0.00002428",
            "prevClosePrice": "0.00002481",
            "lastPrice": "0.00002350",
            "lastQty": "1036.00000000",
            "bidPrice": "0.00002351",
            "bidQty": "1031.00000000",
            "askPrice": "0.00002369",
            "askQty": "4403.00000000",
            "openPrice": "0.00002480",
            "highPrice": "0.00002580",
            "lowPrice": "0.00002300",
            "volume": "6081942.00000000",
            "quoteVolume": "147.65347992",
            "openTime": 1516535006835,
            "closeTime": 1516621406835,
            "firstId": 723841,
            "lastId": 729187,
            "count": 5347
          }         
        ]
        """

        def sort_func(key):
            ask = float(key["askPrice"])
            bid = float(key["bidPrice"])
            volume24h = float(key["quoteVolume"])
            change_percent = float(key["priceChangePercent"])
            rank = ((ask - bid) / bid) * volume24h * (1 + (change_percent / 100))
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
    def __init__(self, config, api_wrapper: ApiWrapperBase = None):
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
            acc_balance_assets_info: List[dict] = self._api_wr.acc_balance_for_assets()
            exchange_symbols_info: List[dict] = self._api_wr.exchange_symbols_info()
            initial_btc_info: dict = next((asset for asset in acc_balance_assets_info if asset["asset"] == "BTC"), None)
            if not all_trade_pairs_btc \
                    or not potential_buy_list \
                    or not acc_balance_assets_info \
                    or not exchange_symbols_info \
                    or not initial_btc_info:
                raise ValueError("Something went wrong and one from mandatory params are None")

            self._generate_sell_orders_slow(all_trade_pairs_btc, acc_balance_assets_info, potential_buy_list,
                                            exchange_symbols_info)
            self._generate_buy_orders_slow(potential_buy_list, exchange_symbols_info, initial_btc_info)

        except Exception as ex:
            LOG.error("Unknown exception has fired. Type:{} msg:{}".format(type(ex), ex.args[-1]))
        finally:
            LOG.info("BinanceWorker is shutting down!")
            self.release()

    def _generate_sell_orders_slow(self, all_trade_pairs_btc, acc_balance_assets_info, potential_buy_list,
                                   exchange_symbols_info):
        # Loop for all of my assets except 'BTC' and create 'SELL' orders
        for asset in acc_balance_assets_info:
            LOG.debug("Try to generate 'SELL' orders for asset:{}".format(asset["asset"]))
            if asset["asset"] == "BTC":
                continue
            asset["symbol"] = asset["asset"] + "BTC"
            asset["total_balance_fl"] = float(asset["free"]) + float(asset["locked"])
            filter_price, filter_lot_size, filter_notional = \
                self._get_filters_for_order_fast(exchange_symbols_info, asset["symbol"])
            # Find trade pair with 'BTC' on exchange in current moment for our asset
            trade_info_for_asset = next((pr for pr in all_trade_pairs_btc if pr["symbol"] == asset["symbol"]), None)
            if trade_info_for_asset and filter_price:
                asset["ask_in_btc_fl"] = float(trade_info_for_asset["askPrice"]) - float(filter_price["tickSize"]) # 0.00000001
                asset["total_cost_in_btc_fl"] = asset["total_balance_fl"] * float(trade_info_for_asset["lastPrice"])
            else:
                raise ValueError("trade_info_for_asset or filter_price is invalid")
            # If asset already bought early we don't buy it again
            asset_in_buy_lst = next((pr for pr in potential_buy_list if pr["symbol"] == asset["symbol"]), None)
            cfg_min_allow_lots_size_in_btc = self._config.getfloat("Exchange", "min_lots_size_in_btc", fallback=0.0001)
            if asset_in_buy_lst and asset["total_cost_in_btc_fl"] > cfg_min_allow_lots_size_in_btc:
                potential_buy_list.remove(asset_in_buy_lst)
            # Analise for new 'SELL' order
            cfg_min_profit_coef = self._config.getfloat("Exchange", "min_profit_coef", fallback=1.04)
            sell_qty = alg.reduce_to_step_size(float(asset["free"]), float(filter_lot_size["stepSize"]))
            LOG.debug("Dump variables after Qty calculating."
                      "\nQuantity: {}\nCfg min profit coef: {}\nTotal asset cost: {} 'BTC'\nAsk: {} 'BTC'"
                .format(
                    f"{sell_qty:.9f}",
                    f"{cfg_min_profit_coef:.9f}",
                    f"{asset['total_cost_in_btc_fl']:.9f}",
                    f"{asset['ask_in_btc_fl']:.9f}"
                )
            )
            if not sell_qty \
                    or float(asset["free"]) < sell_qty \
                    or float(filter_lot_size["minQty"]) > sell_qty \
                    or float(filter_lot_size["maxQty"]) < sell_qty:
                LOG.debug("Quantity too low for trading. Continue".format(sell_qty))
                continue
            asset_last_trade: dict = self._api_wr.my_trades_by_symbol(asset["symbol"])[0]
            if asset["ask_in_btc_fl"] > (float(asset_last_trade["price"]) * cfg_min_profit_coef):
                if self._api_wr.create_new_order(
                        symbol=asset["symbol"],
                        side=api.BnApiEnums.ORDER_SIDE_SELL,
                        order_type=api.BnApiEnums.ORDER_TYPE_LIMIT,
                        quantity=sell_qty,
                        price=asset["ask_in_btc_fl"],
                        time_in_force=api.BnApiEnums.TIME_IN_FORCE_GTC
                ):
                    LOG.debug("SELL order has successfully created")
                else:
                    LOG.debug("SELL order create has failed")
                    continue
            else:
                LOG.debug("Check loss time for symbol: {}".format(asset["symbol"]))
                cfg_loss_time_sec: int = self._config.getint("Exchange", "loss_time_sec",
                                                         fallback=604800)  # default - 7 days
                if (tm.utc_timestamp() - int(asset_last_trade["time"])) > cfg_loss_time_sec * 1000:
                    LOG.debug("Loss time has reached. Create order for symbol: {}".format(asset["symbol"]))
                    if self._api_wr.create_new_order(
                            symbol=asset["symbol"],
                            side=api.BnApiEnums.ORDER_SIDE_SELL,
                            order_type=api.BnApiEnums.ORDER_TYPE_MARKET,
                            quantity=sell_qty
                    ):
                        LOG.debug("SELL order by loss time has successfully created")
                    else:
                        LOG.debug("SELL order by loss time create has failed")
                        continue

    def _generate_buy_orders_slow(self, potential_buy_list, exchange_symbols_info, initial_btc_info):
        # Loop for all potential_buy_list and create 'BUY' order
        cfg_trade_prs_lim = self._config.getint("Exchange", "trade_pairs_limit", fallback=10)
        init_free_btc_balance = float(initial_btc_info["free"])
        for buy_pair in potential_buy_list[0:cfg_trade_prs_lim]:
            symbol = buy_pair["symbol"]
            LOG.debug("Try to generate 'BUY' orders for \nSymbol: {}\nInitial btc balance: {} 'BTC'\nTrade pair limit: {}"
                      .format(symbol, f"{init_free_btc_balance:.9f}", cfg_trade_prs_lim))
            filter_price, filter_lot_size, filter_notional = \
                self._get_filters_for_order_fast(exchange_symbols_info, symbol)
            available_btc_balance = init_free_btc_balance / cfg_trade_prs_lim
            min_btc_balance_size = float(filter_notional["minNotional"])
            if available_btc_balance < min_btc_balance_size:
                LOG.debug("Insufficient btc balance.\nAvailable balance: {0} 'BTC'\nMinimum balance: {1} 'BTC'"
                          "\nTry to increase available balance to initial btc balance."
                          .format(f"{available_btc_balance:.9f}", f"{min_btc_balance_size:.9f}"))
                if init_free_btc_balance > min_btc_balance_size:
                    available_btc_balance = init_free_btc_balance
                else:
                    LOG.debug("Insufficient btc balance. Stop generating.")
                    #return
            else:
                init_free_btc_balance = init_free_btc_balance - available_btc_balance
            # Calculate bid
            bid = float(buy_pair["bidPrice"]) + float(filter_price["tickSize"]) # +
            LOG.debug("Dump variables after bid calculating."
                      "\nbid: {}\nBid price: {} 'BTC'\nTick size: {}"
                .format(
                    f"{bid:.9f}",
                    buy_pair['bidPrice'],
                    filter_price['tickSize']
                )
            )
            if not bid or bid > float(filter_price["maxPrice"]) or bid < float(filter_price["minPrice"]):
                continue
            # Calculate quantity
            buy_qty = alg.reduce_to_step_size(available_btc_balance / bid, float(filter_lot_size["stepSize"]))
            LOG.debug("Dump variables after buy Qty calculating."
                      "\nQuantity: {}\nAvailable balance: {} 'BTC'\nStep size: {}"
                .format(
                    f"{buy_qty:.9f}",
                    f"{available_btc_balance:.9f}",
                    filter_lot_size['stepSize']
                )
            )
            if not buy_qty:
                LOG.debug("Buy quantity isn't valid. Continue.")
                continue
            if self._api_wr.create_new_order(
                    symbol=symbol,
                    side=api.BnApiEnums.ORDER_SIDE_BUY,
                    order_type=api.BnApiEnums.ORDER_TYPE_LIMIT,
                    quantity=buy_qty,
                    price=bid,
                    time_in_force=api.BnApiEnums.TIME_IN_FORCE_GTC
            ):
                LOG.debug("BUY order has successfully created")
            else:
                LOG.debug("BUY order create has failed")

    def _acc_btc_info_slow(self) -> dict:
        # query every time in loop because lod value is not represented
        acc_balance_for_assets = self._api_wr.acc_balance_for_assets()
        for asset in acc_balance_for_assets:
            if asset["asset"] == "BTC":
                return asset
        raise ValueError("Don't have BTC info in my account assets list")

    @staticmethod
    def _get_filters_for_order_fast(exchange_symbols_info, symbol):
        symbol_info: dict = next((pr for pr in exchange_symbols_info if pr["symbol"] == symbol), None)
        if not symbol_info:
            raise ValueError("Bad symbol from potential_buy_list")
        price_filter: dict = symbol_info["filters"][0]
        lot_size_filter: dict = symbol_info["filters"][1]
        min_notional_filter: dict = symbol_info["filters"][2]
        return price_filter, lot_size_filter, min_notional_filter


if __name__ == '__main__':
    from core import config as conf

    conf.init_global_config("/home/andrew/dev/crypto_bot/bot.cfg")
    api_wr_test = ApiWrapperTest(config=conf.global_core_conf)
    LOG.debug(api_wr_test.sorted_trade_pairs_btc(), content_type="json")

    # worker = BinanceWorker(config=conf.global_core_conf, api_wrapper=api_wr_test)
    # worker.run_worker()

    # LOG.debug(worker.open_orders_by_side("SELL"), content_type="json")
    # LOG.debug(worker.sorted_trade_pairs_btc(), content_type="json")
    # LOG.debug(worker.acc_balance_for_assets(), content_type="json")
