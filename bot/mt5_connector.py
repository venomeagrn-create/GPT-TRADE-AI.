"""MetaTrader 5 connector, DEMO accounts only.

Safety rules enforced here:
- Refuses to run unless the logged-in account is a demo account.
- Caps the volume of any single order.
- Reads credentials from environment variables, never from source code.

Requires the `MetaTrader5` package and the MT5 terminal (Windows).
"""
import os
from typing import Any, Optional

MAX_VOLUME = 0.10  # lots per order


class DemoOnlyError(RuntimeError):
    pass


class MT5Connector:
    def __init__(self, mt5_module: Any = None, max_volume: float = MAX_VOLUME):
        if mt5_module is None:
            import MetaTrader5 as mt5_module  # imported lazily so tests run without MT5
        self.mt5 = mt5_module
        self.max_volume = max_volume

    def connect(self, login: Optional[int] = None, password: Optional[str] = None,
                server: Optional[str] = None) -> None:
        login = login or int(os.environ["MT5_LOGIN"])
        password = password or os.environ["MT5_PASSWORD"]
        server = server or os.environ["MT5_SERVER"]
        if not self.mt5.initialize(login=login, password=password, server=server):
            raise ConnectionError(f"MT5 initialize failed: {self.mt5.last_error()}")
        info = self.mt5.account_info()
        if info is None or info.trade_mode != self.mt5.ACCOUNT_TRADE_MODE_DEMO:
            self.mt5.shutdown()
            raise DemoOnlyError("Refusing to trade: this is not a demo account.")

    def close(self) -> None:
        self.mt5.shutdown()

    def closes(self, symbol: str, n: int) -> list[float]:
        rates = self.mt5.copy_rates_from_pos(symbol, self.mt5.TIMEFRAME_M1, 0, n)
        if rates is None:
            raise RuntimeError(f"No price data for {symbol}: {self.mt5.last_error()}")
        return [float(r["close"]) for r in rates]

    def market_order(self, symbol: str, side: str, volume: float, deviation: int = 20) -> dict:
        if side not in ("buy", "sell"):
            raise ValueError("side must be 'buy' or 'sell'")
        if not 0 < volume <= self.max_volume:
            raise ValueError(f"volume must be between 0 and {self.max_volume}")
        tick = self.mt5.symbol_info_tick(symbol)
        if tick is None:
            raise RuntimeError(f"No tick for {symbol}")
        is_buy = side == "buy"
        request = {
            "action": self.mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": self.mt5.ORDER_TYPE_BUY if is_buy else self.mt5.ORDER_TYPE_SELL,
            "price": tick.ask if is_buy else tick.bid,
            "deviation": deviation,
            "magic": 20260101,
            "comment": "bot-demo",
            "type_time": self.mt5.ORDER_TIME_GTC,
            "type_filling": self.mt5.ORDER_FILLING_IOC,
        }
        result = self.mt5.order_send(request)
        if result is None or result.retcode != self.mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(f"Order rejected: {result}")
        return {"ticket": result.order, "price": result.price, "volume": result.volume}
