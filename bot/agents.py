"""Agents that make up the pipeline.

Each agent takes a shared context dict, reads what it needs, and returns
a new dict with its own results added. Nothing here places real orders.
"""
from dataclasses import dataclass, field
from statistics import mean
from typing import Callable, Iterable


@dataclass
class Signal:
    symbol: str
    side: str  # "buy", "sell" or "hold"
    reason: str


@dataclass
class Order:
    symbol: str
    side: str
    qty: float
    price: float


class MarketDataAgent:
    """Fetches recent closing prices for each symbol from an injected source."""

    def __init__(self, source: Callable[[str, int], list[float]], lookback: int = 30):
        self.source = source
        self.lookback = lookback

    def run(self, ctx: dict) -> dict:
        prices = {s: self.source(s, self.lookback) for s in ctx["symbols"]}
        return {**ctx, "prices": prices}


class SignalAgent:
    """Simple moving-average crossover: a placeholder strategy to be replaced."""

    def __init__(self, fast: int = 5, slow: int = 20):
        if fast >= slow:
            raise ValueError("fast window must be shorter than slow window")
        self.fast, self.slow = fast, slow

    def run(self, ctx: dict) -> dict:
        signals: list[Signal] = []
        for symbol, closes in ctx["prices"].items():
            if len(closes) < self.slow:
                signals.append(Signal(symbol, "hold", "not enough data"))
                continue
            fast_ma = mean(closes[-self.fast:])
            slow_ma = mean(closes[-self.slow:])
            if fast_ma > slow_ma:
                signals.append(Signal(symbol, "buy", f"fast MA {fast_ma:.2f} > slow MA {slow_ma:.2f}"))
            elif fast_ma < slow_ma:
                signals.append(Signal(symbol, "sell", f"fast MA {fast_ma:.2f} < slow MA {slow_ma:.2f}"))
            else:
                signals.append(Signal(symbol, "hold", "moving averages equal"))
        return {**ctx, "signals": signals}


class RiskAgent:
    """Turns signals into orders, respecting position size and cash limits."""

    def __init__(self, max_position_value: float = 1000.0, max_orders: int = 5):
        self.max_position_value = max_position_value
        self.max_orders = max_orders

    def run(self, ctx: dict) -> dict:
        orders: list[Order] = []
        cash = ctx["portfolio"]["cash"]
        for sig in ctx["signals"]:
            if sig.side == "hold" or len(orders) >= self.max_orders:
                continue
            price = ctx["prices"][sig.symbol][-1]
            if sig.side == "buy":
                budget = min(self.max_position_value, cash)
                qty = int(budget // price)
                if qty > 0:
                    orders.append(Order(sig.symbol, "buy", qty, price))
                    cash -= qty * price
            elif sig.side == "sell" and ctx["portfolio"]["positions"].get(sig.symbol, 0) > 0:
                qty = ctx["portfolio"]["positions"][sig.symbol]
                orders.append(Order(sig.symbol, "sell", qty, price))
        return {**ctx, "orders": orders}


class PaperExecutionAgent:
    """Applies orders to a simulated portfolio. No real broker is connected."""

    def run(self, ctx: dict) -> dict:
        portfolio = ctx["portfolio"]
        for order in ctx["orders"]:
            cost = order.qty * order.price
            if order.side == "buy":
                portfolio["cash"] -= cost
                portfolio["positions"][order.symbol] = portfolio["positions"].get(order.symbol, 0) + order.qty
            else:
                portfolio["cash"] += cost
                portfolio["positions"][order.symbol] = 0
        return {**ctx, "portfolio": portfolio}
