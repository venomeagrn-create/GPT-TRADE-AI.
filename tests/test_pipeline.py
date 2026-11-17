import unittest

from bot.agents import MarketDataAgent, SignalAgent, RiskAgent, PaperExecutionAgent
from bot.orchestrator import run_pipeline


def rising(symbol, n):
    return [float(i) for i in range(1, n + 1)]


class PipelineTests(unittest.TestCase):
    def test_rising_prices_buy_and_update_cash(self):
        ctx = {"symbols": ["X"], "portfolio": {"cash": 1000.0, "positions": {}}}
        out = run_pipeline(
            [MarketDataAgent(rising), SignalAgent(), RiskAgent(), PaperExecutionAgent()], ctx
        )
        self.assertEqual(out["signals"][0].side, "buy")
        self.assertGreater(out["portfolio"]["positions"]["X"], 0)
        self.assertGreaterEqual(out["portfolio"]["cash"], 0)

    def test_short_history_holds(self):
        ctx = {"symbols": ["X"], "portfolio": {"cash": 1000.0, "positions": {}}}
        out = run_pipeline(
            [MarketDataAgent(lambda s, n: [1.0, 2.0]), SignalAgent(), RiskAgent(), PaperExecutionAgent()], ctx
        )
        self.assertEqual(out["signals"][0].side, "hold")
        self.assertEqual(out["orders"], [])

    def test_bad_windows_rejected(self):
        with self.assertRaises(ValueError):
            SignalAgent(fast=20, slow=5)


if __name__ == "__main__":
    unittest.main()
