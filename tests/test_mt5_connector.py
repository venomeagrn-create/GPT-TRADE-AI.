import unittest
from types import SimpleNamespace

from bot.mt5_connector import MT5Connector, DemoOnlyError


class FakeMT5:
    ACCOUNT_TRADE_MODE_DEMO = 0
    ACCOUNT_TRADE_MODE_REAL = 2
    TRADE_ACTION_DEAL = 1
    TRADE_RETCODE_DONE = 10009
    ORDER_TYPE_BUY = 0
    ORDER_TYPE_SELL = 1
    ORDER_TIME_GTC = 0
    ORDER_FILLING_IOC = 1
    TIMEFRAME_M1 = 1

    def __init__(self, trade_mode=0):
        self.trade_mode = trade_mode
        self.orders = []
        self.shut = False

    def initialize(self, **kwargs):
        self.kwargs = kwargs
        return True

    def shutdown(self):
        self.shut = True

    def last_error(self):
        return (0, "ok")

    def account_info(self):
        return SimpleNamespace(trade_mode=self.trade_mode)

    def copy_rates_from_pos(self, symbol, tf, start, n):
        return [{"close": float(i)} for i in range(n)]

    def symbol_info_tick(self, symbol):
        return SimpleNamespace(ask=101.0, bid=100.0)

    def order_send(self, request):
        self.orders.append(request)
        return SimpleNamespace(retcode=self.TRADE_RETCODE_DONE, order=7, price=request["price"], volume=request["volume"])


class MT5ConnectorTests(unittest.TestCase):
    def test_demo_account_connects(self):
        c = MT5Connector(FakeMT5(trade_mode=0))
        c.connect(login=1, password="x", server="s")
        self.assertEqual(len(c.closes("EURUSD", 3)), 3)

    def test_real_account_is_refused_and_shut_down(self):
        fake = FakeMT5(trade_mode=2)
        with self.assertRaises(DemoOnlyError):
            MT5Connector(fake).connect(login=1, password="x", server="s")
        self.assertTrue(fake.shut)

    def test_order_uses_ask_for_buy_and_bid_for_sell(self):
        fake = FakeMT5()
        c = MT5Connector(fake)
        c.connect(login=1, password="x", server="s")
        c.market_order("EURUSD", "buy", 0.01)
        c.market_order("EURUSD", "sell", 0.01)
        self.assertEqual(fake.orders[0]["price"], 101.0)
        self.assertEqual(fake.orders[1]["price"], 100.0)

    def test_volume_cap_enforced(self):
        c = MT5Connector(FakeMT5(), max_volume=0.1)
        with self.assertRaises(ValueError):
            c.market_order("EURUSD", "buy", 1.0)

    def test_bad_side_rejected(self):
        c = MT5Connector(FakeMT5())
        with self.assertRaises(ValueError):
            c.market_order("EURUSD", "hold", 0.01)


if __name__ == "__main__":
    unittest.main()
